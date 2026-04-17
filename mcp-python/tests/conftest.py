
import pytest


@pytest.fixture(autouse=True)
def _stub_env(monkeypatch: pytest.MonkeyPatch) -> None:
    # Provide fake env so imports and client creation are deterministic in tests.
    monkeypatch.setenv("KS_API_KEY", "sk-user-test")
    monkeypatch.setenv("KS_BASE_URL", "http://localhost:8000")
