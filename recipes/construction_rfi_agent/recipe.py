"""Construction RFI / submittal agent — RFI text → cited draft response.

Pain point: RFIs (Requests For Information) pile up on jobsites; answering
each one means cross-referencing CSI MasterFormat specs, ASHRAE + FHWA
standards, drawings, and prior submittals. This recipe drafts a cited first
pass so the PM only spends time on the ambiguous ones.

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

CORPUS = os.environ.get("CONSTRUCTION_FOLDER_ID", "ab926019-ac7a-579f-bfda-6c52a13c5f41")


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=240)


class RFIDraft(BaseModel):
    rfi_number: str
    subject: str = Field(..., max_length=240)
    spec_section: str = Field(..., max_length=120,
                              description="e.g. CSI MasterFormat division (23 05 93).")
    draft_response: str = Field(..., max_length=1400)
    schedule_impact_days: int = Field(..., ge=0, le=90)
    cost_impact: str = Field(..., max_length=200)
    needs_architect_response: bool
    citations: list[Citation] = Field(..., min_length=1, max_length=5)


PROMPT = (
    "You draft construction RFI responses. Reference CSI MasterFormat, "
    f"ASHRAE / FHWA standards, drawings, and prior submittals in "
    f"path_part_id={CORPUS}. Flag if the architect-of-record must respond "
    "(design-intent questions). chunk_ids must be real."
)


async def run(rfi_number: str, text: str) -> None:
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
                  mcp_servers=[mcp], system_prompt=PROMPT, result_type=RFIDraft)
    async with agent.run_mcp_servers():
        result = await agent.run(f"RFI {rfi_number}:\n{text}")
    print(json.dumps(result.data.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--rfi-number", required=True)
    p.add_argument("--text", required=True, help="The RFI question body.")
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.rfi_number, args.text))


if __name__ == "__main__":
    main()
