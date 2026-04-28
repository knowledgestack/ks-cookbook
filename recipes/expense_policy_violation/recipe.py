"""Expense policy violation check — expense line → cited verdict.

Pain point: Finance reviewers eyeball expense reports against a 40-page T&E
policy. This recipe asks Knowledge Stack about the relevant policy /
guidance for the expense category and grounds the verdict in real chunks.

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


class ExpenseVerdict(BaseModel):
    description: str
    amount: str
    category: str
    verdict: str = Field(..., pattern="^(allowed|out_of_policy|needs_receipt|needs_approval)$")
    reason: str = Field(..., max_length=400)
    citations: list[Citation] = Field(..., min_length=1, max_length=3)


PROMPT = (
    "You're a finance reviewer assessing an expense line against your "
    "company's T&E policy. Knowledge Stack is your search backend; ask it "
    "natural-language questions about expense rules, receipt thresholds, "
    "and IRS deductibility guidance.\n\n"
    "Workflow:\n"
    "1. Ask Knowledge Stack questions like:\n"
    "   • 'What is the per-meal cap and receipt threshold in our T&E "
    "policy?'\n"
    "   • 'When is pre-approval required for travel expenses?'\n"
    "   • 'What does IRS Pub 535 say about deductibility of business "
    "entertainment?'\n"
    "   Frame queries naturally. Never use folder UUIDs or path_part_id "
    "filters.\n"
    "2. search_knowledge returns hits with chunk_id and path_part_id; the "
    "text field is empty. Call read(path_part_id=<hit's path_part_id>) to "
    "get the chunk text. The trailing [chunk:<uuid>] marker is your "
    "citation.chunk_id (NEVER pass chunk_id to read; it 404s).\n"
    "3. Verdict (one of allowed / out_of_policy / needs_receipt / "
    "needs_approval) must be defensible from the chunk text. Reason "
    "quotes the relevant rule verbatim where possible.\n"
    "4. Populate every citation with chunk_id (verbatim), document_name "
    "(filename in read() metadata), and snippet (verbatim ≤240 chars)."
    """Output format (STRICT): Your final response is a single JSON object that matches the response schema exactly. Do NOT wrap it in an extra key like {'<ClassName>': ...} or {'result': ...}. Every required string field is a string, not a nested object. Every required nested model is included with all of its required fields populated. Never omit required fields; never add unspecified ones."""
)
async def run(description: str, amount: str, category: str) -> None:
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={
            "KS_API_KEY": os.environ.get("KS_API_KEY", ""),
            "KS_BASE_URL": os.environ.get("KS_BASE_URL", ""),
        },
    )
    agent = Agent(
        model=f"openai:{os.environ.get('MODEL', 'gpt-4o')}",
        mcp_servers=[mcp],
        system_prompt=PROMPT,
        output_type=ExpenseVerdict,
        retries=4,
        output_retries=4,
    )
    async with agent.run_mcp_servers():
        result = await agent.run(
            f"Description: {description}\nAmount: {amount}\nCategory: {category}"
        )
    print(json.dumps(result.output.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--description", required=True)
    p.add_argument("--amount", required=True)
    p.add_argument("--category", required=True, help="e.g. meals, travel, entertainment")
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.description, args.amount, args.category))


if __name__ == "__main__":
    main()
