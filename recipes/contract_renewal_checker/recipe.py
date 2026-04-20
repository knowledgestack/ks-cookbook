"""Contract renewal checker — contract → cited renewal summary + actions.

Pain point: Auto-renewals sneak up; notice windows get missed. This recipe
reads a contract, surfaces the renewal term, notice window, fee escalator,
and produces a calendar-ready action list with citations.

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
    "You check contract renewal terms. Extract term end, auto-renewal, notice "
    f"window, and fee escalator from path_part_id={CORPUS}. Produce calendar "
    "actions (e.g. 'send non-renewal notice by YYYY-MM-DD'). Cite real chunk_ids."
)


async def run(contract: str) -> None:
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
                  mcp_servers=[mcp], system_prompt=PROMPT, result_type=RenewalCheck)
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
