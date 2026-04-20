"""HIPAA BAA gap — vendor BAA text → cited gap list vs HHS model BAA.

Pain point: Vendor BAAs vary wildly. Privacy/legal re-check every one against
our minimum terms. This recipe reads the vendor BAA (or your playbook) and
flags missing/weak clauses with citations.

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

CORPUS = os.environ.get("PRIVACY_FOLDER_ID", "ab926019-ac7a-579f-bfda-6c52a13c5f41")


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=240)


class BAAGap(BaseModel):
    clause: str = Field(..., max_length=120)
    status: str = Field(..., pattern="^(ok|weak|missing)$")
    excerpt: str = Field(..., max_length=400)
    required_language: str = Field(..., max_length=400)
    citation: Citation


class BAAReport(BaseModel):
    vendor: str
    gaps: list[BAAGap] = Field(..., min_length=1, max_length=20)
    recommendation: str = Field(..., pattern="^(sign|request_changes|do_not_sign)$")


PROMPT = (
    "You audit a vendor BAA vs our BAA playbook and HIPAA minimum terms "
    f"(breach notice 60 days, subcontractor flow-down, return/destroy on "
    f"termination, audit rights). Corpus: path_part_id={CORPUS}. chunk_ids real."
)


async def run(vendor: str) -> None:
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
                  mcp_servers=[mcp], system_prompt=PROMPT, result_type=BAAReport)
    async with agent.run_mcp_servers():
        result = await agent.run(f"Vendor: {vendor}")
    print(json.dumps(result.data.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--vendor", required=True)
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.vendor))


if __name__ == "__main__":
    main()
