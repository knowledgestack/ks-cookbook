"""MCP <-> OpenAI Realtime bridge + session summarizer."""


import json
import os
from contextlib import asynccontextmanager
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from pydantic_ai import Agent

from realtime_voice_sdr.schema import SessionSummary

TURN_INSTRUCTIONS = """\
You are an SDR running live discovery with a prospect. The MCP tools exposed
to you are the KS corpus containing your product one-pager, ICP, past wins,
objection library, and pricing. Call ``list_contents`` on
folder_id=__CORPUS_FOLDER_ID__ first to enumerate, then ``read`` with
``path_part_id`` whenever you need a specific fact, metric, or proof point.

Conversation style:
- One question at a time. Short, human. No walls of text.
- Track MEDDIC silently: Metrics, Economic buyer, Decision criteria, Decision
  process, Identify pain, Champion. Prioritize the weakest dimension.
- Never invent numbers, customer names, or features. If unknown, ask.
- When citing a fact, briefly mention the source document — the SessionSummary
  will pull any [chunk:<uuid>] tags you saw.

Prospect context for this call: __PROSPECT_CONTEXT__.
"""

SUMMARY_SYSTEM = """\
You are summarizing an SDR discovery call. Read the transcript below and
produce a ``SessionSummary``:
- Score each MEDDIC dimension (covered / partial / missing) from the
  transcript alone — no optimism bias.
- ``next_step`` must be concrete with a time commitment.
- ``tool_calls`` = number of tool calls the SDR made (visible as
  ``[tool: ...]`` lines in the transcript).
"""


@asynccontextmanager
async def mcp_session():
    params = StdioServerParameters(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={
            "KS_API_KEY": os.environ.get("KS_API_KEY", ""),
            "KS_BASE_URL": os.environ.get("KS_BASE_URL", ""),
        },
    )
    async with stdio_client(params) as (reader, writer):
        async with ClientSession(reader, writer) as session:
            await session.initialize()
            yield session


async def discover_tools(session: ClientSession) -> list[dict[str, Any]]:
    """List MCP tools and convert to Realtime API function-tool schemas."""
    result = await session.list_tools()
    tools: list[dict[str, Any]] = []
    for t in result.tools:
        tools.append({
            "type": "function",
            "name": t.name,
            "description": (t.description or "")[:1024],
            "parameters": t.inputSchema or {"type": "object", "properties": {}},
        })
    return tools


async def call_mcp_tool(session: ClientSession, name: str, arguments: str) -> str:
    """Proxy a Realtime API function call to the MCP server; return string body."""
    try:
        args = json.loads(arguments) if isinstance(arguments, str) and arguments else {}
    except json.JSONDecodeError:
        args = {}
    result = await session.call_tool(name, args)
    if result.isError:
        msg = result.content[0].text if result.content else "unknown error"
        return f"ERROR: {msg}"
    return "\n".join(c.text for c in result.content if hasattr(c, "text"))[:8000]


def build_summary_agent(*, model: str) -> Agent:
    return Agent(
        model=f"openai:{model}", system_prompt=SUMMARY_SYSTEM,
        output_type=SessionSummary,
    )


def instructions_for(corpus_folder_id: str, prospect_context: str) -> str:
    return (
        TURN_INSTRUCTIONS
        .replace("__CORPUS_FOLDER_ID__", corpus_folder_id)
        .replace("__PROSPECT_CONTEXT__", prospect_context or "(none provided)")
    )
