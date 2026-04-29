"""pydantic-ai agent that produces a traceable contract redline grounded in two KS corpora."""

import os

from pydantic_ai import Agent
from pydantic_ai.usage import UsageLimits
from pydantic_ai.mcp import MCPServerStdio

from contract_redline.schema import RedlineMemo

SYSTEM_TEMPLATE = """\
You are a senior contracts attorney producing a redline of a counterparty
contract against the firm's negotiation playbook. Every proposed edit must
cite BOTH (a) the offending clause in the counterparty draft and (b) the
governing rule in the firm's playbook — each as a chunk UUID returned by MCP.

MANDATORY workflow:
1. Call ``list_contents`` with ``folder_id=__PLAYBOOK_FOLDER_ID__`` to
   enumerate the firm's playbook documents.
2. Call ``list_contents`` with ``folder_id=__DRAFT_FOLDER_ID__`` to enumerate
   the counterparty draft. Identify the document named ``__INBOUND_NAME__``
   (or the closest match).
3. Call ``read`` on the counterparty draft AND on each relevant playbook
   document using their UUID ``path_part_id`` values.
4. Every ``Citation.chunk_id`` MUST be copied verbatim from a
   ``[chunk:<uuid>]`` marker in ``read`` output.
5. For each proposed ``Redline``:
   - ``original_text`` must be an exact quote from the draft.
   - ``proposed_text`` must be send-ready language the attorney can paste.
   - ``risk_tier = blocker`` = cannot sign without this change;
     ``major`` = strong pushback; ``minor`` = negotiate if time permits;
     ``fallback`` = acceptable compromise if counterparty pushes back.
6. Do not invent rules. If the playbook is silent on an issue, do not emit a
   redline for it — note it in ``acceptable_as_is`` or omit.

KS workflow (do NOT skip):
1. Ask Knowledge Stack specific natural-language questions about the input. Never use folder UUIDs or path_part_id filters.
2. search_knowledge returns hits with chunk_id and path_part_id; the text field is empty by design. Call read(path_part_id=<hit's path_part_id>) to get chunk content. The trailing [chunk:<uuid>] marker is the citation chunk_id. NEVER pass chunk_id to read; it 404s.
3. Build every output field ONLY from chunk text you read. Never fabricate.
4. Populate every citation with chunk_id (verbatim from the marker), document_name (filename from read() metadata or materialized_path), snippet (verbatim ≤240 chars).

Output format (STRICT): Your final response is a single JSON object that matches the response schema exactly. Do NOT wrap it in an extra key like {'<ClassName>': ...} or {'result': ...}. Every required string field is a string, not a nested object. Every required nested model is included with all of its required fields populated. Never omit required fields; never add unspecified ones.
"""


async def produce_redline(
    *,
    playbook_folder_id: str,
    draft_folder_id: str,
    inbound_name: str,
    playbook_name: str,
    model: str,
) -> RedlineMemo:
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
    system = (
        SYSTEM_TEMPLATE.replace("__PLAYBOOK_FOLDER_ID__", playbook_folder_id)
        .replace("__DRAFT_FOLDER_ID__", draft_folder_id)
        .replace("__INBOUND_NAME__", inbound_name)
    )
    agent = Agent(
        model=f"openai:{model}",
        mcp_servers=[mcp],
        system_prompt=system,
        output_type=RedlineMemo,
        retries=4,
        output_retries=4,
    )
    prompt = (
        f"Playbook: {playbook_name}. Counterparty draft: {inbound_name}. "
        "Produce the full traceable redline memo."
    )
    async with agent.run_mcp_servers():
        result = await agent.run(prompt, usage_limits=UsageLimits(request_limit=200))
    return getattr(result, "output", None) or getattr(result, "data", None) or result  # type: ignore[return-value]
