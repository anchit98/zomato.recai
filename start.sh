#!/bin/bash
set -e

echo "[RENDER] Installing dependencies into runtime Python..."
python -m pip install -r requirements.txt --quiet

echo "[RENDER] Verifying pandas..."
python -c "import pandas; print(f'pandas {pandas.__version__} OK')"

echo "[RENDER] Starting ZOMATO REC.AI backend..."
python -u -m uvicorn src.phase6.main:app --host 0.0.0.0 --port 10000
