"""Launch email variants — feature + audience → 3 cited email variants.

Pain point: Lifecycle writes three near-identical launch emails. This recipe
produces three *different* angles (value, proof, curiosity), each cited to a
product doc or case study, ready for A/B/C testing.

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


class Variant(BaseModel):
    angle: str = Field(..., pattern="^(value|proof|curiosity)$")
    subject: str = Field(..., max_length=80)
    preheader: str = Field(..., max_length=120)
    body: str = Field(..., max_length=1200)
    cta: str = Field(..., max_length=120)
    citations: list[Citation] = Field(..., min_length=1, max_length=3)


class LaunchEmails(BaseModel):
    feature: str
    audience: str
    variants: list[Variant] = Field(..., min_length=3, max_length=3)


PROMPT = (
    "You write launch emails with three distinct angles: value (what you get), "
    "proof (case/metric), curiosity (question hook). Ground each in real "
    f"chunk_ids from path_part_id={CORPUS}. Keep each body under 160 words."
)


async def run(feature: str, audience: str) -> None:
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
                  mcp_servers=[mcp], system_prompt=PROMPT, result_type=LaunchEmails)
    async with agent.run_mcp_servers():
        result = await agent.run(f"Feature: {feature}\nAudience: {audience}")
    print(json.dumps(result.data.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--feature", required=True)
    p.add_argument("--audience", default="existing customers, technical buyer")
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.feature, args.audience))


if __name__ == "__main__":
    main()
