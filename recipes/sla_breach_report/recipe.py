"""SLA breach report — customer + period → cited SLA breach summary + credits.

Pain point: Customer Success preps SLA credit calculations manually. This
recipe reads the MSA + SLA schedule, computes applicable credit per breach
reference, and cites policy.

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

CORPUS = os.environ.get("LEGAL_CORPUS_FOLDER_ID", "5fa0e0af-561c-5e4e-bfa3-2b66d0e40feb")


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=240)


class Breach(BaseModel):
    incident_ref: str = Field(..., max_length=80)
    metric: str = Field(..., max_length=80)
    target: str = Field(..., max_length=80)
    observed: str = Field(..., max_length=80)
    credit_pct: float = Field(..., ge=0, le=100)
    citation: Citation


class SLABreachReport(BaseModel):
    customer: str
    period: str
    breaches: list[Breach] = Field(default_factory=list, max_length=20)
    total_credit_pct: float = Field(..., ge=0, le=100)
    cap_applies: bool
    narrative: str = Field(..., max_length=800)


PROMPT = (
    f"You compute SLA credits. Read MSA + SLA schedule in path_part_id={CORPUS}. "
    "Apply caps. Every breach cites the exact SLA clause's chunk_id."
)


async def run(customer: str, period: str) -> None:
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
                  mcp_servers=[mcp], system_prompt=PROMPT, result_type=SLABreachReport)
    async with agent.run_mcp_servers():
        result = await agent.run(f"Customer: {customer}\nPeriod: {period}")
    print(json.dumps(result.data.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--customer", required=True)
    p.add_argument("--period", default="Q1 2026")
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.customer, args.period))


if __name__ == "__main__":
    main()
