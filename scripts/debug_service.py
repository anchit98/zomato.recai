import sys
import os
import traceback

# Setup paths
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import src.bootstrap

from src.phase6.service import RecommendationService

try:
    service = RecommendationService()
    payload = {
        "location": "Bellandur",
        "budget": 1500,
        "minimum_rating": 4.0,
        "cuisine": "Mexican",
        "additional_preferences": ""
    }
    result = service.get_recommendations(payload, "test", 5)
    print("Success:")
    print(result)
except Exception as e:
    print("Error occurred:")
    traceback.print_exc()
