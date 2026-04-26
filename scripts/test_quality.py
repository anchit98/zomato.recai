import sys
import os
import json
from pathlib import Path
import time

# Setup paths to import project modules
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import src.bootstrap

from src.phase6.service import RecommendationService

def run_benchmark():
    service = RecommendationService()
    
    test_queries = [
        {"location": "Indiranagar", "cuisine": "Cafe", "budget": 800, "label": "Budget Cafe"},
        {"location": "Koramangala", "cuisine": "Fine Dining", "budget": 3000, "label": "Luxury Dining"},
        {"location": "Whitefield", "cuisine": "Pizza", "budget": 1200, "label": "Mid-range Pizza"},
        {"location": "Jayanagar", "cuisine": "South Indian", "budget": 500, "label": "Quick South Indian"}
    ]
    
    print("Starting Phase 8 Quality Benchmark...")
    print("-" * 50)
    
    results = []
    
    for i, query in enumerate(test_queries):
        print(f"[{i+1}/{len(test_queries)}] Testing: {query['label']} in {query['location']}...")
        
        start = time.perf_counter()
        try:
            res = service.get_recommendations(
                payload={
                    "location": query["location"],
                    "cuisine": query["cuisine"],
                    "budget": query["budget"]
                },
                session_id=f"benchmark-{int(time.time())}",
                top_k=3
            )
            latency = (time.perf_counter() - start) * 1000
            
            success = res.get("status") == "ok"
            recs_count = len(res.get("recommendations", []))
            
            print(f"   Success! Latency: {latency:.2f}ms | Items: {recs_count}")
            
            results.append({
                "query": query["label"],
                "success": success,
                "latency_ms": latency,
                "count": recs_count,
                "model": res.get("meta", {}).get("model", "unknown")
            })
            
        except Exception as e:
            print(f"   Failed: {e}")
            results.append({
                "query": query["label"],
                "success": False,
                "error": str(e)
            })
            
    print("-" * 50)
    avg_latency = sum(r.get("latency_ms", 0) for r in results if r["success"]) / len([r for r in results if r["success"]])
    print(f"Benchmark Complete!")
    print(f"Average Latency: {avg_latency:.2f}ms")
    print(f"Success Rate: {len([r for r in results if r['success']]) / len(results) * 100:.1f}%")

if __name__ == "__main__":
    run_benchmark()
