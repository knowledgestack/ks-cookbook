# document_versions

**Pain point.** Policies change quarterly. Auditors ask "what version of the
access-control policy was in force on 2025-09-01, and which chunk proves it?"
Teams answer from memory instead of from the system.

**What this recipe does.** Resolves a document by query via `find`, dumps the
raw `get_info` payload (so you can see exactly which version fields the KS MCP
server surfaces today), and pulls the current version's chunks with
`[chunk:<uuid>]` citations — deterministic, no LLM.

```bash
uv run python recipes/document_versions/recipe.py \
  --query "access control policy" \
  --out document-versions.md
```

## v1 surface, honestly

The KS MCP server v1 is **read-only**. Version *metadata* travels in `get_info` /
`list_contents` payloads; mutating version tools (`create_version`,
`promote_version`, `rollback_version`) are on the roadmap in the write-back MCP
and are **not** callable from this recipe. Running this recipe is the right way
to see what version fields your backend actually returns before you build on top
of them.
