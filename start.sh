#!/bin/bash
set -e

echo "[RENDER] Installing dependencies into runtime Python..."
python -m pip install -r requirements.txt --quiet

echo "[RENDER] Verifying pandas..."
python -c "import pandas; print(f'pandas {pandas.__version__} OK at {pandas.__file__}')"

echo "[RENDER] Diagnostics..."
python -c "
import sys
print(f'Python: {sys.executable}')
print(f'sys.path: {sys.path}')
import pandas
print(f'pandas at: {pandas.__file__}')
"

echo "[RENDER] Starting ZOMATO REC.AI backend..."
python -u -c "
import sys, os
os.environ['PYTHONUNBUFFERED'] = '1'
sys.path.insert(0, '.')
from src.phase6.main import app
import uvicorn
uvicorn.run(app, host='0.0.0.0', port=10000)
"
