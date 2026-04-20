"""Loan-application doc classifier — uploaded doc → cited type + extraction.

Pain point: Loan ops triage folders of scans: paystubs, W2s, bank statements,
tax returns, IDs. This recipe classifies each document and extracts the key
fields the underwriter needs, citing the corpus's document-type playbook.

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

CORPUS = os.environ.get("LENDING_FOLDER_ID", "ab926019-ac7a-579f-bfda-6c52a13c5f41")


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=240)


class DocClassification(BaseModel):
    document_name: str
    doc_type: str = Field(..., pattern="^(paystub|w2|1099|bank_statement|tax_return|photo_id|lease|other)$")
    confidence: str = Field(..., pattern="^(low|medium|high)$")
    key_fields: dict[str, str] = Field(..., description="Extracted key/value fields per playbook.")
    completeness: str = Field(..., pattern="^(ok|missing_fields|illegible)$")
    citation: Citation


PROMPT = (
    "You classify loan-application documents and extract fields per our "
    f"document-type playbook in path_part_id={CORPUS}. If illegible or "
    "missing fields, say so — don't guess. chunk_ids must be real."
)


async def run(document_name: str, text: str) -> None:
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
                  mcp_servers=[mcp], system_prompt=PROMPT, result_type=DocClassification)
    async with agent.run_mcp_servers():
        result = await agent.run(f"Document: {document_name}\n\nOCR/text:\n{text[:4000]}")
    print(json.dumps(result.data.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--document-name", required=True)
    p.add_argument("--text", required=True, help="OCR text or excerpt of the document.")
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.document_name, args.text))


if __name__ == "__main__":
    main()
