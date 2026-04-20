"""Force majeure impact — event type + contracts → cited impact assessment.

Pain point: When a regional outage, hurricane, or supplier failure hits, legal
needs to know fast which contracts have force-majeure language that applies,
what notice is required, and what the cure window is.

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


class ContractImpact(BaseModel):
    contract: str
    covers_event: bool
    notice_required: str = Field(..., max_length=240)
    cure_window: str = Field(..., max_length=120)
    termination_trigger: str = Field(..., max_length=240)
    citation: Citation


class ImpactReport(BaseModel):
    event: str
    contracts: list[ContractImpact] = Field(..., min_length=1, max_length=20)
    overall_advice: str = Field(..., max_length=600)


PROMPT = (
    "You assess force-majeure exposure. For each contract, read the FM clause "
    f"in path_part_id={CORPUS}. Decide whether the event is covered (is it "
    "listed? generic 'acts of God' clause?), the notice period, cure window, "
    "and termination trigger. Citations must be real chunk_ids."
)


async def run(event: str, contracts: list[str]) -> None:
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
                  mcp_servers=[mcp], system_prompt=PROMPT, result_type=ImpactReport)
    async with agent.run_mcp_servers():
        result = await agent.run(f"Event: {event}\nContracts: {contracts}")
    print(json.dumps(result.data.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--event", required=True, help="e.g. 'AWS us-east-1 outage 2026-03-11'")
    p.add_argument("--contracts", required=True, help="Comma-separated contract names.")
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.event, [c.strip() for c in args.contracts.split(",")]))


if __name__ == "__main__":
    main()
