import urllib.request
import urllib.error
import json

data = {
    "location": "Bellandur",
    "budget": 1500,
    "minimum_rating": 4.0,
    "cuisine": "Mexican",
    "additional_preferences": "",
    "session_id": "test",
    "top_k": 5
}

req = urllib.request.Request(
    'http://localhost:8000/api/v1/recommend',
    data=json.dumps(data).encode('utf-8'),
    headers={'Content-Type': 'application/json'}
)

try:
    with urllib.request.urlopen(req) as response:
        print(response.read().decode())
except urllib.error.HTTPError as e:
    print(f"HTTP Error: {e.code}")
    print(e.read().decode())
except Exception as e:
    print(f"Error: {e}")
