"""Obligation-extractor agent — raw OpenAI + MCP stdio.

Workflow:
1. `list_contents(corpus_folder_id)` to enumerate contracts.
2. Pick the one that matches the user's --contract-name, or take the first.
3. `read(path_part_id=<doc>, max_chars=15000)` to get the full document text
   with inline [chunk:<uuid>] markers.
4. Ask the LLM to extract every shall/must/will obligation into
   `ObligationReport`, copying chunk_ids verbatim.
"""


import json
import os
import re
from contextlib import asynccontextmanager
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from openai import AsyncOpenAI
from pydantic import ValidationError

from contract_obligation_extractor.schema import ObligationReport


@asynccontextmanager
async def ks_mcp_session():
    params = StdioServerParameters(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    async with stdio_client(params) as (reader, writer):
        async with ClientSession(reader, writer) as session:
            await session.initialize()
            yield session


async def call(session: ClientSession, name: str, arguments: dict[str, Any]) -> str:
    result = await session.call_tool(name, arguments)
    if result.isError:
        raise RuntimeError(f"tool `{name}` failed: "
                           + (result.content[0].text if result.content else ""))
    return "\n".join(c.text for c in result.content if hasattr(c, "text"))


async def call_list(session: ClientSession, name: str, arguments: dict[str, Any]) -> list[Any]:
    result = await session.call_tool(name, arguments)
    if result.isError:
        raise RuntimeError(f"tool `{name}` failed: "
                           + (result.content[0].text if result.content else ""))
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
You are a legal contract analyst. Extract every obligation clause from the
supplied contract text. An "obligation" is any sentence whose main verb is
"shall", "must", or "will" (performative will — commitment, not prediction).

For each obligation:
- Set `holder` to one of: Provider, Customer, Mutual. Use "Mutual" only when
  the clause binds both parties equally (e.g. "Each Party shall..." or both
  parties appear together as subjects).
- `verb` is the lowercase modal: shall | must | will.
- `summary` is a plain-English, <=1-sentence paraphrase.
- `quote` is verbatim (or near-verbatim) from the source, trimmed to <=800 chars.
- `chunk_id` MUST be a UUID copied verbatim from a `[chunk:<uuid>]` marker in
  the supplied text. NEVER invent chunk ids.
- `section` is the heading the clause falls under (the most recent `##` in the
  text, or the most recent heading-like line).

RULES:
- Never extract an obligation whose chunk_id you did not see in the input.
- Skip passive/aspirational sentences that don't impose a duty (e.g.
  "Services may be described in an Order Form").
- Keep the JSON minified-compatible — return a single object, no prose,
  no markdown fences, matching the ObligationReport schema exactly.
"""


def _pick_contract(docs: list[dict], wanted: str | None) -> dict:
    if not docs:
        raise RuntimeError("No documents found in the corpus folder.")
    if wanted:
        lw = wanted.lower()
        for d in docs:
            if lw in (d.get("name", "") or "").lower():
                return d
    return docs[0]


def _parse_json(text: str) -> dict:
    cleaned = text.strip()
    fence = re.match(r"^```[a-zA-Z]*\s*\n?(.*?)\n?```\s*$", cleaned, re.DOTALL)
    if fence:
        cleaned = fence.group(1).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass
    start = cleaned.find("{")
    if start < 0:
        raise ValueError(f"no JSON object in reply: {cleaned[:200]!r}")
    depth = 0
    for i in range(start, len(cleaned)):
        if cleaned[i] == "{":
            depth += 1
        elif cleaned[i] == "}":
            depth -= 1
            if depth == 0:
                return json.loads(cleaned[start : i + 1])
    raise ValueError(f"unbalanced JSON in reply: {cleaned[:200]!r}")


async def extract_obligations(
    *, corpus_folder_id: str, contract_name: str | None, model: str,
) -> ObligationReport:
    async with ks_mcp_session() as session:
        listing = await call_list(
            session, "list_contents", {"folder_id": corpus_folder_id}
        )
        docs = [
            p for p in listing
            if isinstance(p, dict) and p.get("part_type") == "DOCUMENT"
        ]
        contract = _pick_contract(docs, contract_name)
        text = await call(
            session, "read",
            {"path_part_id": contract["path_part_id"], "max_chars": 15000},
        )

    client = AsyncOpenAI()
    user_prompt = (
        f"Contract name: {contract['name']}\n\n"
        f"Full text (with inline [chunk:<uuid>] markers after each passage):\n\n"
        f"{text}\n\n"
        f"Return an `ObligationReport` JSON object. `document_name` MUST equal "
        f"\"{contract['name']}\"."
    )
    reply = await client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        response_format={"type": "json_object"},
    )
    raw = reply.choices[0].message.content or ""
    obj = _parse_json(raw)
    # Filter out any obligation whose chunk_id doesn't appear in the source text.
    valid_ids = set(re.findall(r"\[chunk:([0-9a-fA-F-]+)\]", text))
    obs_in = obj.get("obligations", []) or []
    obj["obligations"] = [
        o for o in obs_in if str(o.get("chunk_id", "")).lower() in valid_ids
    ]
    obj.setdefault("document_name", contract["name"])
    try:
        return ObligationReport.model_validate(obj)
    except ValidationError as e:
        raise RuntimeError(f"Model output failed schema validation: {e}") from e


def model_id_default() -> str:
    return os.environ.get("CONTRACT_OBLIG_MODEL", "gpt-4o")
