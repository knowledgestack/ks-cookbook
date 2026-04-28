"""Contract renewal checker — contract → cited renewal summary + actions.

Pain point: Auto-renewals sneak up; notice windows get missed. This recipe
asks Knowledge Stack about a named contract, extracts term end + renewal
mechanics + fee escalator, and emits a calendar-ready action list with
real citations into the contract document.

Framework: pydantic-ai. KS access via the knowledgestack-mcp stdio server.
Output: stdout (JSON).
"""

import argparse
import asyncio
import json
import os
import sys

from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=240)


class RenewalAction(BaseModel):
    do_by: str = Field(..., max_length=40)
    action: str = Field(..., max_length=200)


class RenewalCheck(BaseModel):
    contract: str
    term_end: str = Field(..., max_length=40)
    auto_renews: bool
    notice_window_days: int = Field(..., ge=0, le=365)
    fee_escalator: str = Field(..., max_length=160)
    actions: list[RenewalAction] = Field(..., min_length=1, max_length=6)
    citations: list[Citation] = Field(..., min_length=1, max_length=6)


PROMPT = (
    "You check contract renewal terms. Knowledge Stack is your search "
    "backend; you ask natural-language questions about the named contract.\n\n"
    "For the contract the user names, find:\n"
    " • term_end (effective expiration date)\n"
    " • auto_renews (does it automatically renew?)\n"
    " • notice_window_days (how many days before expiration must non-renewal "
    "be served)\n"
    " • fee_escalator (annual price increase formula or fixed %)\n\n"
    "Workflow:\n"
    "1. Ask Knowledge Stack specific questions about the contract, e.g.:\n"
    "   • 'When does the {company} agreement expire?'\n"
    "   • 'Does the {company} contract auto-renew, and what is the notice "
    "window for non-renewal?'\n"
    "   • 'What is the annual fee escalator in the {company} agreement?'\n"
    "   Always call search_knowledge — never use folder UUIDs or "
    "path_part_id filters.\n"
    "2. search_knowledge returns hits with chunk_id and path_part_id; the "
    "text field is empty by design. Call read(path_part_id=<hit's "
    "path_part_id>) to get the chunk text. The trailing [chunk:<uuid>] "
    "marker is your citation.chunk_id (NEVER pass chunk_id to read — it "
    "404s; only path_part_id is readable).\n"
    "3. Populate every citation with chunk_id, document_name (the filename "
    "in the read() output's metadata, e.g. 'aapl_def14a_2024_proxy.pdf'), "
    "and snippet (verbatim ≤240 chars from the chunk text).\n"
    "4. Compute calendar-ready actions: 'Send non-renewal notice by "
    "<term_end - notice_window_days>'. Use ISO dates.\n"
    "5. If a field is genuinely not stated in the contract, use a sentinel "
    "('TBD' for strings, 0 for notice_window_days, false for auto_renews) "
    "and explain in the action list."
    """Output format (STRICT): Your final response is a single JSON object that matches the response schema exactly. Do NOT wrap it in an extra key like {'<ClassName>': ...} or {'result': ...}. Every required string field is a string, not a nested object. Every required nested model is included with all of its required fields populated. Never omit required fields; never add unspecified ones."""
)
async def run(contract: str) -> None:
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={
            "KS_API_KEY": os.environ.get("KS_API_KEY", ""),
            "KS_BASE_URL": os.environ.get("KS_BASE_URL", ""),
        },
    )
    agent = Agent(
        model=f"openai:{os.environ.get('MODEL', 'gpt-4o')}",
        mcp_servers=[mcp],
        system_prompt=PROMPT,
        output_type=RenewalCheck,
        retries=4,
        output_retries=4,
    )
    async with agent.run_mcp_servers():
        result = await agent.run(f"Contract to check: {contract}")
    print(json.dumps(result.output.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--contract",
        required=True,
        help="Contract name or distinguishing keyword (e.g. company name).",
    )
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.contract))


if __name__ == "__main__":
    main()
