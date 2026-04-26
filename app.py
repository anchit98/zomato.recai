"""
ZOMATO REC.AI — Production entry point for Render deployment.
This file imports everything at the top level to avoid Python's
package-relative import issues caused by Render's /opt/render/project/src/ path
colliding with our src/ package directory.
"""
from __future__ import annotations

import os
import sys

# Force unbuffered output
os.environ["PYTHONUNBUFFERED"] = "1"

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("[BOOT] Starting ZOMATO REC.AI...")

try:
    import traceback
    # Pre-import all heavy dependencies at top level BEFORE entering the src package
    import pandas
    import requests
    import json
    import supabase
    print(f"[BOOT] pandas {pandas.__version__} OK")
    print(f"[BOOT] supabase {supabase.__version__} OK")
except Exception as e:
    print(f"[FATAL] Failed during top-level imports: {e}")
    traceback.print_exc()
    sys.exit(1)

try:
    # Now import the FastAPI app
    from src.phase6.main import app  # noqa: E402
    print("[BOOT] App imported successfully. Handing off to uvicorn.")
except Exception as e:
    print(f"[FATAL] Failed to import app from src.phase6.main: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)

