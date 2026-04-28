"""FOIA response drafter — raw OpenAI + MCP stdio.

Workflow:
1. `list_contents(corpus_folder_id)` to enumerate DOJ guide + agency SOP.
2. `read(path_part_id=<doc>, max_chars=8000)` to get document text with
   inline [chunk:<uuid>] markers.
3. Ask the LLM to draft a FOIA response letter with exemption analysis.
"""

import json
import os
from contextlib import asynccontextmanager
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from openai import AsyncOpenAI


@asynccontextmanager
async def ks_mcp_session():
    params = StdioServerParameters(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={
            "KS_API_KEY": os.environ.get("KS_API_KEY", ""),
            "KS_BASE_URL": os.environ.get("KS_BASE_URL", ""),
        },
    )
    async with stdio_client(params) as (reader, writer):
        async with ClientSession(reader, writer) as session:
            await session.initialize()
            yield session


async def call(session: ClientSession, name: str, arguments: dict[str, Any]) -> str:
    result = await session.call_tool(name, arguments)
    if result.isError:
        raise RuntimeError(
            f"tool `{name}` failed: "
            + (result.content[0].text if result.content else "")
        )
    return "\n".join(c.text for c in result.content if hasattr(c, "text"))


async def call_list(
    session: ClientSession, name: str, arguments: dict[str, Any]
) -> list[Any]:
    result = await session.call_tool(name, arguments)
    if result.isError:
        raise RuntimeError(
            f"tool `{name}` failed: "
            + (result.content[0].text if result.content else "")
        )
    out: list[Any] = []
    for c in result.content:
        if not hasattr(c, "text"):
            continue
        try:
            out.append(json.loads(c.text))
        except json.JSONDecodeError:
            out.append(c.text)
    return out


SYSTEM_PROMPT = """\
You are a FOIA (Freedom of Information Act) response officer drafting an
official response letter. You have access to the agency's FOIA processing
SOP and the DOJ Guide to the Freedom of Information Act.

Using the corpus documents provided, draft a complete FOIA response that:

1. Summarizes the records search conducted.
2. Identifies which FOIA exemptions (5 U.S.C. 552(b)(1)-(9)) apply to any
   withheld or redacted records, citing the DOJ guide for each exemption.
3. Follows the agency SOP for response formatting and processing steps.
4. Notes any redactions and the specific exemption justifying each.
5. Addresses fee waiver eligibility per the SOP.

RULES:
- Every exemption cited MUST reference a `[chunk:<uuid>]` marker you saw
  in the DOJ guide or agency SOP text. NEVER invent chunk ids.
- Output PLAIN MARKDOWN following the template structure. No JSON.
- Citation format: `[N] <document_name> — [chunk:<uuid>] "short quote"`.
- Use `[1]`, `[2]` inline; the numbered list in Citations resolves them.
- If a determination cannot be made from available documents, state
  "REQUIRES MANUAL REVIEW" for that section.
"""


async def draft_foia_response(
    *,
    request_text: str,
    corpus_folder_id: str,
    model: str,
) -> str:
    all_texts: list[str] = []
    doc_names: list[str] = []

    async with ks_mcp_session() as session:
        listing = await call_list(
            session, "list_contents", {"folder_id": corpus_folder_id}
        )
        docs = [
            p
            for p in listing
            if isinstance(p, dict) and p.get("part_type") == "DOCUMENT"
        ]
        if not docs:
            raise RuntimeError("No documents found in the corpus folder.")

        for doc in docs:
            text = await call(
                session,
                "read",
                {"path_part_id": doc["path_part_id"], "max_chars": 8000},
            )
            all_texts.append(f"=== {doc['name']} ===\n{text}")
            doc_names.append(doc["name"])

    combined = "\n\n".join(all_texts)
    client = AsyncOpenAI()
    user_prompt = (
        f"FOIA Request:\n{request_text}\n\n"
        f"Reference documents (with inline [chunk:<uuid>] markers):\n\n"
        f"{combined}\n\n"
        f"Draft the complete FOIA response letter now."
    )
    reply = await client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )
    return (reply.choices[0].message.content or "").strip()


def model_id_default() -> str:
    return os.environ.get("FOIA_MODEL", "gpt-4o")
