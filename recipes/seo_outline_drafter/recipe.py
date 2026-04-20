"""SEO outline drafter — keyword → cited SEO outline (H1/H2, intent, FAQs).

Pain point: SEO teams write outlines by scraping SERPs; brand voice and proof
come later. This recipe seeds the outline from your own corpus so the draft
is brand-correct from minute one, with citations.

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


class FAQ(BaseModel):
    question: str = Field(..., max_length=200)
    short_answer: str = Field(..., max_length=300)
    citation: Citation


class SEOOutline(BaseModel):
    keyword: str
    search_intent: str = Field(..., pattern="^(informational|comparison|transactional|navigational)$")
    h1: str = Field(..., max_length=120)
    h2s: list[str] = Field(..., min_length=3, max_length=10)
    faqs: list[FAQ] = Field(..., min_length=2, max_length=6)
    internal_link_suggestions: list[str] = Field(default_factory=list, max_length=6)


PROMPT = (
    f"You draft SEO outlines. Match user intent. Pull H2 candidates, FAQs, and "
    f"internal-link anchors from path_part_id={CORPUS}. FAQs must cite "
    "real chunk_ids so answers are trustworthy."
)


async def run(keyword: str) -> None:
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
                  mcp_servers=[mcp], system_prompt=PROMPT, result_type=SEOOutline)
    async with agent.run_mcp_servers():
        result = await agent.run(f"Keyword: {keyword}")
    print(json.dumps(result.data.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--keyword", required=True)
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.keyword))


if __name__ == "__main__":
    main()
