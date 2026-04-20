"""HOA compliance check — proposed change → cited HOA-doc verdict.

Pain point: Homeowners submit architectural change requests (new fence,
paint color, solar array) and the HOA board hunts through CC&Rs, bylaws, and
ACC guidelines. This recipe returns a cited verdict.

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

CORPUS = os.environ.get("REAL_ESTATE_FOLDER_ID", "ab926019-ac7a-579f-bfda-6c52a13c5f41")


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=240)


class HOAVerdict(BaseModel):
    requested_change: str
    verdict: str = Field(..., pattern="^(allowed|conditionally_allowed|prohibited|needs_variance)$")
    conditions: list[str] = Field(default_factory=list, max_length=6)
    rationale: str = Field(..., max_length=500)
    citations: list[Citation] = Field(..., min_length=1, max_length=4)


PROMPT = (
    f"You check HOA architectural requests vs CC&Rs, bylaws, and ACC "
    f"guidelines in path_part_id={CORPUS}. Cite real chunk_ids. Be literal — "
    "'paint must be from approved palette' is not the same as 'approved'."
)


async def run(change: str) -> None:
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
                  mcp_servers=[mcp], system_prompt=PROMPT, result_type=HOAVerdict)
    async with agent.run_mcp_servers():
        result = await agent.run(f"Requested change: {change}")
    print(json.dumps(result.data.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--change", required=True,
                   help="e.g. 'install 6kW rooftop solar, south-facing'")
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.change))


if __name__ == "__main__":
    main()
