"""Runway scenario — scenario name → cited cash runway table with assumptions.

Pain point: FP&A rebuilds runway scenarios every board cycle. This recipe
reads the latest plan doc + actuals summary and produces a cited scenario
(baseline / downside / upside) with runway months.

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

CORPUS = os.environ.get("FINANCE_FOLDER_ID", "ab926019-ac7a-579f-bfda-6c52a13c5f41")


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=240)


class Assumption(BaseModel):
    driver: str
    value: str
    citation: Citation


class RunwayScenario(BaseModel):
    scenario: str = Field(..., pattern="^(baseline|downside|upside)$")
    starting_cash: str
    monthly_burn: str
    runway_months: int = Field(..., ge=0, le=120)
    assumptions: list[Assumption] = Field(..., min_length=3, max_length=12)


PROMPT = (
    "You build runway scenarios. Pull numbers from the latest plan doc and "
    f"actuals summary in path_part_id={CORPUS}. Do not fabricate figures. "
    "Cite the chunk_id for every assumption."
)


async def run(scenario: str) -> None:
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
                  mcp_servers=[mcp], system_prompt=PROMPT, result_type=RunwayScenario)
    async with agent.run_mcp_servers():
        result = await agent.run(f"Scenario: {scenario}")
    print(json.dumps(result.data.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--scenario", required=True, choices=["baseline", "downside", "upside"])
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.scenario))


if __name__ == "__main__":
    main()
