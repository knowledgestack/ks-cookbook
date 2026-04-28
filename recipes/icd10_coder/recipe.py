"""ICD-10 coder — clinical note → cited ICD-10-CM code suggestions.

Pain point: Medical coders hand-map physician notes to ICD-10-CM. This recipe
reads a de-identified note and returns code candidates grounded in whatever
ICD-10 / clinical-coding reference happens to live in your Knowledge Stack
tenant. The agent discovers the relevant document itself via search_knowledge
— no folder UUIDs to wire up.

Framework: pydantic-ai. Tools: search_knowledge, search_keyword, read.
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
    "You suggest ICD-10-CM codes for a de-identified clinical note. "
    "Knowledge Stack is your search backend; you ask natural-language "
    "questions about codes and conditions.\n\n"
    "Workflow:\n"
    "1. For each candidate code, call search_knowledge with a real "
    "question, e.g. 'How does the CMS ICD-10-CM guideline distinguish "
    "between NSTEMI and STEMI codes?'. Never use folder UUIDs.\n"
    "2. search_knowledge returns hits with chunk_id and path_part_id, but "
    "text is empty. To get the chunk content, call read(path_part_id=<hit."
    "path_part_id>). The returned text ends in a [chunk:<uuid>] marker — "
    "that uuid is your citation.chunk_id. NEVER pass chunk_id to read.\n"
    "3. If no chunk evidences a code, set confidence='low'.\n\n"
    "Output schema — your final response MUST be a JSON object that exactly "
    "matches this shape (no extra wrapper keys, no $defs):\n"
    "{\n"
    '  "primary": {\n'
    '    "code": "I21.4",\n'
    '    "description": "Non-ST elevation MI",\n'
    '    "confidence": "high",\n'
    '    "evidence_in_note": "Patient with NSTEMI per ECG and troponin.",\n'
    '    "citation": {\n'
    '      "chunk_id": "019dd1fd-c3ad-7971-8bdf-37af8fdbe1db",\n'
    '      "document_name": "cms_fy2026_icd10cm_coding_guidelines.pdf",\n'
    '      "snippet": "Code I21.4, Non-ST elevation (NSTEMI) MI..."\n'
    "    }\n"
    "  },\n"
    '  "secondaries": [ /* zero or more entries with the same shape as '
    "primary */ ]\n"
    "}\n\n"
    "Every field shown is REQUIRED on primary and on each secondary. "
    "code must match the regex ^[A-Z][0-9][0-9A-Z](\\.[0-9A-Z]{1,4})?$. "
    "confidence must be exactly one of: low | medium | high. Do NOT wrap "
    "the result in extra keys like {\"CodeSuggestion\": ...} or "
    "{\"result\": ...}. Never invent codes or chunk_ids."
    """Output format (STRICT): Your final response is a single JSON object that matches the response schema exactly. Do NOT wrap it in an extra key like {'<ClassName>': ...} or {'result': ...}. Every required string field is a string, not a nested object. Every required nested model is included with all of its required fields populated. Never omit required fields; never add unspecified ones."""
)
async def run(note: str) -> None:
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
        output_type=CodingResult,
        retries=4,
        output_retries=4,
    )
    async with agent.run_mcp_servers():
        result = await agent.run(f"Clinical note:\n{note[:6000]}")
    print(json.dumps(result.output.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--note-file", type=Path, required=True, help="Text file with de-identified clinical note."
    )
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.note_file.read_text()))


if __name__ == "__main__":
    main()
