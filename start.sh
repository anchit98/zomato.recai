#!/bin/bash
set -e

echo "[RENDER] Installing dependencies into runtime Python..."
python -m pip install -r requirements.txt --quiet

echo "[RENDER] Starting via app.py..."
python -u app.py
