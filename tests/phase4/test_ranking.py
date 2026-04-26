import unittest
import sys
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.phase4.ranking import generate_ranked_recommendations

class TestPhase4Ranking(unittest.TestCase):
    def setUp(self):
        self.pref_path = ROOT / "tests" / "phase4" / "temp_pref.json"
        self.cand_path = ROOT / "tests" / "phase4" / "temp_cand.json"
        
        pref_data = {
            "valid": True,
            "normalized_preferences": {"location": "bellandur", "minimum_rating": 4.0}
        }
        cand_data = {
            "candidates": [
                {
                    "restaurant_name": "Test Rest 1",
                    "location": "Bellandur",
                    "cuisines": "Cafe",
                    "estimated_cost_for_two": 500,
                    "rating": 4.5,
                    "rank": 1
                }
            ]
        }
        self.pref_path.write_text(json.dumps(pref_data))
        self.cand_path.write_text(json.dumps(cand_data))

    def tearDown(self):
        for p in [self.pref_path, self.cand_path]:
            if p.exists(): p.unlink()

    def test_ranking_logic(self):
        # This will call the actual LLM if GROQ_API_KEY is present
        try:
            result = generate_ranked_recommendations(
                candidates_json_path=self.cand_path,
                preference_object_path=self.pref_path,
                top_k=1
            )
            if not result.used_llm:
                print(f"\nLLM Error in Metadata: {result.meta.get('llm_error')}")
                print(f"Warnings: {result.warnings}")
            self.assertTrue(result.used_llm)
            self.assertEqual(len(result.recommendations), 1)
        except Exception as e:
            self.fail(f"LLM Ranking failed: {e}")

if __name__ == "__main__":
    unittest.main()
