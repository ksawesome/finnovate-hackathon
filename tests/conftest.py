import os
import sys
from pathlib import Path

# Ensure project root and src are on sys.path for tests
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
for p in [str(ROOT), str(SRC)]:
    if p not in sys.path:
        sys.path.insert(0, p)

# Ensure a default GOOGLE_API_KEY to avoid unrelated imports failing in tools
os.environ.setdefault("GOOGLE_API_KEY", "test-key")
