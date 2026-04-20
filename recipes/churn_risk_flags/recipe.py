"""Churn risk flags — customer → risk signals from QBRs, tickets, usage notes.

Pain point: CSMs don't know which accounts are quietly slipping until renewal
slips. This recipe surfaces cited risk signals (usage decline mentions, exec
sponsor loss, competitive evals) with severity + next action.

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


class RiskSignal(BaseModel):
    signal: str = Field(..., max_length=160)
    severity: str = Field(..., pattern="^(low|medium|high)$")
    evidence: str = Field(..., max_length=300)
    citations: list[Citation] = Field(..., min_length=1, max_length=3)


class ChurnReport(BaseModel):
    account: str
    overall_risk: str = Field(..., pattern="^(low|medium|high|critical)$")
    signals: list[RiskSignal] = Field(..., min_length=1, max_length=10)
    recommended_play: str = Field(..., max_length=300)


PROMPT = (
    f"You triage customer churn risk. Read QBRs, ticket digests, and CSM notes "
    f"in path_part_id={CORPUS}. Flag concrete signals — quote or paraphrase. "
    "Every signal must cite a real chunk_id from read output. Severity is high "
    "when exec sponsor lost, usage declining >30%, competitor mentioned by name, "
    "or unresolved escalation >14 days."
)


async def run(account: str) -> None:
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
                  mcp_servers=[mcp], system_prompt=PROMPT, result_type=ChurnReport)
    async with agent.run_mcp_servers():
        result = await agent.run(f"Account: {account}")
    print(json.dumps(result.data.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--account", required=True)
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.account))


if __name__ == "__main__":
    main()
