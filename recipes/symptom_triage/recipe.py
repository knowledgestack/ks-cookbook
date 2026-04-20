"""Symptom triage — patient-reported symptoms → cited triage bucket.

Pain point: Front-desk intake routes patients to the right level of care
(self-care / telehealth / same-day / urgent / ED). This recipe returns a
cited triage per your protocol corpus. Not a diagnosis tool.

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

CORPUS = os.environ.get("CLINICAL_FOLDER_ID", "ab926019-ac7a-579f-bfda-6c52a13c5f41")


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=240)


class TriageOutcome(BaseModel):
    presenting_symptoms: str
    red_flags: list[str] = Field(default_factory=list, max_length=6)
    disposition: str = Field(..., pattern="^(self_care|telehealth|same_day|urgent_care|ed_now)$")
    time_to_care: str = Field(..., max_length=120)
    rationale: str = Field(..., max_length=500)
    citations: list[Citation] = Field(..., min_length=1, max_length=4)
    disclaimer: str = Field(default="Decision-support only; not a diagnosis.")


PROMPT = (
    "You triage patient-reported symptoms per clinical protocols in "
    f"path_part_id={CORPUS}. Any red flag → ED. Cite real chunk_ids. Always "
    "include the decision-support disclaimer."
)


async def run(symptoms: str) -> None:
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
                  mcp_servers=[mcp], system_prompt=PROMPT, result_type=TriageOutcome)
    async with agent.run_mcp_servers():
        result = await agent.run(f"Symptoms: {symptoms}")
    print(json.dumps(result.data.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--symptoms", required=True)
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.symptoms))


if __name__ == "__main__":
    main()
