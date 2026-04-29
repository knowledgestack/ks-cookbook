"""pydantic-ai agent that drafts construction RFI responses grounded in KS corpus."""

import os

from pydantic_ai import Agent
from pydantic_ai.usage import UsageLimits
from pydantic_ai.mcp import MCPServerStdio

from construction_rfi_agent.schema import RFIDraft

SYSTEM_TEMPLATE = """\
You are a senior project engineer on a commercial construction project.
Draft a response to the RFI below, grounded strictly in the documents
available under the CORPUS folder via MCP tools (CSI MasterFormat spec
sections, ASHRAE / FHWA standards, project drawings, prior approved
submittals, addenda).

MANDATORY workflow:
1. Call ``list_contents`` with ``folder_id=your tenant (use search_knowledge — no folder_id needed)`` to find
   the relevant specs, drawings, and prior RFIs / submittals.
2. Call ``read`` on each relevant document using its UUID ``path_part_id``.
3. Every ``Citation.chunk_id`` you emit MUST be copied verbatim from a
   ``[chunk:<uuid>]`` marker in the ``read`` output.
4. Produce the structured ``RFIDraft``:
   - Identify the applicable CSI MasterFormat division(s); each
     ``SpecReference`` must carry a real citation.
   - Flag ``needs_architect_response=true`` if the RFI implicates design
     intent (clashes, substitutions, performance criteria) rather than
     means-and-methods.
   - ``schedule_impact_days`` and ``cost_impact`` must be evidenced — if the
     corpus gives no basis, say so in ``draft_response`` and set them to 0
     and 'none' respectively, with confidence=low.

Do not fabricate sheet numbers, spec sections, or product data. If a fact
is not in the corpus, say so explicitly.

KS workflow (do NOT skip):
1. Ask Knowledge Stack specific natural-language questions about the input. Never use folder UUIDs or path_part_id filters.
2. search_knowledge returns hits with chunk_id and path_part_id; the text field is empty by design. Call read(path_part_id=<hit's path_part_id>) to get chunk content. The trailing [chunk:<uuid>] marker is the citation chunk_id. NEVER pass chunk_id to read; it 404s.
3. Build every output field ONLY from chunk text you read. Never fabricate.
4. Populate every citation with chunk_id (verbatim from the marker), document_name (filename from read() metadata or materialized_path), snippet (verbatim ≤240 chars).

Output format (STRICT): Your final response is a single JSON object that matches the response schema exactly. Do NOT wrap it in an extra key like {'<ClassName>': ...} or {'result': ...}. Every required string field is a string, not a nested object. Every required nested model is included with all of its required fields populated. Never omit required fields; never add unspecified ones.
"""


async def draft_rfi(
    *,
    rfi_number: str,
    question: str,
    corpus_folder_id: str,
    model: str,
) -> RFIDraft:
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
        output_type=RFIDraft,
        retries=4,
        output_retries=4,
    )
    prompt = f"RFI #{rfi_number}:\n\n{question}\n\nDraft the response."
    async with agent.run_mcp_servers():
        result = await agent.run(prompt, usage_limits=UsageLimits(request_limit=200))
    return getattr(result, "output", None) or getattr(result, "data", None) or result  # type: ignore[return-value]
