"""Obligation tracker — contract → cited list of time-bound obligations.

Pain point: "We committed to a 99.9% SLA" — where? by when? to whom? Contracts
bury obligations in long paragraphs. This recipe pulls a flat, dated list of
obligations per contract with citations so you can load it into a tracker.

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


class Obligation(BaseModel):
    obligation: str = Field(..., max_length=300)
    owner: str = Field(..., max_length=80)
    counterparty: str = Field(..., max_length=120)
    due: str = Field(..., max_length=80, description="ISO date, relative, or 'ongoing'.")
    penalty_if_missed: str = Field(..., max_length=240)
    citation: Citation


class ObligationList(BaseModel):
    contract: str
    obligations: list[Obligation] = Field(..., min_length=1, max_length=40)


PROMPT = (
    "You extract every time-bound obligation from a contract: SLAs, reporting, "
    "notice periods, audit rights, data-deletion commitments, renewals. For "
    f"each, report owner (us or them), due, penalty, citation. Corpus: "
    f"path_part_id={CORPUS}. chunk_ids must come from read output."
)


async def run(contract: str) -> None:
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
                  mcp_servers=[mcp], system_prompt=PROMPT, result_type=ObligationList)
    async with agent.run_mcp_servers():
        result = await agent.run(f"Contract: {contract}")
    print(json.dumps(result.data.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--contract", required=True)
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.contract))


if __name__ == "__main__":
    main()
