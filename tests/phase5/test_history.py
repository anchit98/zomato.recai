import unittest
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.phase5.history import HistoryService

class TestPhase5History(unittest.TestCase):
    def setUp(self):
        self.service = HistoryService()
        self.session_id = "test-session-unittest"

    def test_save_and_retrieve(self):
        # Only run if Supabase keys are present
        if not self.service.client:
            self.skipTest("Supabase keys missing in .env")

        dummy_prefs = {"location": "unittest-area"}
        dummy_recs = [{"restaurant_name": "Test Place", "rating": 5.0, "rank": 1}]
        
        try:
            history_id = self.service.save_recommendation_flow(dummy_prefs, dummy_recs, self.session_id)
            self.assertIsNotNone(history_id)
            
            history = self.service.get_session_history(self.session_id)
            self.assertGreater(len(history), 0)
            self.assertEqual(history[0]["location"], "unittest-area")
        except Exception as e:
            self.fail(f"Supabase persistence failed: {e}")

if __name__ == "__main__":
    unittest.main()
