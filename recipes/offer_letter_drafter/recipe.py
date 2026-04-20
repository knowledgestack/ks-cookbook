"""Offer letter drafter — candidate + role + comp → cited offer letter draft.

Pain point: Offer letters require consistent language pulled from comp bands,
benefits, IP/confidentiality, and country-specific templates. This recipe
produces a cited draft that follows your policy doc wording exactly.

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

CORPUS = os.environ.get("HR_FOLDER_ID", "ab926019-ac7a-579f-bfda-6c52a13c5f41")


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=240)


class OfferLetter(BaseModel):
    candidate: str
    role: str
    level: str
    base_salary: str
    equity: str = Field(..., max_length=200)
    benefits_summary: str = Field(..., max_length=600)
    body: str = Field(..., max_length=2400)
    citations: list[Citation] = Field(..., min_length=2, max_length=6)


PROMPT = (
    "You draft offer letters. Use the wording from our offer template, comp "
    f"band doc, and benefits summary in path_part_id={CORPUS}. Do not invent "
    "comp numbers — use the ones provided. Citations must be real chunk_ids."
)


async def run(candidate: str, role: str, level: str, base: str, equity: str) -> None:
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
                  mcp_servers=[mcp], system_prompt=PROMPT, result_type=OfferLetter)
    async with agent.run_mcp_servers():
        result = await agent.run(
            f"Candidate: {candidate}\nRole: {role}\nLevel: {level}\n"
            f"Base: {base}\nEquity: {equity}"
        )
    print(json.dumps(result.data.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--candidate", required=True)
    p.add_argument("--role", required=True)
    p.add_argument("--level", default="Senior")
    p.add_argument("--base", required=True)
    p.add_argument("--equity", default="per band")
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.candidate, args.role, args.level, args.base, args.equity))


if __name__ == "__main__":
    main()
