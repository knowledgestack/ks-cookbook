# pyright: reportMissingImports=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportUnknownParameterType=false, reportAny=false, reportAttributeAccessIssue=false, reportUnusedCallResult=false, reportCallIssue=false, reportGeneralTypeIssues=false, reportArgumentType=false, reportOptionalSubscript=false, reportReturnType=false, reportMissingTypeArgument=false, reportDeprecated=false, reportUnannotatedClassAttribute=false
"""Minimal MCP stdio client every recipe uses. ~50 lines, no framework."""

import json
import os
from contextlib import asynccontextmanager
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


@asynccontextmanager
async def ks_mcp_session():
    """Yields a live ``mcp.ClientSession`` connected to `ks-mcp` over stdio.

    Reads ``KS_API_KEY`` / ``KS_BASE_URL`` from the environment. For local dev,
    set ``KS_MCP_COMMAND`` to ``.venv/bin/ks-mcp`` to skip ``uvx``.
    """
    command = os.environ.get("KS_MCP_COMMAND", ".venv/bin/ks-mcp")
    args_raw = os.environ.get("KS_MCP_ARGS", "")
    args = args_raw.split() if args_raw else []
    params = StdioServerParameters(
        command=command,
        args=args,
        env={
            "KS_API_KEY": os.environ.get("KS_API_KEY", ""),
            "KS_BASE_URL": os.environ.get("KS_BASE_URL", ""),
        },
    )
    async with stdio_client(params) as (reader, writer):
        async with ClientSession(reader, writer) as session:
            await session.initialize()
            yield session


async def call(session: ClientSession, name: str, arguments: dict[str, Any]) -> str:
    """Call a tool and return the concatenated text body. Raises on tool error."""
    result = await session.call_tool(name, arguments)
    if result.isError:
        text = result.content[0].text if result.content else "<no error body>"
        raise RuntimeError(f"tool `{name}` failed: {text}")
    return "\n".join(c.text for c in result.content if hasattr(c, "text"))


async def call_list(session: ClientSession, name: str, arguments: dict[str, Any]) -> list[Any]:
    """Call a tool that returns a collection; each MCP content item is parsed as JSON."""
    result = await session.call_tool(name, arguments)
    if result.isError:
        text = result.content[0].text if result.content else "<no error body>"
        raise RuntimeError(f"tool `{name}` failed: {text}")
    out: list[Any] = []
    for c in result.content:
        if not hasattr(c, "text"):
            continue
        try:
            out.append(json.loads(c.text))
        except json.JSONDecodeError:
            out.append(c.text)
    return out
