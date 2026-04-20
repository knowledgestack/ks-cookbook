"""Meeting notes → cited action items / decisions / risks.

Pain point: after every meeting someone has to turn the transcript into a
shared doc of decisions + action items + risks, usually ~20 minutes of
copy-paste, and half the items drop because nobody owns them.

This recipe reads the transcript (plus any linked prep docs) from KS and
emits a structured summary with owners, due dates (if mentioned), and
citations. No owner invented that isn't named in the source.

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

CORPUS = os.environ.get("MEETINGS_FOLDER_ID", "ab926019-ac7a-579f-bfda-6c52a13c5f41")


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=240)


class ActionItem(BaseModel):
    task: str = Field(..., max_length=300)
    owner: str = Field(..., max_length=80, description="Name or '<unassigned>' — never invent an owner.")
    due: str = Field(..., max_length=40, description="ISO date, phrase like 'next sprint', or 'unspecified'.")
    citation: Citation


class Decision(BaseModel):
    decision: str = Field(..., max_length=400)
    rationale: str = Field(..., max_length=400)
    citation: Citation


class Risk(BaseModel):
    risk: str = Field(..., max_length=300)
    severity: str = Field(..., pattern="^(low|medium|high)$")
    citation: Citation


class MeetingSummary(BaseModel):
    meeting_id: str
    attendees: list[str] = Field(..., min_length=1, max_length=30)
    tl_dr: str = Field(..., max_length=600)
    decisions: list[Decision] = Field(default_factory=list, max_length=15)
    action_items: list[ActionItem] = Field(..., min_length=1, max_length=25)
    risks: list[Risk] = Field(default_factory=list, max_length=10)
    open_questions: list[str] = Field(default_factory=list, max_length=10)


PROMPT = (
    "You turn meeting transcripts into actionable summaries. Find the transcript "
    f"in folder_id={CORPUS} (call list_contents + read). Extract decisions, "
    "action items, risks, and open questions. Only assign an owner if a named "
    "person in the transcript took the item — otherwise use '<unassigned>'. "
    "chunk_ids MUST be copied verbatim from [chunk:<uuid>] markers in read output."
)


async def run(meeting_id: str) -> None:
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
                  mcp_servers=[mcp], system_prompt=PROMPT, result_type=MeetingSummary)
    async with agent.run_mcp_servers():
        result = await agent.run(f"Meeting ID: {meeting_id}")
    print(json.dumps(result.data.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--meeting-id", required=True, help="Filename or identifier of the transcript doc.")
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.meeting_id))


if __name__ == "__main__":
    main()
