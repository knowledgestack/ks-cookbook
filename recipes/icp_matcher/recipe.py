"""ICP matcher — score a prospect company against your Ideal Customer Profile.

Pain point: SDRs spend the first 20 minutes of every prospecting session
re-reading the ICP deck and guessing whether a company fits. This recipe
takes a company name + blurb and asks Knowledge Stack about your ICP
criteria, segmentation rules, and prior conversations — then emits a fit
score with cited hits/misses.

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


class CriterionHit(BaseModel):
    criterion: str = Field(..., max_length=120)
    verdict: str = Field(..., pattern="^(hit|miss|unclear)$")
    reason: str = Field(..., max_length=240)
    citations: list[Citation] = Field(..., min_length=1, max_length=3)


class ICPMatch(BaseModel):
    company: str
    fit_score: int = Field(..., ge=0, le=100)
    tier: str = Field(..., pattern="^(A|B|C|disqualified)$")
    criteria: list[CriterionHit] = Field(..., min_length=3, max_length=10)
    next_step: str = Field(..., max_length=240)


PROMPT = (
    "You're an SDR ops analyst scoring a prospect against your company's "
    "Ideal Customer Profile (ICP). Knowledge Stack is your search backend; "
    "ask it natural-language questions about your ICP criteria, "
    "segmentation rules, customer-success notes, and what works in similar "
    "deals.\n\n"
    "Workflow:\n"
    "1. Ask Knowledge Stack questions like:\n"
    "   • 'What are the company-size and industry criteria in our ICP for "
    "enterprise tier?'\n"
    "   • 'What disqualifies a prospect (regulated industries, "
    "competitor relationships, etc.)?'\n"
    "   • 'Have we had similar deals in <prospect's industry / size>?'\n"
    "   Frame queries naturally. Never use folder UUIDs or path_part_id "
    "filters.\n"
    "2. search_knowledge returns hits with chunk_id and path_part_id; the "
    "text field is empty. Call read(path_part_id=<hit's path_part_id>) to "
    "get the chunk text. The trailing [chunk:<uuid>] marker is your "
    "citation.chunk_id (NEVER pass chunk_id to read; it 404s).\n"
    "3. Build 3–10 CriterionHit entries directly from the chunk text. "
    "Each verdict (hit/miss/unclear) must be defensible by the citations.\n"
    "4. fit_score (0-100) → tier mapping: <40 disqualified, 40-65 C, "
    "65-80 B, >80 A.\n"
    "5. next_step: a concrete SDR action (e.g. 'Email VP Eng with use "
    "case 1', 'Skip — competitor reseller')."
    """Output format (STRICT): Your final response is a single JSON object that matches the response schema exactly. Do NOT wrap it in an extra key like {'<ClassName>': ...} or {'result': ...}. Every required string field is a string, not a nested object. Every required nested model is included with all of its required fields populated. Never omit required fields; never add unspecified ones."""
)
async def run(company: str, blurb: str) -> None:
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
        output_type=ICPMatch,
        retries=4,
        output_retries=4,
    )
    request = f"Prospect company: {company}\nBlurb: {blurb}"
    async with agent.run_mcp_servers():
        result = await agent.run(request)
    print(json.dumps(result.output.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--company", required=True)
    p.add_argument("--blurb", default="B2B SaaS, ~200 employees, US-based.")
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.company, args.blurb))


if __name__ == "__main__":
    main()
