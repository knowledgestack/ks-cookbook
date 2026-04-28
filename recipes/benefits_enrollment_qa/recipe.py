# pyright: reportMissingImports=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportUnknownParameterType=false, reportAny=false, reportAttributeAccessIssue=false, reportUnusedCallResult=false, reportCallIssue=false, reportGeneralTypeIssues=false, reportArgumentType=false, reportOptionalSubscript=false, reportReturnType=false, reportMissingTypeArgument=false, reportDeprecated=false, reportUnannotatedClassAttribute=false
"""Benefits enrollment Q&A — question → cited answer from SPDs + carrier docs.

Pain point: Open enrollment: employees ask the same 50 questions about HDHP
vs PPO, HSA rules, coverage abroad, dependent age cutoffs. This recipe asks
Knowledge Stack about the question and grounds the answer in real chunks
of your Summary Plan Descriptions / carrier docs.

Framework: pydantic-ai. KS access via the knowledgestack-mcp stdio server.
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


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=240)


class BenefitsAnswer(BaseModel):
    question: str
    answer: str = Field(..., max_length=1200)
    plan_specific: bool
    contact_for_edge_case: str = Field(..., max_length=200)
    citations: list[Citation] = Field(..., min_length=1, max_length=4)


PROMPT = (
    "You answer employee benefits questions for an HR team. Knowledge "
    "Stack is your search backend; it holds the company's Summary Plan "
    "Descriptions (SPDs), ERISA disclosures, and carrier reference docs.\n\n"
    "Workflow:\n"
    "1. Ask Knowledge Stack a specific natural-language question that "
    "matches the employee's question, e.g.:\n"
    "   • 'What is the dependent age cutoff for medical coverage under "
    "the PPO plan?'\n"
    "   • 'Are HSA contributions allowed if I'm enrolled in the HDHP "
    "plan?'\n"
    "   • 'Does the company SPD describe how COBRA coverage works after "
    "termination?'\n"
    "   Frame it the way you'd ask the benefits administrator. Never use "
    "folder UUIDs or path_part_id filters.\n"
    "2. search_knowledge returns ranked hits with chunk_id and "
    "path_part_id. The text field is empty by design — call "
    "read(path_part_id=<hit's path_part_id>) to retrieve the chunk text. "
    "The trailing [chunk:<uuid>] marker is the citation chunk_id "
    "(NEVER pass chunk_id to read; it 404s).\n"
    "3. Build the answer ONLY from the read() text. Never quote a number "
    "or rule that isn't in the chunk content. Set plan_specific=true if "
    "the answer depends on plan tier (PPO vs HDHP, etc.).\n"
    "4. Populate every citation with chunk_id (verbatim from the marker), "
    "document_name (filename from the read() output's metadata), and "
    "snippet (verbatim ≤240 chars from the chunk text).\n"
    "5. contact_for_edge_case: who the employee should reach if their "
    "case isn't covered (e.g. 'benefits@example.com' or 'HR Business "
    "Partner'). Default: 'HR Benefits team'."
    """Output format (STRICT): Your final response is a single JSON object that matches the response schema exactly. Do NOT wrap it in an extra key like {'<ClassName>': ...} or {'result': ...}. Every required string field is a string, not a nested object. Every required nested model is included with all of its required fields populated. Never omit required fields; never add unspecified ones."""
)
async def run(question: str) -> None:
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", ".venv/bin/ks-mcp"),
        args=(os.environ.get("KS_MCP_ARGS", "") or "").split(),
        env={
            "KS_API_KEY": os.environ.get("KS_API_KEY", ""),
            "KS_BASE_URL": os.environ.get("KS_BASE_URL", ""),
        },
    )
    agent = Agent(
        model=f"openai:{os.environ.get('MODEL', 'gpt-4o')}",
        mcp_servers=[mcp],
        system_prompt=PROMPT,
        output_type=BenefitsAnswer,
        retries=4,
        output_retries=4,
    )
    async with agent.run_mcp_servers():
        result = await agent.run(f"Employee question: {question}")
    print(json.dumps(result.output.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--question",
        required=True,
        help="Employee benefits question, e.g. 'When can I change my HSA contribution?'",
    )
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.question))


if __name__ == "__main__":
    main()
