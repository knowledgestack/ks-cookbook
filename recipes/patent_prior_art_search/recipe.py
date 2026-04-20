"""Patent prior-art search — claim text → cited prior-art candidates.

Pain point: Patent counsel manually searches USPTO / EPO filings for prior
art; the first pass is mechanical. This recipe searches your ingested patent
corpus, scores candidate references by relevance, and cites the exact chunks
that overlap with the claim.

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

CORPUS = os.environ.get("PATENTS_FOLDER_ID", "ab926019-ac7a-579f-bfda-6c52a13c5f41")


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=240)


class PriorArtCandidate(BaseModel):
    reference: str = Field(..., max_length=200,
                           description="e.g. US-10,123,456-B2 or EP-3,123,456-A1")
    filing_date: str = Field(..., max_length=40)
    relevance: str = Field(..., pattern="^(weak|moderate|strong|anticipating)$")
    overlap_rationale: str = Field(..., max_length=500)
    citation: Citation


class PriorArtReport(BaseModel):
    claim_under_review: str
    candidates: list[PriorArtCandidate] = Field(..., min_length=1, max_length=15)
    novelty_risk: str = Field(..., pattern="^(low|medium|high)$")


PROMPT = (
    f"You search prior art. Compare the claim to USPTO/EPO references in "
    f"path_part_id={CORPUS}. 'anticipating' only if the reference discloses "
    "every element of the claim. chunk_ids must be real."
)


async def run(claim: str) -> None:
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
                  mcp_servers=[mcp], system_prompt=PROMPT, result_type=PriorArtReport)
    async with agent.run_mcp_servers():
        result = await agent.run(f"Claim: {claim}")
    print(json.dumps(result.data.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--claim", required=True, help="Text of the claim under review.")
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.claim))


if __name__ == "__main__":
    main()
