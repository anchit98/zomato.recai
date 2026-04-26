import unittest
import sys
from pathlib import Path
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.phase6.main import app

class TestPhase6API(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_health_check(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "healthy")

    def test_recommend_endpoint(self):
        # We test the endpoint with a mock to avoid full pipeline latency if possible,
        # but here we'll do a real small request.
        payload = {
            "location": "Indiranagar",
            "top_k": 1,
            "session_id": "api-test"
        }
        response = self.client.post("/api/v1/recommend", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn("recommendations", response.json())

if __name__ == "__main__":
    unittest.main()
