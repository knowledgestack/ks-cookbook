# RFC — KS handholding for small-model agents

**Status:** Draft. Filed by ks-cookbook on 2026-04-28.

**Audience:** ks-mcp + ks-backend maintainers.

**TL;DR:** A user with a 7B Ollama model + a KS API key should be able to run any cookbook recipe end-to-end with strict citation grounding. Today they can't, because `ks-mcp` returns half-empty hits that force a multi-step agent loop only large models reliably complete. **The single biggest fix is a ~10-line bug in `ks-mcp/tools/search.py`** that's been silently dropping chunk content from `search_knowledge` responses. Eliminating that one bug should unblock most of the small-model friction.

This RFC sizes six changes ranked by leverage. The first four are bug-fix scope (~hours, not days). The fifth and sixth are real features.

---

## The friction we hit

`recipes/icd10_coder` against `qwen2.5:7b` via Ollama: **fails repeatedly** with
`ValidationError: primary Field required`. The 7B model wrapped its output in
`{"CodeSuggestion": {...}}` because it had to manually assemble citations
from empty `text` and `document_name` fields, then guessed at the schema.

Same recipe against `gpt-4o`: **passes**. Same recipe against `qwen2.5:14b`:
gets closer but still drops fields.

The model isn't the problem. The problem is **how much work each model has
to do in the agent loop** before it can emit a citation. Small models can't
do the multi-step assembly; large ones can. Lower that bar in the server
and small models work.

---

## The fixes, sized

### #1 — Fix `_hit_from_scored_chunk` to populate `text` and `document_name` (BUG)

**Effort:** ~10 LOC, 1 file (`ks-mcp/src/ks_mcp/tools/search.py`). 1–2 hours including a test.

**File:** `tools/search.py:36-47`

**The bug:**

```python
def _hit_from_scored_chunk(scored: Any) -> ChunkHit:
    chunk = getattr(scored, "chunk", scored)
    return ChunkHit(
        chunk_id=chunk.id,
        document_name=getattr(chunk, "document_name", None)
            or (chunk.document.name if getattr(chunk, "document", None) else "")
            or "",
        text=(getattr(chunk, "text", "") or ""),    # ← BUG: ksapi field is `content`, not `text`
        ...
    )
```

`ksapi.ChunkResponse` has a `content` field (verified: `ChunkResponse.model_fields.keys()` returns `[..., 'content', ...]` and **no** `text` field). The MCP reads `chunk.text`, gets the empty default, and returns hits with `text=""`. Same with `document_name`: `ChunkResponse.document` is `null` in API responses, so the fallback to `chunk.document.name` always fails.

**The fix:**

```python
def _hit_from_scored_chunk(scored: Any) -> ChunkHit:
    chunk = getattr(scored, "chunk", scored)
    mat_path = getattr(chunk, "materialized_path", "") or ""
    # filename is the path segment ending in a known extension
    doc_name = ""
    for seg in (p for p in mat_path.split("/") if p):
        if "." in seg and seg.rsplit(".", 1)[-1].lower() in {
            "pdf", "docx", "xlsx", "pptx", "csv", "html", "txt", "md"
        }:
            doc_name = seg
            break
    return ChunkHit(
        chunk_id=chunk.id,
        document_name=doc_name or (chunk.document.name if getattr(chunk, "document", None) else "") or "",
        text=getattr(chunk, "content", "") or "",   # FIX
        score=getattr(scored, "score", None),
        chunk_type=ChunkType(getattr(chunk, "chunk_type", ChunkType.TEXT.value)),
        path_part_id=getattr(chunk, "path_part_id", None),
    )
```

**Impact:** After this, `search_knowledge` returns hits the agent can cite from directly — no follow-up `read()` round-trip needed. **This single fix probably resolves the majority of small-model failures we observed.**

---

### #2 — Make `read()` accept either a `path_part_id` *or* a chunk content id (BUG)

**Effort:** ~10 LOC, 1 file (`ks-mcp/src/ks_mcp/tools/read.py`). 1 hour.

Today the agent gets two UUIDs per hit (`chunk_id` for citation, `path_part_id` for read). When the agent passes `chunk_id` to `read()` — which every small model does at least once per run — `get_path_part()` returns 404, the tool errors, and the agent loop wedges on `Tool 'read' exceeded max retries count of 1`.

**The fix:** in `tools/read.py`, when `get_path_part(<id>)` 404s, **fall back to `ChunksApi.get_chunk(chunk_id=<id>)`** before erroring. The agent calling pattern becomes "either UUID works."

```python
try:
    pp = path_parts.get_path_part(path_part_id=path_part_id)
except ksapi.ApiException as exc:
    if is_not_found(exc):
        # Fallback: maybe the caller passed a chunk content id.
        try:
            chunk = ChunksApi(client).get_chunk(chunk_id=path_part_id)
            return _truncate(f"{chunk.content}\n\n[chunk:{path_part_id}]", max_chars)
        except ksapi.ApiException:
            pass
    raise rest_to_mcp(exc) from exc
```

