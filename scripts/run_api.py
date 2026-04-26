from __future__ import annotations
import src.bootstrap # MUST be first to clean path and env
import sys
from pathlib import Path

if __name__ == "__main__":
    import uvicorn
    print("Starting VibeCheck AI Recommendation API...")
    
    # Run uvicorn using the module string to ensure the reloader picks up the correct path
    uvicorn.run(
        "src.phase6.main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )
