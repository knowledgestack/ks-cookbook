
import ksapi
from mcp.types import INTERNAL_ERROR, INVALID_PARAMS

from ks_mcp.errors import is_not_found, rest_to_mcp


def _api_exception(status: int, body: str = "") -> ksapi.ApiException:
    return ksapi.ApiException(status=status, reason="error", body=body)


def test_rest_to_mcp_maps_401_to_invalid_params() -> None:
    error = rest_to_mcp(_api_exception(401))

    assert error.error.code == INVALID_PARAMS
    assert "Invalid KS_API_KEY" in error.error.message


def test_rest_to_mcp_maps_403_to_invalid_params_with_body() -> None:
    error = rest_to_mcp(_api_exception(403, body="denied"))

    assert error.error.code == INVALID_PARAMS
    assert "Forbidden for this path" in error.error.message
    assert "denied" in error.error.message


def test_rest_to_mcp_maps_402_to_internal_error() -> None:
    error = rest_to_mcp(_api_exception(402))

    assert error.error.code == INTERNAL_ERROR
    assert "quota exhausted" in error.error.message


def test_rest_to_mcp_maps_500_to_internal_error() -> None:
    error = rest_to_mcp(_api_exception(500, body="boom"))

    assert error.error.code == INTERNAL_ERROR
    assert "backend error (500)" in error.error.message
    assert "boom" in error.error.message


def test_is_not_found_only_for_404() -> None:
    assert is_not_found(_api_exception(404)) is True
    assert is_not_found(_api_exception(403)) is False
