"""Insurance fraud-pattern detector — claim file → cited suspicion flags.

Pain point: SIU teams pattern-match claims against known fraud rings (same
repair shop + same attorney + same injury pattern). This recipe reads the
claim file and compares against your SIU playbook, flagging suspicions with
citations.

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

CORPUS = os.environ.get("INSURANCE_FOLDER_ID", "ab926019-ac7a-579f-bfda-6c52a13c5f41")


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=240)


class FraudFlag(BaseModel):
    pattern_name: str = Field(..., max_length=160)
    evidence: str = Field(..., max_length=500)
    severity: str = Field(..., pattern="^(low|medium|high)$")
    recommended_action: str = Field(..., pattern="^(pay|siu_review|deny|deeper_investigation)$")
    citation: Citation


class FraudReport(BaseModel):
    claim_id: str
    flags: list[FraudFlag] = Field(default_factory=list, max_length=15)
    overall_recommendation: str = Field(..., pattern="^(pay|siu_review|deny|deeper_investigation)$")


PROMPT = (
    "You review claims for fraud patterns against our SIU playbook in "
    f"path_part_id={CORPUS}. Only flag what the file + playbook support. "
    "Never fabricate providers, shops, or attorneys. chunk_ids must be real."
)


async def run(claim_id: str, file_text: str) -> None:
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
                  mcp_servers=[mcp], system_prompt=PROMPT, result_type=FraudReport)
    async with agent.run_mcp_servers():
        result = await agent.run(f"Claim: {claim_id}\n\nFile:\n{file_text[:6000]}")
    print(json.dumps(result.data.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--claim-id", required=True)
    p.add_argument("--file-text", required=True, help="Claim file summary (OCR or notes).")
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.claim_id, args.file_text))


if __name__ == "__main__":
    main()
