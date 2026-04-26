#!/bin/bash
set -e

echo "[RENDER] Installing dependencies into runtime environment..."
pip install -r requirements.txt --quiet

echo "[RENDER] Starting ZOMATO REC.AI backend..."
python -u -m uvicorn src.phase6.main:app --host 0.0.0.0 --port 10000
