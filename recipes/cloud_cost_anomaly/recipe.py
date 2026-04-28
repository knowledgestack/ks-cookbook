"""Cloud cost anomaly explainer — AWS CUR CSV → cited anomaly explanations.

Pain point: FinOps sees a $40k NAT-gateway spike; explaining it takes a
half day of Slack spelunking. This recipe scans the CUR extract, then asks
Knowledge Stack about cloud cost optimization patterns, deploy notes, and
runbooks to ground the likely cause and recommended action.

Framework: pydantic-ai. KS access via the knowledgestack-mcp stdio server.
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
    "You explain AWS cost anomalies. Knowledge Stack is your search "
    "backend; ask it natural-language questions about cloud cost "
    "optimization, your deploy notes, and your runbooks.\n\n"
    "Workflow:\n"
    "1. Scan the CUR extract for rows with significant month-over-month "
    "delta (e.g. >2x previous month, or >$1k absolute increase).\n"
    "2. For EACH anomaly, ask Knowledge Stack a specific question, e.g.:\n"
    "   • 'What does AWS Well-Architected say about NAT Gateway cost "
    "optimization?'\n"
    "   • 'How should I right-size an EC2 c6i.4xlarge that is over-"
    "utilized?'\n"
    "   • 'What runbook covers CloudWatch Logs ingestion spikes?'\n"
    "   Frame queries naturally. Never use folder UUIDs or path_part_id "
    "filters.\n"
    "3. search_knowledge returns hits with chunk_id and path_part_id; the "
    "text field is empty. Call read(path_part_id=<hit's path_part_id>) to "
    "get the chunk text. The trailing [chunk:<uuid>] marker is your "
    "citation.chunk_id (NEVER pass chunk_id to read; it 404s).\n"
    "4. Build likely_cause + recommended_action directly from the chunk "
    "text. If no chunk evidences a cause, set likely_cause='unknown — "
    "investigate' rather than guess.\n"
    "5. Populate every citation with chunk_id (verbatim from the marker), "
    "document_name (filename in read() output's metadata), and snippet "
    "(verbatim ≤240 chars from the chunk text)."
    """Output format (STRICT): Your final response is a single JSON object that matches the response schema exactly. Do NOT wrap it in an extra key like {'<ClassName>': ...} or {'result': ...}. Every required string field is a string, not a nested object. Every required nested model is included with all of its required fields populated. Never omit required fields; never add unspecified ones."""
)
async def run(period: str, cur_path: Path) -> None:
    data = cur_path.read_text()[:8000]
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={
            "KS_API_KEY": os.environ.get("KS_API_KEY", ""),
            "KS_BASE_URL": os.environ.get("KS_BASE_URL", ""),
        },
    )
    agent = Agent(
        model=f"openai:{os.environ.get('MODEL', 'gpt-4o')}",
        mcp_servers=[mcp],
        system_prompt=PROMPT,
        output_type=CostReport,
        retries=4,
        output_retries=4,
    )
    async with agent.run_mcp_servers():
        result = await agent.run(f"Period: {period}\n\nCUR extract:\n{data}")
    print(json.dumps(result.output.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--period", default="March 2026")
    p.add_argument(
        "--cur-file", type=Path, required=True, help="AWS Cost-and-Usage Report extract (CSV)."
    )
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.period, args.cur_file))


if __name__ == "__main__":
    main()
