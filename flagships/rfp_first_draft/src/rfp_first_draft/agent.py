"""pydantic-ai agent that drafts RFP responses from past proposals in KS."""

import os

from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio

from rfp_first_draft.schema import RFPDraft

SYSTEM = """\
You are a senior sales engineer drafting responses to an RFP (Request for
Proposal). Your company's past proposals, case studies, and capability
documents are stored in a Knowledge Stack tenant.

MANDATORY workflow — use ONLY these two tools:
1. ``list_contents(folder_id=__CORPUS_FOLDER_ID__)`` — enumerate past proposals.
2. ``read(path_part_id=<UUID>, max_chars=8000)`` — read a proposal's text.
   Each passage ends with an inline ``[chunk:<uuid>]`` marker.

IMPORTANT: Do NOT call ``search_knowledge``, ``search_keyword``, ``find``,
``read_around``, or ``get_info``. Only use ``list_contents`` and ``read``.

Use the UUID path_part_id values from list_contents — NOT document names.

INSTRUCTIONS:
1. List the corpus folder contents.
2. Read each past proposal to find content relevant to the user's RFP question.
3. Draft a response for each question, grounding every claim in text from the
   proposals. Each QuestionResponse MUST have at least one citation with a
   chunk_id copied VERBATIM from a ``[chunk:...]`` marker.
4. Rate confidence: HIGH if directly supported by existing collateral,
   MEDIUM if partially supported, LOW if extrapolated.
5. Note gaps in ``overall_notes`` — areas where no past proposal has relevant
   content and a subject-matter expert should review.

Be specific and professional. Mirror the voice and level of detail found in
the past proposals.
"""


async def draft_rfp(
    *,
    question: str,
    corpus_folder_id: str,
    model: str,
) -> RFPDraft:
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
        system_prompt=SYSTEM.replace("__CORPUS_FOLDER_ID__", corpus_folder_id),
        output_type=RFPDraft,
    )
    draft: RFPDraft | None = None
    try:
        async with agent.run_mcp_servers():
            result = await agent.run(
                f"Draft responses to this RFP question:\n\n{question}"
            )
            draft = (
                getattr(result, "output", None)
                or getattr(result, "data", None)
                or result
            )  # type: ignore[assignment]
    except BaseExceptionGroup:
        pass
    if draft is None:
        raise RuntimeError(
            "Agent did not produce a result before the MCP session closed."
        )
    return draft
