import sys
from pathlib import Path
import copy
import pytest

# Ensure src directory is on sys.path so we can import app
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import app as app_module  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402


@pytest.fixture
def client():
    """Provide a FastAPI TestClient for the app."""
    return TestClient(app_module.app)


@pytest.fixture(autouse=True)
def reset_in_memory_db():
    """Reset the in-memory activities dict after each test to avoid cross-test pollution."""
    original = copy.deepcopy(app_module.activities)
    try:
        yield
    finally:
        app_module.activities.clear()
        app_module.activities.update(copy.deepcopy(original))
