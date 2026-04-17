"""MSA redline agent — raw OpenAI + MCP stdio.

Workflow:
1. ``list_contents(corpus_folder_id)`` to enumerate the playbook and inbound MSA.
2. ``read(path_part_id=<playbook>, max_chars=15000)`` to get the playbook text.
3. ``read(path_part_id=<inbound>, max_chars=15000)`` to get the inbound MSA text.
4. Ask the LLM to compare clause-by-clause and produce a ``RedlineMemo`` with
   chunk_ids copied verbatim from [chunk:<uuid>] markers.
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

from msa_redline_vs_playbook.schema import RedlineMemo


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
You are a senior contracts attorney performing a redline review. You have two
documents:
- The **playbook** (your company's standard terms).
- The **inbound contract** (the counterparty's proposed terms).

Compare them clause-by-clause on every material topic.

Return a JSON object with EXACTLY these fields:
{
  "inbound_contract_name": "<string>",
  "playbook_name": "<string>",
  "executive_summary": "<2-3 sentence summary>",
  "clauses": [
    {
      "clause_topic": "<e.g. Indemnification>",
      "playbook_position": "<summary of playbook stance>",
      "inbound_position": "<summary of inbound stance, or NOT FOUND>",
      "deviation_severity": "<NONE|MINOR|MAJOR|MISSING>",
      "recommended_change": "<specific recommendation>",
      "playbook_citation": "<UUID from [chunk:UUID] in playbook text>",
      "inbound_citation": "<UUID from [chunk:UUID] in inbound text, or empty>"
    }
  ]
}

At minimum cover: Indemnification, Limitation of Liability, Confidentiality,
IP Ownership, Data Protection, Term & Termination, Warranties, Payment.

RULES:
- Use EXACTLY the field names shown above. Do not rename them.
- ``deviation_severity`` must be one of: NONE, MINOR, MAJOR, MISSING.
- ``playbook_citation`` and ``inbound_citation`` MUST be UUIDs copied verbatim
  from ``[chunk:<uuid>]`` markers in the supplied text. NEVER invent chunk ids.
- If the inbound contract is missing a clause, set deviation_severity=MISSING
  and leave inbound_citation as empty string.
- Return a single JSON object. No prose, no markdown fences.
"""


def _pick_doc(docs: list[dict], wanted: str) -> dict:
    lw = wanted.lower()
    for d in docs:
        if lw in (d.get("name", "") or "").lower():
            return d
    raise RuntimeError(
        f"No document matching '{wanted}' found. Available: "
        + ", ".join(d.get("name", "?") for d in docs)
    )


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


async def compare_msa(
    *,
    corpus_folder_id: str,
    playbook_name: str,
    inbound_name: str,
    model: str,
) -> RedlineMemo:
    async with ks_mcp_session() as session:
        listing = await call_list(
            session, "list_contents", {"folder_id": corpus_folder_id}
        )
        docs = [
            p
            for p in listing
            if isinstance(p, dict) and p.get("part_type") == "DOCUMENT"
        ]
        playbook_doc = _pick_doc(docs, playbook_name)
        inbound_doc = _pick_doc(docs, inbound_name)

        playbook_text = await call(
            session,
            "read",
            {"path_part_id": playbook_doc["path_part_id"], "max_chars": 15000},
        )
        inbound_text = await call(
            session,
            "read",
            {"path_part_id": inbound_doc["path_part_id"], "max_chars": 15000},
        )

    client = AsyncOpenAI()
    user_prompt = (
        f"## PLAYBOOK: {playbook_doc['name']}\n\n{playbook_text}\n\n"
        f"---\n\n"
        f"## INBOUND CONTRACT: {inbound_doc['name']}\n\n{inbound_text}\n\n"
        f"---\n\n"
        f"Return a `RedlineMemo` JSON object.\n"
        f'`playbook_name` MUST equal "{playbook_doc["name"]}".\n'
        f'`inbound_contract_name` MUST equal "{inbound_doc["name"]}".'
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

    # Normalize: find the list-valued key that contains the clause comparisons.
    if "clauses" not in obj:
        for key, val in obj.items():
            if isinstance(val, list) and val and isinstance(val[0], dict):
                obj["clauses"] = obj.pop(key)
                break

    # Normalize field names the LLM may use differently.
    field_map = {
        "topic": "clause_topic",
        "clause": "clause_topic",
        "playbook": "playbook_position",
        "inbound": "inbound_position",
        "recommendation": "recommended_change",
        "change": "recommended_change",
        "severity": "deviation_severity",
    }
    severity_map = {
        "DIFFERENT": "MAJOR",
        "SIMILAR": "MINOR",
        "MATCH": "NONE",
        "IDENTICAL": "NONE",
        "ABSENT": "MISSING",
        "NOT FOUND": "MISSING",
    }
    for clause in obj.get("clauses", []):
        for alt, canon in field_map.items():
            if alt in clause and canon not in clause:
                clause[canon] = clause.pop(alt)
        sev = clause.get("deviation_severity", "")
        if isinstance(sev, str):
            clause["deviation_severity"] = severity_map.get(
                sev.upper(), sev.upper()
            )

    # Filter out clauses whose chunk_ids don't appear in the source texts.
    # If filtering would remove all clauses, keep them (LLM best-effort).
    all_text = playbook_text + inbound_text
    valid_ids = {v.lower() for v in re.findall(r"\[chunk:([0-9a-fA-F-]+)\]", all_text)}
    clauses_in = obj.get("clauses", []) or []
    if valid_ids and clauses_in:
        filtered = [
            c
            for c in clauses_in
            if str(c.get("playbook_citation", "")).lower() in valid_ids
            or str(c.get("inbound_citation", "")).lower() in valid_ids
        ]
        if filtered:
            obj["clauses"] = filtered
    obj.setdefault("playbook_name", playbook_doc["name"])
    obj.setdefault("inbound_contract_name", inbound_doc["name"])
    try:
        return RedlineMemo.model_validate(obj)
    except ValidationError as e:
        raise RuntimeError(f"Model output failed schema validation: {e}") from e


def model_id_default() -> str:
    return os.environ.get("MSA_REDLINE_MODEL", "gpt-4o")
