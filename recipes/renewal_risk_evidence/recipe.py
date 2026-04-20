"""Renewal risk evidence pack — customer + renewal date → cited evidence bundle.

Pain point: Renewal committees ask "what's the evidence this will or won't
renew?" and CSMs scramble. This recipe returns a structured evidence pack
(value realized, adoption, open risks, exec advocacy) with citations.

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

CORPUS = os.environ.get("CS_NOTES_FOLDER_ID", "ab926019-ac7a-579f-bfda-6c52a13c5f41")


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=240)


class EvidenceSection(BaseModel):
    title: str = Field(..., max_length=80)
    bullets: list[str] = Field(..., min_length=1, max_length=6)
    citations: list[Citation] = Field(..., min_length=1, max_length=4)


class RenewalEvidence(BaseModel):
    account: str
    renewal_date: str
    recommendation: str = Field(..., pattern="^(renew|expand|at_risk|likely_churn)$")
    value_realized: EvidenceSection
    adoption: EvidenceSection
    open_risks: EvidenceSection
    exec_advocacy: EvidenceSection


PROMPT = (
    "You build a renewal evidence pack for a commercial review. Read QBRs, "
    f"success-plan updates, and usage summaries in path_part_id={CORPUS}. "
    "Each section cites real chunk_ids from read output. Be explicit about "
    "what's supported vs what's missing."
)


async def run(account: str, renewal_date: str) -> None:
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
                  mcp_servers=[mcp], system_prompt=PROMPT, result_type=RenewalEvidence)
    async with agent.run_mcp_servers():
        result = await agent.run(f"Account: {account}\nRenewal: {renewal_date}")
    print(json.dumps(result.data.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--account", required=True)
    p.add_argument("--renewal-date", required=True, help="YYYY-MM-DD")
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.account, args.renewal_date))


if __name__ == "__main__":
    main()
