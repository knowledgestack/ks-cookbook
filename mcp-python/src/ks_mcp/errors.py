"""Map ``ksapi.ApiException`` onto MCP-friendly responses."""


import ksapi
from mcp import McpError
from mcp.types import INTERNAL_ERROR, INVALID_PARAMS, ErrorData


def rest_to_mcp(exc: ksapi.ApiException) -> McpError:
    """Convert a REST error into an MCP error with an agent-readable message."""
    status = getattr(exc, "status", 0)
    body = getattr(exc, "body", "") or ""
    snippet = str(body)[:300] if body else ""

    if status == 401:
        msg = "Invalid KS_API_KEY (401). Re-check the key exported to the MCP server."
        return McpError(ErrorData(code=INVALID_PARAMS, message=msg))
    if status == 402:
        msg = (
            "KS quota exhausted (402). This key has hit its daily request limit; "
            "stop looping and inform the user."
        )
        return McpError(ErrorData(code=INTERNAL_ERROR, message=msg))
    if status == 403:
        msg = f"Forbidden for this path (403). {snippet}"
        return McpError(ErrorData(code=INVALID_PARAMS, message=msg))
    if status >= 500:
        msg = (
            f"KS backend error ({status}). Transient; retry later, do not auto-loop. "
            f"{snippet}"
        )
        return McpError(ErrorData(code=INTERNAL_ERROR, message=msg))

    return McpError(
        ErrorData(code=INTERNAL_ERROR, message=f"Unexpected {status} from KS: {snippet}")
    )


def is_not_found(exc: ksapi.ApiException) -> bool:
    """404 is probe-able data — surface as a structured result, not an MCP error."""
    return getattr(exc, "status", 0) == 404
