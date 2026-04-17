# KS-Only MCP Contract

This repository is intentionally constrained to **Knowledge Stack tooling**.

## Invariants

1. MCP server identity must be `knowledgestack`.
2. MCP command/args must launch the KS server:
- `ks-mcp` (local venv entrypoint), or
- `uvx knowledgestack-mcp`.
3. Do not add secondary MCP servers (filesystem, web, browser, etc.) to recipe
   and flagship agents.
4. Retrieval grounding must come from KS MCP tools only.

## Why

- Keeps examples portable across frameworks.
- Guarantees a single enterprise permission boundary (KS).
- Prevents “works on one client only” multi-server coupling.

## Review checklist for new agents

1. Uses `KS_API_KEY` + `KS_BASE_URL`.
2. Binds only `knowledgestack-mcp`.
3. Calls at least one KS MCP retrieval tool.
4. Emits citations (`[chunk:<uuid>]` or structured citations field).
