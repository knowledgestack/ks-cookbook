"""SAM.gov RFP match notifier — capability keywords → cited matching opportunities.

Pain point: GovCon BD teams scan SAM.gov daily for matching opportunities.
This recipe reads the ingested notices corpus and returns a ranked list of
matches with NAICS, response-by, and fit rationale.

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

CORPUS = os.environ.get("GOV_RFP_FOLDER_ID", "ab926019-ac7a-579f-bfda-6c52a13c5f41")


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=240)


class Opportunity(BaseModel):
    notice_id: str
    title: str = Field(..., max_length=240)
    agency: str = Field(..., max_length=160)
    naics: str
    response_by: str
    fit_score: int = Field(..., ge=0, le=100)
    rationale: str = Field(..., max_length=400)
    citation: Citation


class RFPMatchReport(BaseModel):
    capabilities: list[str]
    matches: list[Opportunity] = Field(..., min_length=1, max_length=15)


PROMPT = (
    f"You match GovCon opportunities. Read SAM.gov notices in "
    f"path_part_id={CORPUS}. Score fit only on evidenced scope overlap; never "
    "invent NAICS codes. chunk_ids must be real."
)


async def run(capabilities: list[str]) -> None:
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
                  mcp_servers=[mcp], system_prompt=PROMPT, result_type=RFPMatchReport)
    async with agent.run_mcp_servers():
        result = await agent.run(f"Capabilities: {capabilities}")
    print(json.dumps(result.data.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--capabilities", required=True,
                   help="Comma-separated, e.g. 'RAG,citations,PII redaction'.")
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run([c.strip() for c in args.capabilities.split(",")]))


if __name__ == "__main__":
    main()
