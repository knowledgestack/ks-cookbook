"""Server-level smoke tests for the KS MCP server."""


EXPECTED_TOOLS = {
    "search_knowledge",
    "search_keyword",
    "read",
    "read_around",
    "list_contents",
    "find",
    "get_info",
    "view_chunk_image",
    "get_organization_info",
    "get_current_datetime",
}


def test_build_server_metadata() -> None:
    from ks_mcp.server import build_server

    mcp = build_server(host="0.0.0.0", port=9999)
    assert mcp.name == "knowledgestack"
    assert "search_knowledge" in mcp.instructions
    assert "read_around" in mcp.instructions


async def test_all_tools_registered() -> None:
    from ks_mcp.server import build_server

    mcp = build_server()
    tools = await mcp.list_tools()
    names = {t.name for t in tools}
    assert EXPECTED_TOOLS.issubset(names), (
        f"Missing tools: {EXPECTED_TOOLS - names}"
    )


async def test_every_tool_has_non_empty_description() -> None:
    from ks_mcp.server import build_server

    mcp = build_server()
    tools = await mcp.list_tools()
    missing_desc = [t.name for t in tools if not (t.description or "").strip()]
    assert not missing_desc, f"Tools lacking description: {missing_desc}"


async def test_every_tool_has_input_schema() -> None:
    from ks_mcp.server import build_server

    mcp = build_server()
    tools = await mcp.list_tools()
    for t in tools:
        assert t.inputSchema, f"{t.name} has no inputSchema"
