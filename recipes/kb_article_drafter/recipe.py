"""KB article drafter — topic → cited KB article in help-center style.

Pain point: KB debt grows; writers rebuild the same article from scratch. This
recipe mines product docs + past tickets to produce a structured KB article
(overview, prerequisites, steps, troubleshooting, related) with citations.

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

CORPUS = os.environ.get("KB_FOLDER_ID", "ab926019-ac7a-579f-bfda-6c52a13c5f41")


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=240)


class KBArticle(BaseModel):
    title: str
    overview: str = Field(..., max_length=500)
    prerequisites: list[str] = Field(default_factory=list, max_length=6)
    steps: list[str] = Field(..., min_length=2, max_length=12)
    troubleshooting: list[str] = Field(default_factory=list, max_length=6)
    related_articles: list[str] = Field(default_factory=list, max_length=6)
    citations: list[Citation] = Field(..., min_length=1, max_length=6)


PROMPT = (
    "You draft help-center KB articles. Voice: clear, imperative, no fluff. "
    f"Mine product docs and past resolutions in path_part_id={CORPUS}. "
    "chunk_ids must be real."
)


async def run(topic: str) -> None:
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
                  mcp_servers=[mcp], system_prompt=PROMPT, result_type=KBArticle)
    async with agent.run_mcp_servers():
        result = await agent.run(f"Topic: {topic}")
    print(json.dumps(result.data.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--topic", required=True)
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.topic))


if __name__ == "__main__":
    main()
