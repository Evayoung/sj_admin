"""Pytest fixtures for SJ Interiors Admin."""

import importlib.util
import sys
from pathlib import Path

import pytest
from starlette.testclient import TestClient

APP_PATH = Path(__file__).with_name("main.py")
ROOT = APP_PATH.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture(scope="session")
def app():
    """Import and return the FastHTML app."""
    spec = importlib.util.spec_from_file_location("sj_admin_app", APP_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.app


@pytest.fixture(scope="session")
def client(app):
    """Return a test client for the app."""
    return TestClient(app)
