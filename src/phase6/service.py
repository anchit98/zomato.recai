import json
import time
import logging
import uuid
import threading
from pathlib import Path
import pandas as pd
from typing import Any, List, Optional

from src.phase2.preferences import validate_and_normalize_preferences
from src.phase3.candidates import generate_candidates
from src.phase4.ranking import generate_ranked_recommendations
from src.phase5.history import HistoryService
from src.phase8.monitoring import TelemetryService

ROOT = Path(__file__).resolve().parents[2]
CLEANED_DATA_PATH = ROOT / "artifacts" / "phase1" / "zomato_cleaned.csv"

class RecommendationService:
    _df_cache: Optional[pd.DataFrame] = None
    _cache_lock = threading.Lock()

    def __init__(self):
        self.history_service = HistoryService()
        self.telemetry = TelemetryService()
        self._llm_semaphore = threading.Semaphore(3)  # Cap parallel LLM calls to 3 (EC-46)
        self._load_data_into_cache()

    def _load_data_into_cache(self):
        """Loads the dataset into memory once (EC-47, EC-49)"""
        with self._cache_lock:
            if RecommendationService._df_cache is None:
                try:
                    if CLEANED_DATA_PATH.exists():
                        print(f"[CACHE] Loading {CLEANED_DATA_PATH.name} into memory...")
                        RecommendationService._df_cache = pd.read_csv(CLEANED_DATA_PATH)
                        print("[CACHE] Dataset cached successfully.")
                except Exception as e:
                    print(f"[CACHE] Error caching dataset: {e}")

    def get_recommendations(self, payload: dict[str, Any], session_id: str, top_k: int = 5) -> dict[str, Any]:
        start_time = time.perf_counter()
        request_id = str(uuid.uuid4())[:8] # UUID for isolation (EC-45)
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

            # Create a unique temp folder for this request to ensure isolation (EC-45)
            temp_dir = ROOT / "artifacts" / "temp" / request_id
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            pref_path = temp_dir / "preferences.json"
            cand_path = temp_dir / "candidates.json"
            
            pref_data = {
                "valid": True,
                "normalized_preferences": norm_result.normalized_preferences.to_dict() if norm_result.normalized_preferences else None,
                "constraint_policy": norm_result.constraint_policy,
                "warnings": norm_result.warnings
            }
            pref_path.write_text(json.dumps(pref_data), encoding="utf-8")

            # 2. Phase 3: Candidate Retrieval
            cand_result = generate_candidates(
                cleaned_data_path=CLEANED_DATA_PATH,
                preference_object_path=pref_path,
                top_n=20
            )
            cand_path.write_text(cand_result.to_json(), encoding="utf-8")

            # 3. Phase 4: LLM Ranking (Bounded by Semaphore to prevent 429 storms - EC-46)
            print(f"[CONCURRENCY] Request {request_id} waiting for LLM slot...")
            with self._llm_semaphore:
                print(f"[CONCURRENCY] Request {request_id} entering LLM stage.")
                rank_result = generate_ranked_recommendations(
                    candidates_json_path=cand_path,
                    preference_object_path=pref_path,
                    top_k=top_k
                )
            
            model = rank_result.model
            usage = rank_result.usage

            # Cleanup request-specific temp directory (EC-45)
            try:
                for f in temp_dir.glob("*"): f.unlink()
                temp_dir.rmdir()
            except:
                pass

            # 4. Process results
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
            
            # NOTE: History saving should be handled as a BackgroundTask in main.py
            # but we keep the logic accessible here.
            self.last_flow_data = {
                "preferences": pref_data["normalized_preferences"],
                "recommendations": recs_for_storage,
                "session_id": session_id
            }

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
                    "usage": usage,
                    "request_id": request_id
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

    def save_history_background(self, data: dict[str, Any]):
        """Helper for non-blocking history writes (EC-51)"""
        try:
            self.history_service.save_recommendation_flow(
                preferences=data["preferences"],
                recommendations=data["recommendations"],
                session_id=data["session_id"]
            )
        except Exception as e:
            print(f"[BACKGROUND] Failed to save history: {e}")

    def save_feedback(self, feedback_data: dict[str, Any]):
        print(f"[FEEDBACK] Session {feedback_data['session_id']} | Restaurant: {feedback_data['restaurant_name']} | Positive: {feedback_data['is_positive']}")
        logging.info(f"FEEDBACK | {json.dumps(feedback_data)}")

    def get_unique_locations(self) -> List[str]:
        """Thread-safe location fetching from memory cache (EC-47)"""
        try:
            if RecommendationService._df_cache is None:
                self._load_data_into_cache()
            
            df = RecommendationService._df_cache
            if df is None or "location" not in df.columns:
                return []
                
            locations = df["location"].dropna().unique().tolist()
            return sorted([str(loc) for loc in locations])
        except Exception as e:
            print(f"Error fetching locations: {e}")
            return []
