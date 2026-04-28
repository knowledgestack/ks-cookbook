# pyright: reportMissingImports=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportUnknownParameterType=false, reportAny=false, reportAttributeAccessIssue=false, reportUnusedCallResult=false, reportCallIssue=false, reportGeneralTypeIssues=false, reportArgumentType=false, reportOptionalSubscript=false, reportReturnType=false, reportMissingTypeArgument=false, reportDeprecated=false, reportUnannotatedClassAttribute=false
"""Clause extractor — contract name → cited inventory of standard clauses.

Pain point: Legal ops needs to know "does this contract have a limitation of
liability cap? indemnity? IP assignment? auto-renew?" across hundreds of
documents. This recipe runs against your Knowledge Stack tenant — drop your
contracts in via the KS UI, then run this and you get a structured clause
inventory grounded in real chunk citations.

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

CLAUSES = [
    "limitation of liability",
    "indemnification",
    "intellectual property assignment",
    "auto-renewal",
    "termination for convenience",
    "governing law",
    "confidentiality",
    "data processing",
    "warranty disclaimer",
    "force majeure",
    "assignment",
    "notices",
]


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=240)


class ClauseHit(BaseModel):
    clause: str
    present: bool
    excerpt: str = Field(..., max_length=400)
    citation: Citation


class ClauseInventory(BaseModel):
    contract: str
    clauses: list[ClauseHit] = Field(..., min_length=3)


PROMPT = (
    "You inventory standard contract clauses for the user's company. Knowledge "
    "Stack is your search backend; you ask it questions in natural language.\n\n"
    f"Target clauses: {CLAUSES}\n\n"
    "Workflow — for each clause, ask Knowledge Stack a real question about "
    "the company / document the user named, then cite what comes back:\n\n"
    "1. Call search_knowledge with a specific natural-language question, "
    "e.g.:\n"
    "   • 'Does the {company} 2024 proxy include indemnification of "
    "directors and officers?'\n"
    "   • 'What governing-law clause does {company} use in its proxy?'\n"
    "   • 'Does {company} have a force majeure provision in its 10-K "
    "exhibits?'\n"
    "   Frame the question like you would ask a colleague — never use folder "
    "IDs, path UUIDs, or path_part_id filters.\n"
    "2. search_knowledge returns ranked hits. The text field is empty by "
    "design — to get the chunk content, call read(path_part_id=<hit's "
    "path_part_id>). The returned text ends in a [chunk:<uuid>] marker; "
    "that uuid is your citation.chunk_id (NEVER pass the chunk_id to read; "
    "use path_part_id).\n"
    "3. Decide present=true/false based on the chunk text. Always populate "
    "every citation field: chunk_id (from the [chunk:<uuid>] marker), "
    "document_name (the filename in the read() output's metadata, e.g. "
    "'aapl_def14a_2024_proxy.pdf'), snippet (verbatim ≤240 chars).\n"
    "4. excerpt is verbatim contract text proving the clause (or 'not "
    "found').\n"
    "5. Always emit all 12 clauses."
    """Output format (STRICT): Your final response is a single JSON object that matches the response schema exactly. Do NOT wrap it in an extra key like {'<ClassName>': ...} or {'result': ...}. Every required string field is a string, not a nested object. Every required nested model is included with all of its required fields populated. Never omit required fields; never add unspecified ones."""
)
async def run(contract: str) -> None:
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
        output_type=ClauseInventory,
        retries=4,
        output_retries=4,
    )
    async with agent.run_mcp_servers():
        result = await agent.run(f"Contract to inventory: {contract}")
    print(json.dumps(result.output.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--contract",
        required=True,
        help="Contract name or distinguishing keyword that "
        "appears in the document filename or content.",
    )
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.contract))


if __name__ == "__main__":
    main()
