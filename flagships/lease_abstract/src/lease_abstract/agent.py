"""Raw OpenAI function-calling agent grounded in the KS HTTP API."""

import json
import os
from typing import Any
from uuid import UUID

import ksapi
from ksapi.api.chunks_api import ChunksApi
from ksapi.api.document_versions_api import DocumentVersionsApi
from ksapi.api.documents_api import DocumentsApi
from ksapi.api.folders_api import FoldersApi
from ksapi.api.path_parts_api import PathPartsApi
from openai import OpenAI

from lease_abstract.schema import ABSTRACT_TEMPLATE, TOOLS

SYSTEM_PROMPT_TEMPLATE = """\
You are a CRE asset manager writing a one-page LEASE ABSTRACT.

Tools: `list_contents(folder_id)` and `read(path_part_id, max_chars)` — document
reads return the outline with inline `[chunk:<uuid>]` markers (your citations).

Workflow:
1. `list_contents(CORPUS_FOLDER_ID)` to see leases and the abstract template.
2. `read` the `lease_abstract_template` to internalize required fields.
3. `read` the target lease. Copy every `[chunk:<uuid>]` UUID verbatim.
4. Emit PLAIN MARKDOWN following this shape (replace UUID placeholders):

{template}

RULES: never invent a chunk UUID; only cite UUIDs that appeared in a `read`
response. If a field is not addressed, write "Not addressed" and skip the
citation. Keep it concise — one page, bullets preferred.

CORPUS_FOLDER_ID: {corpus_folder_id}
TARGET_LEASE: {target_lease}

KS workflow (do NOT skip — this section overrides the workflow above):
1. Use search_knowledge with natural-language questions. NEVER use folder UUIDs or path_part_id filters; KS searches the whole tenant.
2. search_knowledge returns hits with chunk_id and path_part_id (text empty). Call read(path_part_id=<hit's path_part_id>) to get the chunk text. The trailing [chunk:<uuid>] marker is the citation chunk_id. NEVER pass chunk_id to read; it 404s.
3. Available MCP tools (use ONLY these): search_knowledge, search_keyword, read, find, list_contents, get_info. There is NO 'cite' tool, no 'read_around' workflow, do NOT invent tools.
4. Build every output field ONLY from chunk text you read. Never fabricate. Populate every citation with chunk_id (verbatim), document_name (filename), snippet (verbatim ≤240 chars).

Output format (STRICT): A single JSON object matching the schema. Do NOT wrap in {{<ClassName>: ...}} or {{result: ...}}. Every required field must be present.
"""


def _build_client() -> ksapi.ApiClient:
    config = ksapi.Configuration(
        host=os.environ.get("KS_BASE_URL", "https://api.knowledgestack.ai"),
    )
    client = ksapi.ApiClient(config)
    client.set_default_header("Authorization", f"Bearer {os.environ['KS_API_KEY']}")
    return client


def _truncate(text: str, limit: int) -> str:
    return text if len(text) <= limit else text[:limit] + "\n...[truncated]"


def _do_list_contents(api: ksapi.ApiClient, folder_id: str) -> str:
    resp = FoldersApi(api).list_folder_contents(folder_id=UUID(folder_id))
    rows = []
    for raw in getattr(resp, "items", None) or []:
        inner = getattr(raw, "actual_instance", None) or raw
        pp_id = getattr(inner, "path_part_id", None) or getattr(inner, "id", None)
        rows.append(
            {
                "path_part_id": str(pp_id) if pp_id else None,
                "name": getattr(inner, "name", ""),
                "part_type": str(getattr(inner, "part_type", "UNKNOWN")),
            }
        )
    return json.dumps(rows)


def _do_read(api: ksapi.ApiClient, path_part_id: str, max_chars: int) -> str:
    pp = PathPartsApi(api).get_path_part(path_part_id=UUID(path_part_id))
    ptype = getattr(pp, "part_type", "")
    meta = getattr(pp, "metadata_obj_id", None)
    if ptype == "CHUNK" and meta:
        chunk: Any = ChunksApi(api).get_chunk(chunk_id=meta)
        return _truncate(getattr(chunk, "text", "") or "", max_chars)
    if ptype != "DOCUMENT" or not meta:
        return f"{pp.name} ({ptype}) — call list_contents to drill in."
    doc: Any = DocumentsApi(api).get_document(document_id=meta)
    version_id = getattr(doc, "active_version_id", None)
    if version_id is None:
        return getattr(doc, "name", pp.name)
    pieces: list[str] = [f"# {getattr(doc, 'name', pp.name)}\n"]
    offset = 0
    while True:
        contents: Any = DocumentVersionsApi(api).get_document_version_contents(
            version_id=version_id,
            limit=100,
            offset=offset,
        )
        items = getattr(contents, "items", None) or []
        if not items:
            break
        for item in items:
            inner = getattr(item, "actual_instance", None) or item
            part = str(getattr(inner, "part_type", ""))
            if "SECTION" in part:
                pieces.append(f"\n## {getattr(inner, 'name', '')}\n")
                continue
            text = getattr(inner, "text", None) or getattr(inner, "content", "") or ""
            cid = getattr(inner, "id", None) or getattr(inner, "metadata_obj_id", None)
            if text:
                pieces.append(f"{text}{f' [chunk:{cid}]' if cid else ''}\n")
        if len(items) < 100:
            break
        offset += 100
    return _truncate("".join(pieces), max_chars)


def _dispatch(api: ksapi.ApiClient, name: str, args: dict[str, Any]) -> str:
    if name == "list_contents":
        return _do_list_contents(api, args["folder_id"])
    if name == "read":
        return _do_read(api, args["path_part_id"], int(args.get("max_chars", 8000)))
    return json.dumps({"error": f"unknown tool {name}"})


def draft_abstract(
    *,
    corpus_folder_id: str,
    target_lease: str,
    model: str = "gpt-4o",
    max_steps: int = 12,
) -> str:
    api = _build_client()
    openai = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    prompt = SYSTEM_PROMPT_TEMPLATE.format(
        template=ABSTRACT_TEMPLATE,
        corpus_folder_id=corpus_folder_id,
        target_lease=target_lease,
    )
    messages: list[dict[str, Any]] = [
        {"role": "system", "content": prompt},
        {
            "role": "user",
            "content": f"Produce the lease abstract for '{target_lease}'.",
        },
    ]
    for _ in range(max_steps):
        resp = openai.chat.completions.create(
            model=model,
            messages=messages,  # pyright: ignore[reportArgumentType]
            tools=TOOLS,  # pyright: ignore[reportArgumentType]
            tool_choice="auto",
        )
        msg = resp.choices[0].message
        if not msg.tool_calls:
            return (msg.content or "").strip()
        messages.append(
            {
                "role": "assistant",
                "content": msg.content or "",
                "tool_calls": [t.model_dump() for t in msg.tool_calls],
            }
        )
        for call in msg.tool_calls:
            try:
                args = json.loads(call.function.arguments or "{}")
                output = _dispatch(api, call.function.name, args)
            except Exception as exc:  # noqa: BLE001
                output = json.dumps({"error": f"{type(exc).__name__}: {exc}"})
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call.id,
                    "name": call.function.name,
                    "content": output,
                }
            )
    return "ERROR: agent exceeded max_steps without producing a final abstract."
