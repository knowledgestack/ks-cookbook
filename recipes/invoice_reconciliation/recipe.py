"""Invoice reconciliation — invoice line → cited match vs PO + contract.

Pain point: AP reconciles each line against the PO and the contract rate card.
This recipe performs a 3-way match (invoice vs PO vs contract) and flags
discrepancies with citations.

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

CORPUS = os.environ.get("FINANCE_FOLDER_ID", "ab926019-ac7a-579f-bfda-6c52a13c5f41")


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=240)


class MatchResult(BaseModel):
    invoice_line: str
    po_number: str
    contract_ref: str
    matched: bool
    discrepancy: str = Field(..., max_length=400)
    suggested_action: str = Field(..., pattern="^(approve|short_pay|hold|reject)$")
    citations: list[Citation] = Field(..., min_length=1, max_length=4)


PROMPT = (
    "You reconcile invoices. Read the PO and the contract rate card in "
    f"path_part_id={CORPUS}. Flag any line where unit price, quantity, or "
    "service period diverges. Cite real chunk_ids."
)


async def run(invoice_line: str, po: str, contract: str) -> None:
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
                  mcp_servers=[mcp], system_prompt=PROMPT, result_type=MatchResult)
    async with agent.run_mcp_servers():
        result = await agent.run(
            f"Invoice line: {invoice_line}\nPO: {po}\nContract: {contract}"
        )
    print(json.dumps(result.data.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--invoice-line", required=True)
    p.add_argument("--po", required=True)
    p.add_argument("--contract", required=True)
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.invoice_line, args.po, args.contract))


if __name__ == "__main__":
    main()
