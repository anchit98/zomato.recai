from __future__ import annotations
import json
import time
import logging
from pathlib import Path
import pandas as pd
from typing import Any, List

from src.phase2.preferences import validate_and_normalize_preferences
from src.phase3.candidates import generate_candidates
from src.phase4.ranking import generate_ranked_recommendations
from src.phase5.history import HistoryService
from src.phase8.monitoring import TelemetryService

ROOT = Path(__file__).resolve().parents[2]
CLEANED_DATA_PATH = ROOT / "artifacts" / "phase1" / "zomato_cleaned.csv"

class RecommendationService:
    def __init__(self):
        self.history_service = HistoryService()
        self.telemetry = TelemetryService()

    def get_recommendations(self, payload: dict[str, Any], session_id: str, top_k: int = 5) -> dict[str, Any]:
        start_time = time.perf_counter()
        success = False
        model = "unknown"
        usage = None
        error_msg = None
        
        try:
            # 1. Phase 2: Normalization
            norm_result = validate_and_normalize_preferences(payload)
            if not norm_result.valid:
                errors = [e.message for e in norm_result.errors]
                return {"status": "error", "message": "Invalid preferences", "errors": errors}

            # Create a temporary JSON file for the preference object
            temp_dir = ROOT / "artifacts" / "temp"
            temp_dir.mkdir(parents=True, exist_ok=True)
            pref_path = temp_dir / f"pref_{session_id}.json"
            
            pref_data = {
                "valid": True,
                "normalized_preferences": norm_result.normalized_preferences.to_dict() if norm_result.normalized_preferences else None,
                "constraint_policy": norm_result.constraint_policy,
                "warnings": norm_result.warnings
            }
            pref_path.write_text(json.dumps(pref_data), encoding="utf-8")

            # 2. Phase 3: Candidate Retrieval
            cand_path = temp_dir / f"cand_{session_id}.json"
            cand_result = generate_candidates(
                cleaned_data_path=CLEANED_DATA_PATH,
                preference_object_path=pref_path,
                top_n=20
            )
            cand_path.write_text(cand_result.to_json(), encoding="utf-8")

            # 3. Phase 4: LLM Ranking
            rank_result = generate_ranked_recommendations(
                candidates_json_path=cand_path,
                preference_object_path=pref_path,
                top_k=top_k
            )
            
            model = rank_result.model
            usage = rank_result.usage

            # Cleanup temp files
            try:
                pref_path.unlink()
                cand_path.unlink()
            except:
                pass

            # 4. Phase 5: Save to History
            recs_for_storage = []
            for r in rank_result.recommendations:
                recs_for_storage.append({
                    "restaurant_name": r["restaurant_name"],
                    "location": r["location"],
                    "cuisines": r["cuisines"],
                    "rating": r["rating"],
                    "explanation": r["explanation"],
                    "estimated_cost_for_two": r["estimated_cost_for_two"],
                    "rank": r["rank"]
                })
            
            try:
                self.history_service.save_recommendation_flow(
                    preferences=pref_data["normalized_preferences"],
                    recommendations=recs_for_storage,
                    session_id=session_id
                )
            except Exception as e:
                print(f"Warning: Failed to save history: {e}")

            success = True
            return {
                "status": "ok",
                "session_id": session_id,
                "recommendations": recs_for_storage,
                "warnings": norm_result.warnings + rank_result.warnings,
                "meta": {
                    "model": rank_result.model,
                    "used_llm": rank_result.used_llm,
                    "phase3_relaxed": cand_result.relaxed_constraints,
                    "usage": usage
                }
            }
        except Exception as e:
            error_msg = str(e)
            raise e
        finally:
            latency = (time.perf_counter() - start_time) * 1000
            self.telemetry.log_recommendation_event(
                session_id=session_id,
                latency_ms=latency,
                success=success,
                model=model,
                token_usage=usage,
                error=error_msg
            )

    def get_history(self, session_id: str) -> list[dict[str, Any]]:
        return self.history_service.get_session_history(session_id)

    def get_recent_searches(self, limit: int = 10) -> list[dict[str, Any]]:
        return self.history_service.get_recent_global_history(limit)

    def save_feedback(self, feedback_data: dict[str, Any]):
        # In a real production app, this would go to a 'feedback' table in Supabase
        # For Phase 8, we'll log it to our telemetry system for analysis
        print(f"[FEEDBACK] Session {feedback_data['session_id']} | Restaurant: {feedback_data['restaurant_name']} | Positive: {feedback_data['is_positive']}")
        logging.info(f"FEEDBACK | {json.dumps(feedback_data)}")

    def get_unique_locations(self) -> List[str]:
        try:
            if not CLEANED_DATA_PATH.exists():
                return []
            df = pd.read_csv(CLEANED_DATA_PATH)
            if "location" not in df.columns:
                return []
            # Get unique locations, drop NaNs, and sort alphabetically
            locations = df["location"].dropna().unique().tolist()
            return sorted([str(loc) for loc in locations])
        except Exception as e:
            print(f"Error fetching locations: {e}")
            return []
