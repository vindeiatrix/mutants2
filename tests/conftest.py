import sys
from pathlib import Path

# Ensure the package root is importable when tests run from within the tests directory
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
