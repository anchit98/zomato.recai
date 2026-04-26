import subprocess
import time
import sys
import os
from pathlib import Path

def start_vibecheck():
    root = Path(__file__).resolve().parents[1]
    
    print("[START] Starting VibeCheck Full-Stack Application...")
    
    # Clean environment to prevent .venv inheritance
    env = os.environ.copy()
    env.pop("VIRTUAL_ENV", None)
    env["PYTHONPATH"] = str(root)

    backend_proc = subprocess.Popen(
        [r"C:\Python314\python.exe", "scripts/run_api.py"],
        cwd=root,
        env=env
    )
    
    # Give backend a moment to start
    time.sleep(2)
    
    # 2. Start Frontend
    print("[WEB] Starting Frontend (Next.js)...")
    frontend_proc = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=root / "frontend",
        shell=True
    )
    
    print("\n[SUCCESS] Both services are starting!")
    print("Backend: http://localhost:8000")
    print("Frontend: http://localhost:3000")
    print("\nPress Ctrl+C to stop both services.")

    try:
        while True:
            # Check if processes are still running
            if backend_proc.poll() is not None:
                print("[ERROR] Backend process stopped unexpectedly.")
                break
            if frontend_proc.poll() is not None:
                print("[ERROR] Frontend process stopped unexpectedly.")
                break
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
    finally:
        backend_proc.terminate()
        frontend_proc.terminate()

if __name__ == "__main__":
    start_vibecheck()
