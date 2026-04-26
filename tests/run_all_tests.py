import unittest
import sys
from pathlib import Path

def run_all():
    print("--- Running AI Restaurant Recommendation System Test Suite ---")
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir="tests", pattern="test_*.py")
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    if result.wasSuccessful():
        print("\nALL TESTS PASSED!")
        sys.exit(0)
    else:
        print("\nSOME TESTS FAILED. CHECK LOGS.")
        sys.exit(1)

if __name__ == "__main__":
    run_all()
