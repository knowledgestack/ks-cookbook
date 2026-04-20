"""Vendor consolidation — category → cited consolidation plan.

Pain point: Procurement has 6 overlapping vendors in one category; nobody
remembers why. This recipe reads vendor contracts/notes and produces a
consolidation plan: keep / migrate / terminate, with annualized savings.

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

CORPUS = os.environ.get("FINANCE_FOLDER_ID", "ab926019-ac7a-579f-bfda-6c52a13c5f41")


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=240)


class VendorAction(BaseModel):
    vendor: str
    action: str = Field(..., pattern="^(keep|migrate|terminate|renegotiate)$")
    rationale: str = Field(..., max_length=400)
    annual_spend: str
    estimated_savings: str
    citation: Citation


class ConsolidationPlan(BaseModel):
    category: str
    vendors: list[VendorAction] = Field(..., min_length=2)
    overall_savings_estimate: str
    risks: list[str] = Field(default_factory=list, max_length=5)


PROMPT = (
    "You build vendor consolidation plans. Read vendor contracts, renewal "
    f"notes, and usage summaries in path_part_id={CORPUS}. Do not invent "
    "dollar figures — use what the docs say. Cite real chunk_ids."
)


async def run(category: str) -> None:
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
                  mcp_servers=[mcp], system_prompt=PROMPT, result_type=ConsolidationPlan)
    async with agent.run_mcp_servers():
        result = await agent.run(f"Category: {category}")
    print(json.dumps(result.data.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--category", required=True,
                   help="e.g. observability, CRM, contact-center")
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.category))


if __name__ == "__main__":
    main()
