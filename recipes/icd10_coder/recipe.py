"""ICD-10 coder — clinical note → cited ICD-10-CM code suggestions.

Pain point: Medical coders hand-map physician notes to ICD-10-CM. This recipe
reads a de-identified note and returns code candidates grounded in the
ICD-10 reference in your corpus (CMS publishes it publicly).

Framework: pydantic-ai. Tools: list_contents, search_knowledge, read.
Output: stdout (JSON).
"""

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio

CORPUS = os.environ.get("CLINICAL_FOLDER_ID", "ab926019-ac7a-579f-bfda-6c52a13c5f41")


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=240)


class CodeSuggestion(BaseModel):
    code: str = Field(..., pattern=r"^[A-Z][0-9][0-9A-Z](\.[0-9A-Z]{1,4})?$")
    description: str = Field(..., max_length=200)
    confidence: str = Field(..., pattern="^(low|medium|high)$")
    evidence_in_note: str = Field(..., max_length=300)
    citation: Citation


class CodingResult(BaseModel):
    primary: CodeSuggestion
    secondaries: list[CodeSuggestion] = Field(default_factory=list, max_length=10)


PROMPT = (
    "You suggest ICD-10-CM codes for a de-identified clinical note. Cite the "
    f"ICD-10 reference in path_part_id={CORPUS} for every code. Never invent "
    "codes. Low confidence → flag for human review."
)


async def run(note: str) -> None:
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
                  mcp_servers=[mcp], system_prompt=PROMPT, result_type=CodingResult)
    async with agent.run_mcp_servers():
        result = await agent.run(f"Clinical note:\n{note[:6000]}")
    print(json.dumps(result.data.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--note-file", type=Path, required=True,
                   help="Text file with de-identified clinical note.")
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.note_file.read_text()))


if __name__ == "__main__":
    main()
