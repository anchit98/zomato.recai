import sys
import os
from pathlib import Path
import site

def setup_environment():
    """
    Ensures the Python environment is clean and correctly mapped,
    bypassing any corrupted virtual environments in the project root.
    """
    ROOT = Path(__file__).resolve().parents[1]
    
    # 1. Force the Project Root to the top of the search path
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
        
    # 2. Identify and SCRUB the broken .venv from sys.path
    # This prevents 'ModuleNotFoundError' when Python tries to look in a corrupted venv
    sys.path = [p for p in sys.path if ".venv" not in p.lower()]
    
    # 3. Ensure User Site-Packages (where our global libs are) are included
    user_site = site.getusersitepackages()
    if os.path.exists(user_site) and user_site not in sys.path:
        sys.path.append(user_site)
        
    # 4. Clean up environment variables that might confuse child processes (Uvicorn reload)
    os.environ.pop("VIRTUAL_ENV", None)
    
    # 5. Set PYTHONPATH to root to help sub-processes
    os.environ["PYTHONPATH"] = str(ROOT)

# Run bootstrap immediately on import
setup_environment()
