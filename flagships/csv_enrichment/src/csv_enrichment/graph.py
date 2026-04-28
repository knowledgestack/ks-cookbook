"""LangGraph StateGraph for concurrent CSV enrichment against the KS MCP server."""

import asyncio
import csv
from pathlib import Path
from typing import Any

from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.graph import END, START, StateGraph

from csv_enrichment.schema import EnrichmentState, Row

SYSTEM_PROMPT = """\
You are a data analyst enriching one row of a customer CSV.

Given the row's query string:
1. Call ``search_knowledge`` with top_k=3.
2. Call ``read`` on the most relevant hit.
3. Produce ONE short paragraph (<=150 words) summarizing what the knowledge
   base knows. Every factual claim MUST end with a ``[chunk:<uuid>]`` tag
   copied verbatim from the ``read`` tool's output — never synthesize
   chunk UUIDs.

Return only the paragraph — no preamble, no structured JSON.
"""


async def _build_tools() -> list[Any]:
    """Connect to the KS MCP server over stdio and load its tools as LangChain tools.

    ``KS_MCP_COMMAND`` lets dev setups point at a local editable install
    (``.venv/bin/ks-mcp``) instead of the published ``uvx knowledgestack-mcp``.
    """
    import os

    command = os.environ.get("KS_MCP_COMMAND", "uvx")
    args_raw = os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp")
    args = args_raw.split() if args_raw else []

    client = MultiServerMCPClient(
        {
            "knowledgestack": {
                "command": command,
                "args": args,
                "transport": "stdio",
                "env": {
                    "KS_API_KEY": os.environ.get("KS_API_KEY", ""),
                    "KS_BASE_URL": os.environ.get("KS_BASE_URL", ""),
                },
            }
        }
    )
    return await client.get_tools()


async def _enrich_one(row: Row, agent: Any) -> tuple[int, str]:
    try:
        result = await agent.ainvoke(
            {"messages": [("system", SYSTEM_PROMPT), ("user", row["query"])]}
        )
        messages = result.get("messages", [])
        text = messages[-1].content if messages else ""
        if isinstance(text, list):
            text = " ".join(p.get("text", "") for p in text if isinstance(p, dict))
        return row["index"], (text or "").strip()
    except Exception as exc:  # noqa: BLE001 — partial-failure policy
        return row["index"], f"ERROR: {type(exc).__name__}: {exc}"


async def _enrich_node(state: EnrichmentState) -> dict[str, Any]:
    import os

    from langgraph.prebuilt import create_react_agent

    tools = await _build_tools()

    provider = os.environ.get("CSV_ENRICH_PROVIDER", "openai").lower()
    if provider == "anthropic":
        from langchain_anthropic import ChatAnthropic

        model = ChatAnthropic(
            model=os.environ.get("CSV_ENRICH_MODEL", "claude-opus-4-6"),
            max_tokens=1024,
        )
    else:
        from langchain_openai import ChatOpenAI

        model = ChatOpenAI(
            model=os.environ.get("CSV_ENRICH_MODEL", "gpt-4o"),
            max_tokens=1024,
        )
    agent = create_react_agent(model, tools)

    sem = asyncio.Semaphore(state.get("concurrency", 5))

    async def _bounded(row: Row) -> tuple[int, str]:
        async with sem:
            return await _enrich_one(row, agent)

    coros = [_bounded(r) for r in state["rows"]]
    pairs: list[tuple[int, str]] = []
    for coro in asyncio.as_completed(coros):
        idx, text = await coro
        if state.get("fail_fast") and text.startswith("ERROR:"):
            raise RuntimeError(f"row {idx} failed: {text}")
        pairs.append((idx, text))

    return {"results": dict(pairs)}


def build_graph():
    graph = StateGraph(EnrichmentState)
    graph.add_node("enrich", _enrich_node)
    graph.add_edge(START, "enrich")
    graph.add_edge("enrich", END)
    return graph.compile()


def read_csv(path: Path, *, query_column: str) -> tuple[list[str], list[Row]]:
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        rows: list[Row] = []
        for i, record in enumerate(reader):
            rows.append(
                {
                    "index": i,
                    "data": record,
                    "query": record.get(query_column, "").strip() or record.get(fieldnames[0], ""),
                }
            )
    return fieldnames, rows


def write_csv(
    path: Path,
    fieldnames: list[str],
    rows: list[Row],
    results: dict[int, str],
    new_column: str,
) -> None:
    out_fields = [*fieldnames, new_column] if new_column not in fieldnames else list(fieldnames)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=out_fields)
        writer.writeheader()
        for row in rows:
            record = dict(row["data"])
            record[new_column] = results.get(row["index"], "")
            writer.writerow(record)
