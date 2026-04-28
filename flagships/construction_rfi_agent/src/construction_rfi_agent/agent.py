"""pydantic-ai agent that drafts construction RFI responses grounded in KS corpus."""

import os

from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio

from construction_rfi_agent.schema import RFIDraft

SYSTEM_TEMPLATE = """\
You are a senior project engineer on a commercial construction project.
Draft a response to the RFI below, grounded strictly in the documents
available under the CORPUS folder via MCP tools (CSI MasterFormat spec
sections, ASHRAE / FHWA standards, project drawings, prior approved
submittals, addenda).

MANDATORY workflow:
1. Call ``list_contents`` with ``folder_id=__CORPUS_FOLDER_ID__`` to find
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
        system_prompt=SYSTEM_TEMPLATE.replace("__CORPUS_FOLDER_ID__", corpus_folder_id),
        output_type=RFIDraft,
    )
    prompt = f"RFI #{rfi_number}:\n\n{question}\n\nDraft the response."
    async with agent.run_mcp_servers():
        result = await agent.run(prompt)
    return getattr(result, "output", None) or getattr(result, "data", None) or result  # type: ignore[return-value]
