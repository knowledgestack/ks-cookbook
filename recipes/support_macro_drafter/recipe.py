"""Support macro drafter — common ticket type → cited macro + escalation path.

Pain point: Support agents write the same reply 50 times before someone turns
it into a macro. This recipe produces a cited macro from your KB, plus the
escalation path for the edge cases.

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


class SupportMacro(BaseModel):
    ticket_type: str
    greeting: str = Field(..., max_length=120)
    body: str = Field(..., max_length=1400)
    when_to_use: str = Field(..., max_length=300)
    when_not_to_use: str = Field(..., max_length=300)
    escalation_path: list[str] = Field(..., min_length=1, max_length=5)
    citations: list[Citation] = Field(..., min_length=1, max_length=4)


PROMPT = (
    f"You write support macros. Ground answers in KB articles in "
    f"path_part_id={CORPUS}. Keep the body under ~180 words. Be explicit "
    "about when NOT to use the macro. chunk_ids must be real."
)


async def run(ticket_type: str) -> None:
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
                  mcp_servers=[mcp], system_prompt=PROMPT, result_type=SupportMacro)
    async with agent.run_mcp_servers():
        result = await agent.run(f"Ticket type: {ticket_type}")
    print(json.dumps(result.data.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--ticket-type", required=True,
                   help="e.g. 'API key rotation request'")
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.ticket_type))


if __name__ == "__main__":
    main()
