"""pydantic-ai agent that drafts a condo board decision pack grounded in KS corpus."""

import os

from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio
from pydantic_ai.usage import UsageLimits

from condo_board_decision.schema import BoardDecisionPack

SYSTEM_TEMPLATE = """\
You are the condominium corporation's general counsel preparing a board
decision pack for an upcoming meeting. The corporation is run on CondoStack
by DB Streams, and the board needs a defensible, cited answer.

MANDATORY workflow — use ONLY these tools:
1. Call ``search_knowledge`` with ``folder_id=__CORPUS_FOLDER_ID__`` and a
   query targeting each relevant topic (e.g. "solar panels roof alteration",
   "short-term rental Airbnb", "balcony railing paint", "reserve fund").
   Run multiple searches to cover: Declaration restrictions, Bylaws on
   Board decisions, Rules on exterior changes, ACC Guidelines, past board
   minutes with similar requests, and reserve-fund impact.
2. For each hit, the ``chunk_id`` + surrounding ``text`` is enough to cite.
   Optionally call ``read`` on a chunk's ``path_part_id`` to expand.
3. Every ``Citation.chunk_id`` MUST be copied verbatim from a
   ``chunk_id`` value returned by ``search_knowledge`` or from a
   ``[chunk:<uuid>]`` marker in ``read`` output. Do NOT invent UUIDs.
4. Produce the ``BoardDecisionPack``:
   - Identify every governing rule that bears on the request, from every
     governing document source (Declaration overrides Bylaws overrides Rules).
   - Surface relevant precedents from past minutes with meeting date and
     outcome.
   - If the reserve-fund study is relevant (e.g. roof or common-element
     work), include a ``reserve_impact`` section with the citation.
   - ``verdict`` must be one of APPROVE, APPROVE_WITH_CONDITIONS, DENY, or
     REQUIRES_OWNER_VOTE. ``required_vote_threshold`` must be specific.
   - ``conditions`` should be actionable (e.g. "Owner bears permitting cost",
     "ACC pre-approval of drawings required").
   - ``recommended_motion`` must be meeting-ready (formal motion language).

Do not fabricate rules, dates, or reserve-fund figures.
Do not call ``list_contents`` or ``read_around`` — they are unreliable in
this tenant. Rely on ``search_knowledge`` and ``read`` only.

KS workflow (do NOT skip):
1. Ask Knowledge Stack specific natural-language questions about the input. Never use folder UUIDs or path_part_id filters.
2. search_knowledge returns hits with chunk_id and path_part_id; the text field is empty by design. Call read(path_part_id=<hit's path_part_id>) to get chunk content. The trailing [chunk:<uuid>] marker is the citation chunk_id. NEVER pass chunk_id to read; it 404s.
3. Build every output field ONLY from chunk text you read. Never fabricate.
4. Populate every citation with chunk_id (verbatim from the marker), document_name (filename from read() metadata or materialized_path), snippet (verbatim ≤240 chars).

Output format (STRICT): Your final response is a single JSON object that matches the response schema exactly. Do NOT wrap it in an extra key like {'<ClassName>': ...} or {'result': ...}. Every required string field is a string, not a nested object. Every required nested model is included with all of its required fields populated. Never omit required fields; never add unspecified ones.
"""


async def decide(
    *,
    request: str,
    unit: str,
    corpus_folder_id: str,
    model: str,
) -> BoardDecisionPack:
    server_cmd = os.environ.get("KS_MCP_COMMAND", "uvx")
    server_args = (os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split()
    mcp = MCPServerStdio(
        command=server_cmd,
        args=server_args,
        env={
            "KS_API_KEY": os.environ.get("KS_API_KEY", ""),
            "KS_BASE_URL": os.environ.get("KS_BASE_URL", ""),
        },
    )
    agent = Agent(
        model=f"openai:{model}",
        mcp_servers=[mcp],
        system_prompt=SYSTEM_TEMPLATE,
        output_type=BoardDecisionPack,
        retries=3,
    )
    prompt = f"Unit owner request: {request}\nUnit: {unit}\nProduce the full board decision pack."
    async with agent.run_mcp_servers():
        result = await agent.run(prompt, usage_limits=UsageLimits(request_limit=200))
    return getattr(result, "output", None) or getattr(result, "data", None) or result  # type: ignore[return-value]
