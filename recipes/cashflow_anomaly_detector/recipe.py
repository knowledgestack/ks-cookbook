"""Cash-flow anomaly detector — bank CSV path → cited anomaly list.

Pain point: Controllers reconcile bank statements line by line and miss
unusual patterns (duplicate vendors, weekend ACH bursts, above-threshold cash).
This recipe cross-references transactions with your AP/AR notes corpus and
surfaces cited anomalies.

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

CORPUS = os.environ.get("FINANCE_FOLDER_ID", "ab926019-ac7a-579f-bfda-6c52a13c5f41")


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=240)


class Anomaly(BaseModel):
    pattern: str = Field(..., max_length=160)
    example_lines: list[str] = Field(..., min_length=1, max_length=5)
    severity: str = Field(..., pattern="^(info|low|medium|high)$")
    suggested_control: str = Field(..., max_length=300)
    citations: list[Citation] = Field(..., min_length=1, max_length=3)


class AnomalyReport(BaseModel):
    source_csv: str
    anomalies: list[Anomaly] = Field(..., min_length=1, max_length=15)


PROMPT = (
    f"You review bank CSV exports for anomalies. Cross-reference AP/AR notes "
    f"and expense policy in path_part_id={CORPUS}. Flag duplicate vendors, "
    "atypical cadence, above-threshold cash, and policy violations. Cite real "
    "chunk_ids for each suggested control."
)


async def run(csv_path: Path) -> None:
    txns = csv_path.read_text()[:8000]
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
                  mcp_servers=[mcp], system_prompt=PROMPT, result_type=AnomalyReport)
    async with agent.run_mcp_servers():
        result = await agent.run(f"Source: {csv_path.name}\n\nTransactions:\n{txns}")
    print(json.dumps(result.data.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--csv", type=Path, required=True, help="Path to bank transaction CSV.")
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.csv))


if __name__ == "__main__":
    main()
