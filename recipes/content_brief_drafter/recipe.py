"""Content brief drafter — topic → cited content brief (audience, angle, proof).

Pain point: Writers get a topic and spin their wheels. This recipe produces a
cited brief: target audience, key angle, proof points (from your case studies,
product docs), and recommended structure.

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

CORPUS = os.environ.get("MARKETING_FOLDER_ID", "ab926019-ac7a-579f-bfda-6c52a13c5f41")


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=240)


class ContentBrief(BaseModel):
    topic: str
    audience: str = Field(..., max_length=200)
    angle: str = Field(..., max_length=300)
    key_messages: list[str] = Field(..., min_length=2, max_length=5)
    proof_points: list[str] = Field(..., min_length=2, max_length=6)
    outline: list[str] = Field(..., min_length=3, max_length=10)
    cta: str = Field(..., max_length=160)
    citations: list[Citation] = Field(..., min_length=2, max_length=6)


PROMPT = (
    f"You draft content briefs. Mine case studies, product docs, and past "
    f"winning content in path_part_id={CORPUS}. Proof points must cite "
    "real chunk_ids. Avoid vague adjectives; prefer specifics."
)


async def run(topic: str) -> None:
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
                  mcp_servers=[mcp], system_prompt=PROMPT, result_type=ContentBrief)
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
