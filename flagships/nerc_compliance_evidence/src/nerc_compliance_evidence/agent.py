"""pydantic-ai agent that builds NERC CIP compliance evidence packs."""

import os

from pydantic_ai import Agent
from pydantic_ai.usage import UsageLimits
from pydantic_ai.mcp import MCPServerStdio

from nerc_compliance_evidence.schema import NERCEvidencePack

SYSTEM = """\
You are a NERC CIP compliance analyst building an evidence pack for an
upcoming audit. The NERC CIP standards and the utility's cybersecurity
procedures are stored in Knowledge Stack.

MANDATORY workflow — use ONLY these two tools:
1. ``list_contents(folder_id=your tenant (use search_knowledge — no folder_id needed))`` — enumerate the corpus.
2. ``read(path_part_id=<UUID>, max_chars=8000)`` — read a document.
   Each passage ends with an inline ``[chunk:<uuid>]`` marker.

IMPORTANT: Do NOT call ``search_knowledge``, ``search_keyword``, ``find``,
``read_around``, or ``get_info``. Only use ``list_contents`` and ``read``.

Use the UUID path_part_id values from list_contents — NOT document names.

INSTRUCTIONS:
1. List the corpus folder to find the NERC CIP standard and the utility's
   procedures document.
2. Read the standard document to find the specific requirement text for the
   requested standard ID and requirement number.
3. Read the utility's procedures to find evidence that addresses each
   sub-requirement or control objective.
4. For each evidence item, cite the specific procedure that satisfies the
   requirement. Copy chunk_ids VERBATIM from ``[chunk:...]`` markers.
5. Mark items as SATISFIED, PARTIAL, GAP, or NOT_APPLICABLE.
6. List any compliance gaps where procedures do not adequately address the
   requirement.
7. Provide auditor notes summarizing the overall compliance posture.
"""


async def build_evidence_pack(
    *,
    standard: str,
    requirement: str,
    corpus_folder_id: str,
    model: str,
) -> NERCEvidencePack:
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
        system_prompt=SYSTEM,
        output_type=NERCEvidencePack,
        retries=4,
        output_retries=4,
    )
    pack: NERCEvidencePack | None = None
    try:
        async with agent.run_mcp_servers():
            result = await agent.run(f"Build a compliance evidence pack for NERC {standard} "
                f"requirement {requirement}."
            , usage_limits=UsageLimits(request_limit=200))
            pack = (
                getattr(result, "output", None)
                or getattr(result, "data", None)
                or result
            )  # type: ignore[assignment]
    except BaseExceptionGroup:
        pass
    if pack is None:
        raise RuntimeError(
            "Agent did not produce a result before the MCP session closed."
        )
    return pack
