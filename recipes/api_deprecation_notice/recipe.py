"""API deprecation notice — endpoint → cited customer-facing deprecation notice.

Pain point: Deprecations are communicated inconsistently. This recipe produces
a standard notice: what's deprecated, why, migration path, timeline — cited
from your API reference and deprecation policy.

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

CORPUS = os.environ.get("ENG_DOCS_FOLDER_ID", "ab926019-ac7a-579f-bfda-6c52a13c5f41")


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=240)


class DeprecationNotice(BaseModel):
    endpoint: str
    deprecation_reason: str = Field(..., max_length=400)
    replacement: str = Field(..., max_length=200)
    sunset_date: str
    migration_steps: list[str] = Field(..., min_length=2, max_length=8)
    header_to_watch: str = Field(..., max_length=120,
                                 description="e.g. Sunset: <date>")
    citations: list[Citation] = Field(..., min_length=1, max_length=4)


PROMPT = (
    "You write API deprecation notices. Follow our deprecation policy's "
    f"minimum notice window and header convention from path_part_id={CORPUS}. "
    "Cite real chunk_ids."
)


async def run(endpoint: str, replacement: str, sunset: str) -> None:
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
                  mcp_servers=[mcp], system_prompt=PROMPT, result_type=DeprecationNotice)
    async with agent.run_mcp_servers():
        result = await agent.run(
            f"Endpoint: {endpoint}\nReplacement: {replacement}\nSunset: {sunset}"
        )
    print(json.dumps(result.data.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--endpoint", required=True, help="e.g. POST /v1/ingest")
    p.add_argument("--replacement", required=True, help="e.g. POST /v2/ingest")
    p.add_argument("--sunset", required=True, help="YYYY-MM-DD")
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.endpoint, args.replacement, args.sunset))


if __name__ == "__main__":
    main()