**Impact:** Removes the second-most-common small-model failure mode (404 on `read(<chunk_id>)`).

---

### #3 — Improve tool descriptions to encode the gotchas

**Effort:** ~10 LOC of docstring edits. 30 minutes.

The schema docstrings are visible to *every* agent framework (pydantic-ai, LangGraph, Claude Desktop) without any per-recipe prompt fix. Three concrete edits:

```python
# search.py — add a single sentence to the search_knowledge docstring:
"""...
After this change, each hit includes the chunk text and the document
filename, so you can usually cite directly without a follow-up read()."""

# read.py — clarify the input parameter:
path_part_id: Annotated[UUID, Field(description=
    "Either a path_part_id from list_contents/find OR a chunk_id from "
    "search_knowledge. Both are accepted.")]

# Provide consistent canonical citation field names in ChunkHit
# (document_filename, not document_name vs materialized_path).
```

**Impact:** Recipe prompts no longer need to spell out KS quirks. The cookbook's per-recipe prompt-engineering compensation goes away.

---

### #4 — Surface `materialized_path` on `ChunkHit`

**Effort:** ~2 LOC in `schema.py`. 5 minutes.

```python
class ChunkHit(BaseModel):
    chunk_id: UUID
    document_name: str
    materialized_path: str | None = None   # ADD
    text: str
    ...
```

Then any agent has both filename and full provenance path without an extra `get_info` call. **Removes another round trip.**

---

### #5 — New tool: `cite(chunk_id)` returns canonical citation envelope

**Effort:** ~30 LOC, 1 new function in `tools/search.py` or new `tools/cite.py`. 2–3 hours including tests.

```python
class Citation(BaseModel):
    chunk_id: UUID
    document_filename: str
    snippet: str
    materialized_path: str

@mcp.tool()
def cite(chunk_id: UUID) -> Citation:
    """Return a canonical citation envelope for a chunk. Use this whenever
    the agent needs to cite a chunk in structured output — never assemble
    citations from raw fields."""
    chunk = ChunksApi(get_api_client()).get_chunk(chunk_id=chunk_id)
    return Citation(
        chunk_id=chunk_id,
        document_filename=_filename_from_path(chunk.materialized_path),
        snippet=chunk.content[:240],
        materialized_path=chunk.materialized_path or "",
    )
```

**Impact:** The recipe never assembles a citation — it calls `cite(chunk_id)` and pastes the result. Small-model drift on citation construction (the `{"CodeSuggestion": {...}}` wrapper bug) becomes structurally impossible.

---

### #6 — New tool: `answer_with_citations(question, schema)` (BIG)

**Effort:** **2–3 days** including LLM client + retry loop + tests. New file in `ks-mcp` plus possibly a new `/v1/agent/answer` endpoint in `ks-backend`.

```python
@mcp.tool()
def answer_with_citations(
    question: str,
    schema: dict,           # JSON-Schema
    schema_hint: str = "",  # "Return CodingResult"
) -> str:                   # JSON matching schema
    """Server-side: run the full search → read → cite → format loop and
    return a JSON object that conforms to <schema>. The KS server hosts
    its own LLM and handles retries. The calling agent only needs to
    parse the JSON."""
```

This requires KS to either (a) host its own LLM endpoint or (b) call out to an LLM provider on behalf of the user. That's a product decision (cost, billing, model choice) more than a code one. **Defer until #1–#5 are shipped and we measure how much friction remains.**

---

## Recommended phasing

| Phase | Items | Effort | Unblocks |
|---|---|---|---|
| **P0 — bug fixes** | #1, #2, #3, #4 | **~1 day** total | Most small-model failures we saw. Cookbook recipes work with `qwen2.5:7b`. |
| **P1 — citation tool** | #5 | 2–3 hours | Eliminates the citation-drift class entirely. |
| **P2 — server-side agent** | #6 | 2–3 days + product decisions | Recipe = 30 LOC; any model can route. |

**The single highest-leverage move is P0 #1.** That's a 10-line patch to `ks-mcp/src/ks_mcp/tools/search.py:36-47` that probably moves the cookbook from ~30% small-model pass-rate to ~80% with no other changes.

---

## Verification plan after P0 ships

1. Re-run `bulk_verify_recipes.py --limit 25` with `MODEL=qwen2.5:7b`. Expect ≥80% pass.
2. Spot-check 5 recipes by hand for citation quality (real chunk_ids, real document filenames, real snippets).
3. Repeat with `gpt-4o`. Expect ≥95% pass with no other recipe changes.

If P0 lands those numbers, P2 (#6) is optional polish. If it doesn't, P1 + #5 next; only escalate to #6 if friction persists.
