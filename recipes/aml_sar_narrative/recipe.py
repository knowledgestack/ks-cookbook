"""AML SAR narrative writer — case → cited FinCEN-format SAR narrative.

Pain point: AML analysts hand-write 200-word Suspicious Activity Report
narratives in FinCEN's Who/What/When/Where/Why/How format. This recipe pulls
transaction summaries + alert rationale from your corpus and drafts a
compliant narrative with citations.

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

CORPUS = os.environ.get("AML_FOLDER_ID", "ab926019-ac7a-579f-bfda-6c52a13c5f41")


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=240)


class SARNarrative(BaseModel):
    case_id: str
    who: str = Field(..., max_length=400)
    what: str = Field(..., max_length=600)
    when: str = Field(..., max_length=240)
    where: str = Field(..., max_length=240)
    why_suspicious: str = Field(..., max_length=600)
    how: str = Field(..., max_length=600)
    narrative: str = Field(..., max_length=1600,
                           description="Combined ~200-word narrative paragraph.")
    citations: list[Citation] = Field(..., min_length=2, max_length=8)


PROMPT = (
    "You draft AML Suspicious Activity Report (SAR) narratives in FinCEN "
    "Who/What/When/Where/Why/How form. Ground every fact in "
    f"path_part_id={CORPUS} (transaction ledger exports, alert rationale, "
    "KYC notes). No speculation beyond what documents support. Keep the "
    "combined narrative ≤ ~200 words. chunk_ids must be real."
)


async def run(case_id: str) -> None:
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
                  mcp_servers=[mcp], system_prompt=PROMPT, result_type=SARNarrative)
    async with agent.run_mcp_servers():
        result = await agent.run(f"Case: {case_id}")
    print(json.dumps(result.data.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--case-id", required=True)
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.case_id))


if __name__ == "__main__":
    main()
