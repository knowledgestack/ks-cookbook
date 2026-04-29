"""pydantic-ai agent wired to the KS MCP server."""

import os
from pathlib import Path

from pydantic_ai import Agent
from pydantic_ai.usage import UsageLimits
from pydantic_ai.mcp import MCPServerStdio

from research_brief.schema import BriefOutput

SYSTEM_PROMPT = """\
You are a research analyst. Given a topic, produce a concise brief grounded in
the caller's knowledge base (exposed via MCP tools).

Workflow:
1. Call ``search_keyword`` first with concrete title or policy terms from the
   topic to find likely matching chunks quickly.
2. If keyword results are sparse or ambiguous, call ``search_knowledge`` to
   broaden recall semantically.
3. For the most promising hits, call ``read`` or ``read_around`` to pull enough
   surrounding context to ground your claims.
4. Build the ``BriefOutput`` with:
   - 3–6 sections, each 150–400 words.
   - Inline references like "[1]" that map to the ``citations`` list.
   - One ``Citation`` per distinct chunk you actually relied on.

Do NOT invent facts not supported by retrieved chunks. If you lack evidence
for a section, say so and cite a placeholder chunk_id.

Return a single ``BriefOutput`` — no prose around it.


KS workflow (do NOT skip):
1. Ask Knowledge Stack specific natural-language questions about the input. Never use folder UUIDs.
2. search_knowledge returns hits with chunk_id and path_part_id; the text field is empty by design. Call read(path_part_id=<hit's path_part_id>) to get chunk content. The trailing [chunk:<uuid>] marker is the citation chunk_id. NEVER pass chunk_id to read; it 404s.
3. Build every output field ONLY from chunk text you read. Never fabricate.
4. Populate every citation with chunk_id (verbatim from the marker), document_name (filename from read() metadata or materialized_path), snippet (verbatim ≤240 chars).

Available MCP tools (use ONLY these): search_knowledge, search_keyword, read, find, list_contents, get_info. There is NO 'cite' tool.

Output format (STRICT): Your final response is a single JSON object that matches the response schema exactly. Do NOT wrap it in an extra key like {'<ClassName>': ...} or {'result': ...}. Every required string field is a string, not a nested object. Every required nested model is included with all of its required fields populated. Never omit required fields; never add unspecified ones.
"""


def build_agent(model: str = "openai:gpt-4o") -> Agent[None, BriefOutput]:
    """Construct the pydantic-ai Agent wired to the stdio MCP server.

    ``model`` can be any pydantic-ai-supported id (e.g. ``openai:gpt-4o``,
    ``anthropic:claude-opus-4-6``).
    """
    local_ks_mcp = Path.cwd() / ".venv" / "bin" / "ks-mcp"
    if "KS_MCP_COMMAND" in os.environ:
        server_cmd = os.environ["KS_MCP_COMMAND"]
        server_args = (os.environ.get("KS_MCP_ARGS", "") or "").split()
    elif local_ks_mcp.exists():
        server_cmd = str(local_ks_mcp)
        server_args = []
    else:
        server_cmd = "uvx"
        server_args = ["knowledgestack-mcp"]
    mcp_server = MCPServerStdio(
        command=server_cmd,
        args=server_args,
        env={
            "KS_API_KEY": os.environ.get("KS_API_KEY", ""),
            "KS_BASE_URL": os.environ.get("KS_BASE_URL", ""),
        },
    )
    return Agent(
        model=model,
        mcp_servers=[mcp_server],
        system_prompt=SYSTEM_PROMPT,
        output_type=BriefOutput,
        retries=4,
        output_retries=4,
    )


async def research_topic(topic: str, *, model: str = "openai:gpt-4o") -> BriefOutput:
    """Run the agent against a topic and return a validated ``BriefOutput``."""
    agent = build_agent(model=model)
    async with agent.run_mcp_servers():
        result = await agent.run(topic, usage_limits=UsageLimits(request_limit=200))
    return result.output
