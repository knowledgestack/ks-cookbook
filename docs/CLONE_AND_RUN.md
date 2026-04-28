# Clone & run — what a fresh developer actually hits

This doc is the result of running the cookbook from a freshly cloned, empty
checkout against a real Knowledge Stack tenant on 2026-04-28. It documents
exactly what works, what doesn't, and the pragmatic retry pattern needed
with `gpt-4o-mini`.

---

## Two paths the README advertises

| | Path A — `ingestion: true` | Path B — `ingestion: false` |
|---|---|---|
| Use case | Try recipes against pre-ingested cookbook tenant | Run recipes against your own KS tenant |
| Status | **🚧 not yet stood up** — the shared cookbook tenant is on the roadmap. | **✅ verified end-to-end** in this document. |

For now, **only Path B is real**. The README references "request a read-only Cookbook demo key" which is aspirational until the maintainers stand up the shared tenant.

## Path B — fresh-clone walkthrough (verified)

### 1. Clone + install

```bash
git clone https://github.com/knowledgestack/ks-cookbook
cd ks-cookbook
make install   # uv sync --all-packages — installs ksapi, pydantic-ai, llama_index, knowledgestack-mcp (git dep)
```

The `knowledgestack-mcp` server is now a **git dependency** in `pyproject.toml`. After `make install`, the binary is at `.venv/bin/ks-mcp` and that's the recipes' default `KS_MCP_COMMAND`. **No `uvx`, no separate clone of `ks-mcp` required.**

### 2. Configure env

```bash
cp .env.example .env
# edit .env to set:
#   KS_API_KEY=sk-user-...
#   KS_BASE_URL=https://api.knowledgestack.ai
#   OPENAI_API_KEY=sk-...
#   MODEL=gpt-4o-mini   # cheapest viable; gpt-4o is more reliable per-shot
```

### 3. Ingest the unified corpus into your tenant (one-time)

```bash
# Create a parent folder via the KS UI, copy its path_part_id, then:
KS_API_KEY=$KS_API_KEY KS_BASE_URL=$KS_BASE_URL \
  uv run python scripts/seed_unified_corpus.py \
    --parent-folder-id <PARENT_PATH_PART_ID>
```

Idempotent — re-running skips already-ingested files. Wait ~4 min/doc for KS ingestion workflows to complete.

### 4. Run any recipe

```bash
uv run python recipes/icd10_coder/recipe.py \
    --note-file recipes/icd10_coder/sample_inputs/deid_visit_001.txt
```

Each recipe folder has its own README with a captured live JSON output sample under "Live verified — \<recipe\>".

---

## The honest gpt-4o-mini reality

Over a 105-recipe bulk sweep against `gpt-4o-mini`:

| Run | Pass rate |
|-----|-----------|
| First shot | ~73% |
| After 1 retry | ~92% |
| After 2 retries | ~97% |
| After 3 retries | **~98% (103/105)** |

The two consistently-failing recipes are documented product-shape gaps, not bugs:
- `permission_aware_retrieval` — multi-tenant demo, requires `ALICE_KS_API_KEY` + `BOB_KS_API_KEY`.
- `version_drift_review` — calls `ksapi` directly (not via MCP) and hits the auth-wiring bug documented in [`docs/RFC_KS_MCP_HANDHOLDING.md`](RFC_KS_MCP_HANDHOLDING.md).

**Why first-shot fails happen on the cheapest model:** `gpt-4o-mini` regularly calls `read(<chunk_id>)` on its first attempt instead of `read(<path_part_id>)` from a `search_knowledge` hit. KS's `read` returns 404 on chunk_ids, the recipe retries, and the model usually self-corrects within 4 attempts (per `retries=4, output_retries=4` on every Agent). When it doesn't, the recipe surfaces `Tool 'read' exceeded max retries`. The fix is on the KS side ([RFC](RFC_KS_MCP_HANDHOLDING.md) item #1: have `search_knowledge` return chunk text directly so no second `read` round-trip is needed).

**Practical recommendation for now:**

```bash
# Cheap path (good enough for ~73% first-shot, ~98% with retries):
MODEL=gpt-4o-mini uv run python scripts/bulk_verify_recipes.py --out report.json
# Re-run failures:
FAILS=$(jq -r '.results[] | select(.status!="pass") | .recipe' report.json | paste -sd,)
MODEL=gpt-4o-mini uv run python scripts/bulk_verify_recipes.py --only "$FAILS" --out report-retry.json

# Reliable path (single shot, ~95% pass, ~10x cost):
MODEL=gpt-4o uv run python scripts/bulk_verify_recipes.py --out report.json
```

## What's verified end-to-end from a clean clone

- `make install` succeeds and produces `.venv/bin/ks-mcp` (verified 2026-04-28).
- `import pydantic_ai, ksapi, llama_index.core` works in the fresh `.venv`.
- `recipes/icd10_coder/recipe.py` runs against `api.knowledgestack.ai` with no `KS_MCP_COMMAND` override — captured JSON output above.
- `scripts/seed_unified_corpus.py` is idempotent and ingests 34 real PDFs/PPTX/XLSX into a tenant.

## What's still aspirational

- **Path A (shared cookbook tenant)** — needs a public read-only KS tenant + invite flow. Tracked in `CHANGELOG.md` as next-up.
- **PyPI publishing of `knowledgestack-mcp`** — currently a git dep. Not blocking, but a `uvx knowledgestack-mcp` one-liner would be cleaner once published.
- **Flagships (44)** — 17 already refactored to the no-FOLDER_ID pattern; remainder pending the same bulk sweep.
