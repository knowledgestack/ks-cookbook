"""pydantic-ai agent that drafts a tone-matched invoice follow-up grounded in KS history."""

import os

from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio

from invoice_followup.schema import FollowUpDraft

SYSTEM_TEMPLATE = """\
You are a bookkeeper for a small business. Draft a follow-up email for an
overdue invoice. Tone MUST match the way this client has historically
communicated — not a generic template.

MANDATORY workflow:
1. Call ``find`` on the corpus ``folder_id=__CORPUS_FOLDER_ID__`` with the
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
        system_prompt=SYSTEM_TEMPLATE.replace("__CORPUS_FOLDER_ID__", corpus_folder_id),
        output_type=FollowUpDraft,
    )
    prompt = (
        f"Client: {client}. Overdue invoice: {invoice_number} "
        f"({days_overdue} days overdue). Draft the follow-up."
    )
    async with agent.run_mcp_servers():
        result = await agent.run(prompt)
    return getattr(result, "output", None) or getattr(result, "data", None) or result  # type: ignore[return-value]
