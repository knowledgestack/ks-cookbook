"""Cloud cost anomaly explainer — AWS CUR CSV → cited anomaly explanations.

Pain point: FinOps sees a $40k NAT-gateway spike; explaining it takes a half
day of Slack spelunking. This recipe reads the CUR extract, pairs anomalies
with change notes + runbook entries from your corpus, and cites the likely
cause.

Framework: pydantic-ai. Tools: list_contents, search_knowledge, read.
Output: stdout (JSON).
"""

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio

CORPUS = os.environ.get("FINOPS_FOLDER_ID", "ab926019-ac7a-579f-bfda-6c52a13c5f41")


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=240)


class CostAnomaly(BaseModel):
    service: str
    usage_type: str
    delta: str
    likely_cause: str = Field(..., max_length=400)
    recommended_action: str = Field(..., max_length=300)
    citation: Citation


class CostReport(BaseModel):
    period: str
    anomalies: list[CostAnomaly] = Field(..., min_length=1, max_length=15)


PROMPT = (
    f"You explain AWS cost anomalies using deploy notes + runbooks in "
    f"path_part_id={CORPUS}. If no matching change note exists, say "
    "'unknown — investigate' rather than guess. chunk_ids must be real."
)


async def run(period: str, cur_path: Path) -> None:
    data = cur_path.read_text()[:8000]
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
                  mcp_servers=[mcp], system_prompt=PROMPT, result_type=CostReport)
    async with agent.run_mcp_servers():
        result = await agent.run(f"Period: {period}\n\nCUR extract:\n{data}")
    print(json.dumps(result.data.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--period", default="March 2026")
    p.add_argument("--cur-file", type=Path, required=True,
                   help="AWS Cost-and-Usage Report extract (CSV).")
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.period, args.cur_file))


if __name__ == "__main__":
    main()
