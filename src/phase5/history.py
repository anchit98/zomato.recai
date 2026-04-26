from __future__ import annotations

import os
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Any, Optional
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

@dataclass
class UserHistoryEntry:
    location: str
    budget: Optional[str]
    min_rating: Optional[float]
    cuisine: Optional[str]
    session_id: str
    raw_preferences: dict[str, Any]
    id: Optional[str] = None
    created_at: Optional[str] = None

@dataclass
class RecommendationEntry:
    restaurant_name: str
    rating: float
    estimated_cost: float
    ai_explanation: str
    rank: int
    history_id: Optional[str] = None
    id: Optional[str] = None

class HistoryService:
    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_ANON_KEY")
        if not url or not key:
            # We don't raise here yet to allow the script to load, 
            # but methods will fail if keys are missing.
            self.client = None
        else:
            self.client: Client = create_client(url, key)

    def _ensure_client(self):
        if not self.client:
            raise ValueError("Supabase credentials missing in .env (SUPABASE_URL, SUPABASE_ANON_KEY)")

    def save_recommendation_flow(
        self, 
        preferences: dict[str, Any], 
        recommendations: list[dict[str, Any]], 
        session_id: str
    ) -> str:
        """
        Saves the user preferences and the resulting AI recommendations to Supabase.
        Returns the history_id of the saved record.
        """
        self._ensure_client()

        # 1. Save to user_history
        history_data = {
            "location": preferences.get("location"),
            "budget": preferences.get("budget"),
            "min_rating": preferences.get("minimum_rating"),
            "cuisine": preferences.get("cuisine"),
            "session_id": session_id,
            "raw_preferences": preferences
        }
        
        history_response = self.client.table("user_history").insert(history_data).execute()
        if not history_response.data:
            raise Exception("Failed to save user history to Supabase")
        
        history_id = history_response.data[0]["id"]

        # 2. Save recommendations linked to this history_id
        rec_data = []
        for rec in recommendations:
            rec_data.append({
                "history_id": history_id,
                "restaurant_name": rec.get("restaurant_name"),
                "rating": rec.get("rating"),
                "estimated_cost": rec.get("estimated_cost_for_two"),
                "ai_explanation": rec.get("explanation"),
                "rank": rec.get("rank")
            })
        
        if rec_data:
            rec_response = self.client.table("recommendations").insert(rec_data).execute()
            if not rec_response.data:
                # Log warning but history was saved
                print(f"Warning: Failed to save details for history_id {history_id}")

        return history_id

    def get_session_history(self, session_id: str) -> list[dict[str, Any]]:
        """
        Retrieves all past searches and their recommendations for a given session.
        """
        self._ensure_client()

        # Join user_history and recommendations
        # Note: In a real production app, we might do separate calls or a view
        response = self.client.table("user_history")\
            .select("*, recommendations(*)")\
            .eq("session_id", session_id)\
            .order("created_at", desc=True)\
            .execute()
        
        return response.data

    def get_recent_global_history(self, limit: int = 10) -> list[dict[str, Any]]:
        """
        Retrieves recent searches across all users for a 'Trending' view.
        """
        self._ensure_client()
        response = self.client.table("user_history")\
            .select("*, recommendations(*)")\
            .order("created_at", desc=True)\
            .limit(limit)\
            .execute()
        return response.data
