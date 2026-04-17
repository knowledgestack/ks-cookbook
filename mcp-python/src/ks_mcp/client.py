"""Shared ksapi client factory.

One ``ApiClient`` per server process, pooled across tool calls to avoid
re-doing the TLS handshake for every tool invocation. Reads ``KS_API_KEY`` and
``KS_BASE_URL`` from the environment.
"""


import os
from functools import lru_cache

import ksapi


def _env(key: str, *, required: bool = True, default: str | None = None) -> str:
    value = os.environ.get(key, default)
    if required and not value:
        raise RuntimeError(
            f"{key} is not set. Export it or add it to your MCP client config."
        )
    return value or ""


@lru_cache(maxsize=1)
def get_api_client() -> ksapi.ApiClient:
    """Return a process-singleton authenticated KS API client.

    The KS backend's ``get_current_identity`` accepts
    ``Authorization: Bearer sk-user-...`` on every v1 route, so a single
    header injection is enough.
    """
    base_url = _env("KS_BASE_URL", default="https://api.knowledgestack.ai")
    api_key = _env("KS_API_KEY")

    configuration = ksapi.Configuration(host=base_url)
    client = ksapi.ApiClient(configuration)
    client.set_default_header("Authorization", f"Bearer {api_key}")
    return client
