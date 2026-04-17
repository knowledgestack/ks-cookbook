"""pydantic-ai agent for Grant Compliance Checker."""

import os

from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio
from pydantic_ai.usage import UsageLimits

from grant_compliance_checker.schema import ComplianceCheck

SYSTEM = """\
You are an expert producing a Grant Compliance Checker. Make at most 3 tool calls total. Use ONLY `list_contents` and `read`
MCP tools to retrieve documents from the corpus folder
(folder_id=__FOLDER_ID__). The `read` output has inline [chunk:<uuid>]
markers — copy those verbatim into every Citation.chunk_id you emit.
Ground every claim in retrieved text. If evidence is insufficient, say so.
Use UUID path_part_ids from list_contents, NOT document names.
"""


async def run_agent(*, input_text: str, corpus_folder_id: str, model: str) -> ComplianceCheck:
    server_cmd = os.environ.get("KS_MCP_COMMAND", "uvx")
    server_args = (os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split()
    mcp = MCPServerStdio(
        command=server_cmd, args=server_args,
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(
        model=f"openai:{model}", mcp_servers=[mcp],
        system_prompt=SYSTEM.replace("__FOLDER_ID__", corpus_folder_id),
        output_type=ComplianceCheck,
    )
    memo = None
    try:
        async with agent.run_mcp_servers():
            result = await agent.run(input_text, usage_limits=UsageLimits(request_limit=25))
            memo = getattr(result, "output", None) or getattr(result, "data", None) or result
    except BaseExceptionGroup:
        pass
    if memo is None:
        raise RuntimeError("Agent did not produce a result.")
    return memo
