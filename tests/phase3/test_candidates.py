import unittest
import sys
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.phase3.candidates import generate_candidates

class TestPhase3Candidates(unittest.TestCase):
    def setUp(self):
        self.cleaned_data = ROOT / "artifacts" / "phase1" / "zomato_cleaned.csv"
        # Create a temp preference file
        self.temp_pref = ROOT / "tests" / "phase3" / "temp_pref.json"
        pref_data = {
            "valid": True,
            "normalized_preferences": {
                "location": "indiranagar",
                "budget": "medium",
                "minimum_rating": 4.0,
                "cuisine": "italian"
            }
        }
        self.temp_pref.write_text(json.dumps(pref_data))

    def tearDown(self):
        if self.temp_pref.exists():
            self.temp_pref.unlink()

    def test_candidate_generation(self):
        result = generate_candidates(
            cleaned_data_path=self.cleaned_data,
            preference_object_path=self.temp_pref,
            top_n=5
        )
        self.assertGreaterEqual(result.candidates_returned, 0)
        if result.candidates_returned > 0:
            first = result.candidates[0]
            self.assertIn("restaurant_name", first)
            self.assertIn("rating", first)

if __name__ == "__main__":
    unittest.main()
