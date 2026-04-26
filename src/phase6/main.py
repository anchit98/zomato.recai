from __future__ import annotations

import os
import sys
import traceback

# Force unbuffered output so Render can see all print statements and errors
os.environ["PYTHONUNBUFFERED"] = "1"
sys.stdout.reconfigure(line_buffering=True) if hasattr(sys.stdout, 'reconfigure') else None
sys.stderr.reconfigure(line_buffering=True) if hasattr(sys.stderr, 'reconfigure') else None

print("[STARTUP] Starting ZOMATO REC.AI backend...")

try:
    import uvicorn
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from dotenv import load_dotenv
    print("[STARTUP] Core imports OK")
except Exception as e:
    print(f"[FATAL] Failed to import core packages: {e}")
    traceback.print_exc()
    sys.exit(1)

# Load env vars
load_dotenv()

# Validate required environment variables
REQUIRED_VARS = ["GROQ_API_KEY", "SUPABASE_URL", "SUPABASE_ANON_KEY"]
missing_vars = [var for var in REQUIRED_VARS if not os.getenv(var)]
if missing_vars:
    print(f"[WARNING] Missing environment variables: {', '.join(missing_vars)}")
else:
    print("[STARTUP] All environment variables present")

try:
    from src.phase6.models import RecommendationRequest, RecommendationResponse, HistoryItem, FeedbackRequest
    print("[STARTUP] Models import OK")
except Exception as e:
    print(f"[FATAL] Failed to import models: {e}")
    traceback.print_exc()
    sys.exit(1)

try:
    from src.phase6.service import RecommendationService
    print("[STARTUP] Service import OK")
except Exception as e:
    print(f"[FATAL] Failed to import service: {e}")
    traceback.print_exc()
    sys.exit(1)

app = FastAPI(
    title="ZOMATO REC.AI",
    description="AI-powered restaurant scout for Zomato data",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://zomato-recai-frontend.vercel.app",
        "https://zomato-recai.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("[STARTUP] FastAPI app created, initializing service...")

try:
    service = RecommendationService()
    print("[STARTUP] RecommendationService initialized OK")
except Exception as e:
    print(f"[FATAL] Failed to initialize RecommendationService: {e}")
    traceback.print_exc()
    sys.exit(1)

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "restaurant-recommendation-api"}

@app.get("/api/v1/locations")
async def get_locations():
    locations = service.get_unique_locations()
    return {"locations": locations}

@app.post("/api/v1/recommend", response_model=RecommendationResponse)
async def recommend(request: RecommendationRequest):
    payload = request.dict(exclude={"session_id", "top_k"})
    result = service.get_recommendations(
        payload=payload, 
        session_id=request.session_id, 
        top_k=request.top_k
    )
    
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result)
        
    return result

@app.get("/api/v1/history/{session_id}")
async def get_history(session_id: str):
    try:
        history = service.get_history(session_id)
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/recent-searches")
async def get_recent_searches():
    try:
        searches = service.get_recent_searches(limit=15)
        return searches
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/feedback")
async def save_feedback(request: FeedbackRequest):
    try:
        service.save_feedback(request.dict())
        return {"status": "success", "message": "Feedback saved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

print("[STARTUP] All routes registered. Ready to serve.")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
