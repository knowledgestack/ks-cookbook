"""Tenant-context tools: organisation info + current datetime."""


import os
from datetime import UTC, datetime
from zoneinfo import ZoneInfo

import httpx
import ksapi
from mcp.server.fastmcp import FastMCP

from ks_mcp.client import get_api_client
from ks_mcp.errors import rest_to_mcp
from ks_mcp.schema import CurrentDateTime, OrganizationInfo

_cached_tenant: OrganizationInfo | None = None


def _fetch_tenant_via_httpx() -> OrganizationInfo:
    """Fallback for deployments whose SDK / backend doesn't yet expose ``GET /v1/tenants/me``.

    Tries ``/v1/tenants/me`` first, and if the backend pre-dates that route
    (returns 404 / 422 because ``me`` is being parsed as a UUID path param),
    falls back to ``/v1/tenants`` and picks the first one the caller belongs to.
    """
    base = os.environ.get("KS_BASE_URL", "https://api.knowledgestack.ai")
    key = os.environ.get("KS_API_KEY", "")
    with httpx.Client(base_url=base, headers={"Authorization": f"Bearer {key}"}, timeout=30) as c:
        r = c.get("/v1/tenants/me")
        if r.status_code in (404, 422):
            r = c.get("/v1/tenants", params={"limit": 1})
            r.raise_for_status()
            payload = r.json()
            items = payload.get("items") or []
            if not items:
                raise RuntimeError("No tenants visible to this API key.")
            body = items[0]
        else:
            r.raise_for_status()
            body = r.json()
    settings = body.get("settings") or {}
    return OrganizationInfo(
        tenant_id=body["id"],
        name=body.get("name", ""),
        default_language=str(settings.get("language", "en")),
        timezone=str(settings.get("timezone", "UTC")),
    )


def _fetch_tenant() -> OrganizationInfo:
    global _cached_tenant
    if _cached_tenant is not None:
        return _cached_tenant

    tenants_api = getattr(ksapi, "TenantsApi", None)
    if tenants_api is not None and hasattr(tenants_api(get_api_client()), "get_current_tenant"):
        try:
            t = tenants_api(get_api_client()).get_current_tenant()
            settings = getattr(t, "settings", None)
            info = OrganizationInfo(
                tenant_id=t.id,
                name=getattr(t, "name", ""),
                default_language=str(getattr(settings, "language", "en")) if settings else "en",
                timezone=str(getattr(settings, "timezone", "UTC")) if settings else "UTC",
            )
        except ksapi.ApiException as exc:
            raise rest_to_mcp(exc) from exc
    else:
        info = _fetch_tenant_via_httpx()

    _cached_tenant = info
    return info


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    def get_organization_info() -> OrganizationInfo:
        """Return the caller's tenant metadata: id, name, default language, timezone."""
        return _fetch_tenant()

    @mcp.tool()
    def get_current_datetime() -> CurrentDateTime:
        """Return current date/time in both UTC and the tenant's timezone."""
        info = _fetch_tenant()
        now_utc = datetime.now(UTC)
        try:
            zone = ZoneInfo(info.timezone)
        except Exception:  # noqa: BLE001
            zone = UTC
        now_local = now_utc.astimezone(zone)
        return CurrentDateTime(
            iso_utc=now_utc.isoformat(),
            iso_local=now_local.isoformat(),
            timezone=str(zone),
        )
