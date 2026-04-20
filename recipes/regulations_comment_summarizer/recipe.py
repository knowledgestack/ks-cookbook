"""Regulations.gov comment summarizer — docket → cited theme summary.

Pain point: Regulatory affairs staff skim thousands of public comments on a
proposed rule. This recipe clusters comments from your ingested docket and
returns a cited theme summary with representative excerpts.

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

CORPUS = os.environ.get("GOV_FOLDER_ID", "ab926019-ac7a-579f-bfda-6c52a13c5f41")


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=240)


class Theme(BaseModel):
    theme: str = Field(..., max_length=160)
    stance: str = Field(..., pattern="^(support|oppose|mixed|neutral)$")
    representative_quote: str = Field(..., max_length=400)
    approximate_count: str = Field(..., max_length=60)
    citations: list[Citation] = Field(..., min_length=2, max_length=4)


class CommentSummary(BaseModel):
    docket_id: str
    total_comments_estimate: str
    themes: list[Theme] = Field(..., min_length=3, max_length=10)


PROMPT = (
    f"You summarize public comments on a docket from path_part_id={CORPUS}. "
    "Cluster themes, don't list. Every theme cites ≥2 real chunk_ids. Never "
    "invent numerical counts — say 'dozens' etc. if unsure."
)


async def run(docket_id: str) -> None:
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
                  mcp_servers=[mcp], system_prompt=PROMPT, result_type=CommentSummary)
    async with agent.run_mcp_servers():
        result = await agent.run(f"Docket: {docket_id}")
    print(json.dumps(result.data.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--docket-id", required=True, help="e.g. 'EPA-HQ-OAR-2026-0123'")
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.docket_id))


if __name__ == "__main__":
    main()
