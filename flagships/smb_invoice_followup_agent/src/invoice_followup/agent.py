"""pydantic-ai agent that drafts a tone-matched invoice follow-up grounded in KS history."""

import os

from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio
from pydantic_ai.usage import UsageLimits

from invoice_followup.schema import FollowUpDraft

SYSTEM_TEMPLATE = """\
You are a bookkeeper for a small business. Draft a follow-up email for an
overdue invoice. Tone MUST match the way this client has historically
communicated — not a generic template.

MANDATORY workflow:
1. Call ``find`` on the corpus ``folder_id=your tenant (use search_knowledge — no folder_id needed)`` with the
   client name to locate past invoices, prior follow-ups, and inbound client
   emails.
2. Call ``read`` on the most recent prior email exchange with this client
   AND on the overdue invoice itself (if present), using the UUID
   ``path_part_id`` values.
3. Observe: does the client use first names, formal salutations, emoji,
   short paragraphs, casual sign-offs? Record 1-4 concrete tone observations
   in ``tone_analysis``, each citing a chunk UUID.
4. Every ``Citation.chunk_id`` MUST be copied verbatim from a
   ``[chunk:<uuid>]`` marker. Do NOT synthesize.
5. Draft ``subject`` + ``body``:
   - Reference the specific invoice number and days overdue.
   - Match the tone observations you recorded.
   - End with a clear call to action and a polite offer to resolve any
     issue.
6. ``suggested_send_hour_local`` should reflect when the client has
   historically responded (e.g. morning vs end-of-day). If unknown, use 9.

Do not fabricate amounts, dates, or prior interactions.

KS workflow (do NOT skip):
1. Ask Knowledge Stack specific natural-language questions about the input. Never use folder UUIDs or path_part_id filters.
2. search_knowledge returns hits with chunk_id and path_part_id; the text field is empty by design. Call read(path_part_id=<hit's path_part_id>) to get chunk content. The trailing [chunk:<uuid>] marker is the citation chunk_id. NEVER pass chunk_id to read; it 404s.
3. Build every output field ONLY from chunk text you read. Never fabricate.
4. Populate every citation with chunk_id (verbatim from the marker), document_name (filename from read() metadata or materialized_path), snippet (verbatim ≤240 chars).

Output format (STRICT): Your final response is a single JSON object that matches the response schema exactly. Do NOT wrap it in an extra key like {'<ClassName>': ...} or {'result': ...}. Every required string field is a string, not a nested object. Every required nested model is included with all of its required fields populated. Never omit required fields; never add unspecified ones.
"""


async def draft_followup(
    *,
    client: str,
    invoice_number: str,
    days_overdue: int,
    corpus_folder_id: str,
    model: str,
) -> FollowUpDraft:
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
        output_type=FollowUpDraft,
        retries=4,
        output_retries=4,
    )
    prompt = (
        f"Client: {client}. Overdue invoice: {invoice_number} "
        f"({days_overdue} days overdue). Draft the follow-up."
    )
    async with agent.run_mcp_servers():
        result = await agent.run(prompt, usage_limits=UsageLimits(request_limit=200))
    return getattr(result, "output", None) or getattr(result, "data", None) or result  # type: ignore[return-value]
