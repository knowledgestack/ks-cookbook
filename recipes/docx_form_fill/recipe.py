"""DOCX form-fill — replace ``{{placeholders}}`` in a .docx using corpus answers.

Pain point: Vendor questionnaires, DDQs, security forms arrive as Word files with
blanks. Ops copy-pastes from policy PDFs and tracks citations in a sidecar sheet.
This recipe: a ``.docx`` with ``{{field_name}}`` tokens → filled .docx + cited
evidence sidecar (JSON), every answer grounded in real ``[chunk:<uuid>]`` tags.

Framework: pydantic-ai + python-docx.
Tools used: list_contents, search_knowledge, read.
Output: <template-stem>.filled.docx  +  <template-stem>.citations.json
"""

import argparse
import asyncio
import json
import os
import re
import sys
from pathlib import Path

from docx import Document as DocxDocument
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio

CORPUS_FOLDER = os.environ.get("POLICIES_FOLDER_ID", "ab926019-ac7a-579f-bfda-6c52a13c5f41")
PLACEHOLDER_RE = re.compile(r"\{\{\s*([a-zA-Z0-9_\-]+)\s*\}\}")


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=240)


class FieldAnswer(BaseModel):
    value: str = Field(..., max_length=1200)
    citations: list[Citation] = Field(..., min_length=1, max_length=4)


PROMPT = (
    "You answer a single form field from corporate policy. Use MCP tools to ground "
    f"every answer in path_part_id={CORPUS_FOLDER}. Return a concise value suitable "
    "for direct paste into a Word document. Citations MUST be real [chunk:<uuid>] "
    "IDs from read output — never fabricate a UUID."
)


def _find_placeholders(doc: DocxDocument) -> list[str]:
    seen: list[str] = []
    for para in doc.paragraphs:
        for match in PLACEHOLDER_RE.finditer(para.text):
            name = match.group(1)
            if name not in seen:
                seen.append(name)
    return seen


def _replace(doc: DocxDocument, name: str, value: str) -> None:
    token = "{{" + name + "}}"
    for para in doc.paragraphs:
        if token in para.text:
            for run in para.runs:
                if token in run.text:
                    run.text = run.text.replace(token, value)


async def run(template: Path, question_hint: str) -> None:
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(
        model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
        mcp_servers=[mcp], system_prompt=PROMPT, result_type=FieldAnswer,
    )
    doc = DocxDocument(template)
    fields = _find_placeholders(doc)
    if not fields:
        sys.exit(f"No {{{{placeholders}}}} found in {template}.")
    evidence: dict[str, dict] = {}
    async with agent.run_mcp_servers():
        for field in fields:
            request = f"Field: {field.replace('_', ' ')}\nContext: {question_hint}"
            result = await agent.run(request)
            answer = result.data
            _replace(doc, field, answer.value)
            evidence[field] = answer.model_dump()
    out_docx = template.with_suffix(".filled.docx")
    out_json = template.with_suffix(".citations.json")
    doc.save(out_docx)
    out_json.write_text(json.dumps(evidence, indent=2))
    print(f"Filled: {out_docx}\nCitations: {out_json}")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--template", type=Path, required=True,
                   help="A .docx with {{field_name}} placeholders.")
    p.add_argument("--hint", default="Answer from our security & privacy policies.")
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.template, args.hint))


if __name__ == "__main__":
    main()
