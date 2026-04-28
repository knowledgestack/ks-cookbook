"""Court-docket monitor — party + period → cited litigation activity summary.

Pain point: Legal + strategy teams want to know "has <competitor> been sued
in N.D. Cal. this quarter?" without paying for PACER monitoring. This
recipe asks Knowledge Stack about the named party's litigation in the
period and returns a cited summary.

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


class DocketEntry(BaseModel):
    case_caption: str = Field(..., max_length=240)
    court: str = Field(..., max_length=120)
    filed: str = Field(..., max_length=40)
    nature_of_suit: str = Field(..., max_length=120)
    role: str = Field(..., pattern="^(plaintiff|defendant|amicus|other)$")
    status: str = Field(..., max_length=120)
    citation: Citation


class DocketReport(BaseModel):
    party: str
    period: str
    entries: list[DocketEntry] = Field(default_factory=list, max_length=50)
    headline: str = Field(..., max_length=400)


PROMPT = (
    "You summarize litigation activity for a named party. Knowledge Stack "
    "is your search backend; ask it natural-language questions about the "
    "party's court filings, opinions, and dockets.\n\n"
    "Workflow:\n"
    "1. Ask Knowledge Stack questions like:\n"
    "   • 'What court opinions or dockets in the corpus involve <party>?'\n"
    "   • 'Has <party> been sued in <period>?'\n"
    "   • 'What is the nature of suit and case status for <party>'s "
    "matters?'\n"
    "   Frame queries naturally. Never use folder UUIDs or path_part_id "
    "filters.\n"
    "2. search_knowledge returns hits with chunk_id and path_part_id; the "
    "text field is empty. Call read(path_part_id=<hit's path_part_id>) to "
    "get the chunk text. The trailing [chunk:<uuid>] marker is your "
    "citation.chunk_id (NEVER pass chunk_id to read; it 404s).\n"
    "3. Build DocketEntry rows ONLY from chunks whose content actually "
    "names the party. Never invent case captions, courts, or dates.\n"
    "4. If no matter is documented, return entries=[] and a headline like "
    "'No litigation involving <party> in the corpus for <period>.'\n"
    "5. Populate every citation with chunk_id (verbatim), document_name "
    "(filename in read() metadata), and snippet (verbatim ≤240 chars)."
    """Output format (STRICT): Your final response is a single JSON object that matches the response schema exactly. Do NOT wrap it in an extra key like {'<ClassName>': ...} or {'result': ...}. Every required string field is a string, not a nested object. Every required nested model is included with all of its required fields populated. Never omit required fields; never add unspecified ones."""
)
async def run(party: str, period: str) -> None:
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
        output_type=DocketReport,
        retries=4,
        output_retries=4,
    )
    async with agent.run_mcp_servers():
        result = await agent.run(f"Party: {party}\nPeriod: {period}")
    print(json.dumps(result.output.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--party", required=True, help="Company or individual name.")
    p.add_argument("--period", default="Q1 2026")
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.party, args.period))


if __name__ == "__main__":
    main()
