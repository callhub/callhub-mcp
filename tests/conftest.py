"""Shared test fixtures. Puts src/ on the import path so `server`, `callhub.*`
and `tools_callhub` import the same way they do when the server is launched."""
import sys
import pathlib

import pytest

SRC = pathlib.Path(__file__).resolve().parent.parent / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


@pytest.fixture
def default_credentials(monkeypatch):
    """Provide a minimal 'default' CallHub account via environment variables."""
    monkeypatch.setenv("CALLHUB_API_KEY", "test-key")
    monkeypatch.setenv("CALLHUB_BASE_URL", "https://api-na1.callhub.io")
    monkeypatch.setenv("CALLHUB_USERNAME", "tester@example.com")
    yield
