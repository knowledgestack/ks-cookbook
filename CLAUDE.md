# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

`ks-cookbook` is a **uv workspace** of 32 flagship agent demos plus a set of lightweight recipes that sit on top of Knowledge Stack. Every flagship uses the same pattern: connect to `knowledgestack-mcp` (stdio), enumerate a corpus folder, read chunks, produce structured output with real `[chunk:<uuid>]` citations, and write a file artifact (`.md` / `.docx` / `.xlsx`).

The `ksapi` dependency is pinned to the **local generated SDK** at `../ks-backend/codegen/ks-backend-python` (see `[tool.uv.sources]` in `pyproject.toml`); the sibling `ks-backend` checkout must exist for `uv sync` to resolve.

## Commands

All targets assume `.env` with `KS_API_KEY` + (`OPENAI_API_KEY` or `ANTHROPIC_API_KEY`).

```bash
make setup                # uv sync --all-packages + check-env
make lint                 # ruff check . (rules: E,F,I,W,UP,B; line-length 88)
make test                 # pytest mcp-python/tests/ only
make help                 # list every demo target
make demo-<name>          # run a single flagship (e.g. demo-credit-memo)
make recipe NAME=<dir> ARGS='...'   # run a recipe from recipes/<dir>/recipe.py
make clean                # delete generated artifacts in repo root
```

Run a single MCP test:

```bash
uv run --package knowledgestack-mcp --extra dev pytest mcp-python/tests/<file>::<test> -v
```

Run a flagship directly (bypasses Makefile defaults):

```bash
uv run --package ks-cookbook-<slug> ks-cookbook-<slug> --help
```

`make check-env` is a dependency of every demo target — it fails fast if `KS_API_KEY` or an LLM key is missing.

## Architecture

### Workspace layout

- `pyproject.toml` at the root defines the uv workspace. Every flagship and `mcp-python` is a member; each has its own `pyproject.toml`, `src/<module>/`, and `[project.scripts]` entrypoint (`ks-cookbook-<slug>`).
- `flagships/<name>/src/<module>/` — each flagship follows the same four-file shape: `__main__.py` (CLI), `agent.py` (prompt + MCP wiring), `schema.py` (pydantic output contract), `sample_inputs/`.
- `recipes/` — short (<100 LOC) single-file patterns. `recipes/_shared/mcp_client.py` exposes `ks_mcp_session()`; recipes use it rather than constructing `MCPServerStdio` by hand.
- `mcp-python/` — the `knowledgestack-mcp` server package. The only MCP server flagships and recipes connect to.

### Flagship runtime flow

1. CLI parses args; resolves `KS_MCP_COMMAND` (defaults to `.venv/bin/ks-mcp`) and `KS_MCP_ARGS`.
2. Agent spawns `MCPServerStdio` with `KS_API_KEY` + `KS_BASE_URL` in env.
3. System prompt hard-codes the MCP workflow: `list_contents(folder_id=<corpus>)` → `read(path_part_id=<uuid>)` → emit structured output whose `Citation.chunk_id` values are copied verbatim from `[chunk:<uuid>]` markers in `read` output.
4. `agent.run()` returns a pydantic model; `__main__.py` renders it to `.md`/`.docx`/`.xlsx` in the repo root.

The `corpus_folder_id` is always threaded as a per-demo env var (e.g. `CORPUS_FOLDER_ID`, `LEGAL_CORPUS_FOLDER_ID`, `AUDIT_CORPUS_FOLDER_ID`) with a seeded default in the Makefile — overriding it points the same agent at a different tenant folder.

### MCP tool surface (read-only, v1)

`search_knowledge`, `search_keyword`, `read`, `read_around`, `list_contents`, `find`, `get_info`, `view_chunk_image`, `get_organization_info`, `get_current_datetime`. Writes are intentionally not exposed. Don't add a second MCP server — the KS-only contract is enforced on contribution.

## Contribution rules that affect code changes

From `CONTRIBUTING.md`, enforced by CI:

- **Recipes ≤100 LOC**; anything larger belongs under `flagships/`.
- **Grounding is mandatory** — every recipe/flagship must call at least one MCP tool; no ungrounded LLM output.
- **Citations must be visible** — inline `[chunk:<uuid>]` tags from `read` output, or an explicit `citations` field in the schema.
- **Defaults must just work** — the default seeded policies corpus is `ab926019-ac7a-579f-bfda-6c52a13c5f41`. Recipes run with no flags.
- To scaffold: `cp -r flagships/_template flagships/<name>` (or `recipes/_template recipes/<name>`), then add the member to the root `pyproject.toml` workspace list and a `demo-<name>` target to the Makefile.

## Gotchas

- `ksapi` resolves via a local path. If `uv sync` fails, check that `../ks-backend/codegen/ks-backend-python` exists.
- `chunk_id` UUIDs **must** come from `read` output markers, not be synthesized — multiple system prompts repeat this and CI-style reviewers will reject fabricated citations.
- `make test` only runs the MCP package tests; flagships are not unit-tested (non-deterministic LLM output). Use `--help` as a smoke test.
- Generated artifacts (`credit-memo.md`, `filled.xlsx`, `brief.docx`, etc.) are intentionally checked into the repo root as reference outputs. `make clean` removes them.
