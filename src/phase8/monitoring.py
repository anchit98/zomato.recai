import time
import logging
from pathlib import Path
from datetime import datetime
from typing import Any, Optional
import os
import json

# Configure local logging as a secondary fallback
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
logging.basicConfig(
    filename=LOG_DIR / "telemetry.log",
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s'
)

class TelemetryService:
    @staticmethod
    def log_recommendation_event(
        session_id: str,
        latency_ms: float,
        success: bool,
        model: str,
        token_usage: Optional[dict] = None,
        error: Optional[str] = None
    ):
        """
        Logs a recommendation event for performance monitoring.
        """
        event = {
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id,
            "latency_ms": round(latency_ms, 2),
            "status": "success" if success else "error",
            "model": model,
            "token_usage": token_usage,
            "error_message": error
        }
        
        # Log to file
        logging.info(json.dumps(event))
        
        # In a full implementation, we would also push this to Supabase 'metrics' table
        print(f"[TELEMETRY] Request for {session_id} finished in {latency_ms:.2f}ms | Status: {'SUCCESS' if success else 'ERROR'}")

    @staticmethod
    def track_latency(func):
        """Decorator to measure function execution time."""
        def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                latency = (time.perf_counter() - start_time) * 1000
                return result, latency
            except Exception as e:
                latency = (time.perf_counter() - start_time) * 1000
                raise e
        return wrapper
