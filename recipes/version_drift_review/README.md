# version_drift_review

**Pain point.** A policy was tightened in v2, then quietly loosened in v3.
Nobody noticed until an audit. Reviewers want a cited changelog across versions
*and* explicit flags for any control that was weakened.

**What this recipe does.**
1. `seed.py` ingests a demo **Access Control Policy** with three versions that
   drift on purpose — v1 baseline, v2 tightened, v3 regresses (MFA "required" →
   "recommended", 12-char → 8-char passwords, quarterly → annual review, shared
   service accounts re-enabled with manager approval).
2. `recipe.py` lists every version of a document via the KS SDK, pulls each
   version's chunks (with real chunk IDs), asks pydantic-ai for a
   `DriftReport`, and writes a Markdown file with a summary, changelog, and a
   **Regressions** section that cites `[chunk:<uuid>]` tags.

## Run it end-to-end

```bash
# 1. Seed three versions, capture the document id
DOC_ID=$(uv run python recipes/version_drift_review/seed.py)

# 2. Produce the cited drift review
uv run python recipes/version_drift_review/recipe.py --doc-id "$DOC_ID"

# 3. Read the output
cat version-drift.md
```

## Expected output shape

`version-drift.md` will contain three sections:

- **Summary** — one paragraph on what moved.
- **Changelog** — bullet list across all versions.
- **Regressions** — for the v2→v3 drift, entries like "MFA requirement: v2 →
  v3", with the prior and new wording, a "why weakened" note, and real chunk
  citations from both versions.

## Why the SDK, not MCP?

KS MCP v1 is read-only and its `read` tool returns only the **current** version
of a document. To compare historical versions we go through the SDK's
`list_document_versions` and `get_document_version_contents` — citations are
still real chunk UUIDs from the backend. When the write-back MCP ships with
`list_versions` / `read_version` tools, this recipe will flip to MCP-only.

## Don't use this as

- A replacement for an auditor. It's a drafting aid; an LLM can miss a subtle
  regression. Treat the Regressions list as a review queue, not a verdict.
- A diff viewer. It summarizes *semantic* changes; for line-level diffs, use
  `diff`.
