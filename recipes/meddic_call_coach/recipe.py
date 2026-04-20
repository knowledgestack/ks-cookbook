"""MEDDIC call coach — call transcript → cited MEDDIC coverage + gaps.

Pain point: AEs miss MEDDIC fields on discovery calls (Metrics, Economic
buyer, Decision criteria, Decision process, Identify pain, Champion). This
recipe scores coverage from the transcript and flags gaps with citations to
your sales playbook.

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

CORPUS = os.environ.get("SALES_NOTES_FOLDER_ID", "ab926019-ac7a-579f-bfda-6c52a13c5f41")


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=240)


class MEDDICField(BaseModel):
    field: str = Field(..., pattern="^(metrics|economic_buyer|decision_criteria|decision_process|identify_pain|champion)$")
    coverage: str = Field(..., pattern="^(missing|partial|strong)$")
    evidence_in_call: str = Field(..., max_length=400)
    followup_question: str = Field(..., max_length=240)
    citation: Citation


class MEDDICReport(BaseModel):
    call: str
    fields: list[MEDDICField] = Field(..., min_length=6, max_length=6)
    overall_grade: str = Field(..., pattern="^(A|B|C|D)$")
    top_3_followups: list[str] = Field(..., min_length=1, max_length=3)


PROMPT = (
    f"You coach discovery calls against MEDDIC. Use the playbook in "
    f"path_part_id={CORPUS} for what 'strong' looks like per field. Every "
    "field cites a real chunk_id + transcript moment."
)


async def run(call_name: str, transcript_file: Path) -> None:
    text = transcript_file.read_text()[:10000]
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
                  mcp_servers=[mcp], system_prompt=PROMPT, result_type=MEDDICReport)
    async with agent.run_mcp_servers():
        result = await agent.run(f"Call: {call_name}\n\nTranscript:\n{text}")
    print(json.dumps(result.data.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--call-name", required=True)
    p.add_argument("--transcript-file", type=Path, required=True)
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.call_name, args.transcript_file))


if __name__ == "__main__":
    main()
