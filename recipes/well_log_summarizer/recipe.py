"""Well-log / drilling-report summarizer — well ID → cited HSE + ops summary.

Pain point: Drilling engineers triage 100s of daily drilling reports and well
logs. This recipe scans your corpus (DOE OpenEnergy + SPE papers + state RRC
filings), pulls HSE events, equipment issues, and formation notes, and emits
a cited summary so hazards aren't buried in 40-page PDFs.

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

CORPUS = os.environ.get("ENERGY_FOLDER_ID", "ab926019-ac7a-579f-bfda-6c52a13c5f41")


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=240)


class WellEvent(BaseModel):
    event_type: str = Field(..., pattern="^(hse|equipment|formation|lost_time|other)$")
    description: str = Field(..., max_length=400)
    severity: str = Field(..., pattern="^(info|low|medium|high|critical)$")
    citation: Citation


class WellSummary(BaseModel):
    well_id: str
    operator: str = Field(..., max_length=200)
    depth_summary: str = Field(..., max_length=300)
    events: list[WellEvent] = Field(..., min_length=1, max_length=20)
    recommended_actions: list[str] = Field(..., min_length=1, max_length=6)


PROMPT = (
    "You summarize drilling reports + well logs. Pull HSE, equipment, and "
    f"formation events from path_part_id={CORPUS}. Severity must be evidenced. "
    "chunk_ids must be real — never fabricate."
)


async def run(well_id: str) -> None:
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
                  mcp_servers=[mcp], system_prompt=PROMPT, result_type=WellSummary)
    async with agent.run_mcp_servers():
        result = await agent.run(f"Well ID: {well_id}")
    print(json.dumps(result.data.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--well-id", required=True, help="API well number or operator well name.")
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.well_id))


if __name__ == "__main__":
    main()
