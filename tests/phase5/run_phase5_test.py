from __future__ import annotations

import sys
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.phase5.history import HistoryService

def test_supabase_persistence():
    service = HistoryService()
    
    print("Testing Phase 5: Supabase Persistence")
    
    # Mock data based on Phase 4 outputs
    dummy_preferences = {
        "location": "Indiranagar",
        "budget": "medium",
        "minimum_rating": 4.0,
        "cuisine": "Italian"
    }
    
    dummy_recommendations = [
        {
            "restaurant_name": "Milano Ice Cream",
            "rating": 4.9,
            "explanation": "Excellent ratings and great vibe.",
            "estimated_cost_for_two": 400.0,
            "rank": 1
        },
        {
            "restaurant_name": "Chianti",
            "rating": 4.5,
            "explanation": "Authentic Italian experience.",
            "estimated_cost_for_two": 1500.0,
            "rank": 2
        }
    ]
    
    session_id = "test-session-123"

    try:
        print(f"Saving flow for session: {session_id}...")
        history_id = service.save_recommendation_flow(
            dummy_preferences, 
            dummy_recommendations, 
            session_id
        )
        print(f"Success! History ID: {history_id}")
        
        print("\nRetrieving history for session...")
        history = service.get_session_history(session_id)
        print(f"Number of records retrieved: {len(history)}")
        print(json.dumps(history, indent=2))
        
    except Exception as e:
        print("\n--- ERROR ENCOUNTERED ---")
        import traceback
        traceback.print_exc()
        print("\n-------------------------")
        print("\nNOTE: Ensure you have:")
        print("1. Added SUPABASE_URL and SUPABASE_ANON_KEY to your .env file.")
        print("2. Created the 'user_history' and 'recommendations' tables in your Supabase project using the SQL shared earlier.")

if __name__ == "__main__":
    test_supabase_persistence()
