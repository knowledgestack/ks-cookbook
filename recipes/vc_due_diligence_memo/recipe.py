"""VC due-diligence memo — company + data room → cited IC memo.

Pain point: a VC associate spends a week turning a data room into a
partner-ready investment-committee memo (team / market / product / traction
/ competition / terms / risks). This recipe reads the data room from KS
and emits the structured memo with citations for every fact.

Framework: pydantic-ai. Tools: list_contents, search_knowledge, read.
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

CORPUS = os.environ.get("VC_DATAROOM_FOLDER_ID", "ab926019-ac7a-579f-bfda-6c52a13c5f41")


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=240)


class Finding(BaseModel):
    claim: str = Field(..., max_length=400)
    citation: Citation


class Risk(BaseModel):
    risk: str = Field(..., max_length=300)
    severity: str = Field(..., pattern="^(low|medium|high|deal_breaker)$")
    citation: Citation


class DiligenceMemo(BaseModel):
    company: str
    round_: str = Field(..., alias="round", max_length=40)
    recommendation: str = Field(..., pattern="^(pass|track|diligence_deeper|ic_yes)$")
    tl_dr: str = Field(..., max_length=600)
    team: list[Finding] = Field(..., min_length=1, max_length=6)
    market: list[Finding] = Field(..., min_length=1, max_length=6)
    product: list[Finding] = Field(..., min_length=1, max_length=6)
    traction: list[Finding] = Field(..., min_length=1, max_length=6)
    competition: list[Finding] = Field(default_factory=list, max_length=6)
    terms_and_structure: list[Finding] = Field(default_factory=list, max_length=6)
    risks: list[Risk] = Field(..., min_length=1, max_length=10)

    class Config:
        populate_by_name = True


PROMPT = (
    "You are a VC associate drafting an IC memo. Read the data room in "
    f"folder_id={CORPUS} (list_contents + read). Cover team, market, product, "
    "traction, competition, terms, risks. Use ONLY facts in the corpus — if a "
    "category has no evidence, return an empty list rather than speculating. "
    "chunk_ids MUST be copied verbatim from [chunk:<uuid>] markers in read output."
)


async def run(company: str, round_: str) -> None:
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
                  mcp_servers=[mcp], system_prompt=PROMPT, result_type=DiligenceMemo)
    async with agent.run_mcp_servers():
        result = await agent.run(f"Company: {company}. Round: {round_}.")
    print(json.dumps(result.data.model_dump(by_alias=True), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--company", required=True)
    p.add_argument("--round", dest="round_", required=True, help="e.g. 'Seed', 'Series A'")
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.company, args.round_))


if __name__ == "__main__":
    main()
