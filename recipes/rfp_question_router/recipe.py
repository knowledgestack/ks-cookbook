"""RFP question router — RFP line → cited team owner + draft answer.

Pain point: RFP questions land in one big doc; half should go to Security,
half to Engineering, the rest to PMM. This recipe routes each question to the
right team and drafts a cited first answer from your corpus.

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

CORPUS = os.environ.get("RFP_FOLDER_ID", "ab926019-ac7a-579f-bfda-6c52a13c5f41")


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=240)


class RoutedAnswer(BaseModel):
    question: str
    owner_team: str = Field(..., pattern="^(Security|Engineering|Privacy|Legal|PMM|Support|Finance)$")
    confidence: str = Field(..., pattern="^(low|medium|high)$")
    draft_answer: str = Field(..., max_length=1200)
    needs_human_review_reason: str = Field(..., max_length=300)
    citations: list[Citation] = Field(..., min_length=1, max_length=4)


PROMPT = (
    "You route RFP questions. Decide owner team from question content. Draft "
    f"an answer grounded in path_part_id={CORPUS}. Flag confidence honestly; "
    "low confidence → human review. chunk_ids must be real."
)


async def run(question: str) -> None:
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
                  mcp_servers=[mcp], system_prompt=PROMPT, result_type=RoutedAnswer)
    async with agent.run_mcp_servers():
        result = await agent.run(f"RFP question: {question}")
    print(json.dumps(result.data.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--question", required=True)
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.question))


if __name__ == "__main__":
    main()
