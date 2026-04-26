import unittest
from pathlib import Path
import pandas as pd

class TestPhase1Data(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parents[2]
        self.cleaned_csv = self.root / "artifacts" / "phase1" / "zomato_cleaned.csv"
        self.cleaned_json = self.root / "artifacts" / "phase1" / "zomato_cleaned.json"

    def test_artifacts_exist(self):
        self.assertTrue(self.cleaned_csv.exists(), "Cleaned CSV not found")
        self.assertTrue(self.cleaned_json.exists(), "Cleaned JSON not found")

    def test_data_integrity(self):
        df = pd.read_csv(self.cleaned_csv)
        self.assertFalse(df.empty, "Cleaned CSV is empty")
        self.assertIn("restaurant_name", df.columns)
        self.assertIn("rating", df.columns)
        self.assertIn("estimated_cost_for_two", df.columns)

if __name__ == "__main__":
    unittest.main()
