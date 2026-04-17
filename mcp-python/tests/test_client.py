
import pytest


def test_env_returns_default_for_optional(monkeypatch: pytest.MonkeyPatch) -> None:
    from ks_mcp.client import _env

    monkeypatch.delenv("OPTIONAL_VALUE", raising=False)
    assert _env("OPTIONAL_VALUE", required=False, default="fallback") == "fallback"


def test_env_raises_for_missing_required(monkeypatch: pytest.MonkeyPatch) -> None:
    from ks_mcp.client import _env

    monkeypatch.delenv("KS_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="KS_API_KEY is not set"):
        _env("KS_API_KEY")


def test_get_api_client_sets_auth_header(monkeypatch: pytest.MonkeyPatch) -> None:
    from ks_mcp.client import get_api_client

    get_api_client.cache_clear()
    monkeypatch.setenv("KS_API_KEY", "sk-user-custom")
    monkeypatch.setenv("KS_BASE_URL", "https://api.example.com")

    client = get_api_client()

    assert client.configuration.host == "https://api.example.com"
    assert client.default_headers["Authorization"] == "Bearer sk-user-custom"

    get_api_client.cache_clear()


def test_get_api_client_is_cached() -> None:
    from ks_mcp.client import get_api_client

    get_api_client.cache_clear()
    client_a = get_api_client()
    client_b = get_api_client()

    assert client_a is client_b

    get_api_client.cache_clear()
