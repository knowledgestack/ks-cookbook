# Troubleshooting

Common issues when setting up or running the cookbook. If you hit something not listed here, open an issue with the command you ran and the full traceback.

## Setup

**`uv sync` fails on `ksapi`**
The workspace pins `ksapi` to a local path at `../ks-backend/codegen/ks-backend-python`. If you only cloned `ks-cookbook`, that directory doesn't exist. Either clone `ks-backend` alongside this repo, or remove the `[tool.uv.sources]` block in the root `pyproject.toml` (in which case `uv` will resolve `ksapi` from the registry — only do this if you don't plan to touch flagships that depend on backend SDK types).

**`make check-env` says `KS_API_KEY is not set`**
You haven't filled in `.env`. Run `cp .env.example .env` and paste in your key.

**`make check-env` says `Set OPENAI_API_KEY or ANTHROPIC_API_KEY`**
The agents need one LLM provider key. Only one is required — pick whichever you have.

## Running a demo

**`ks-mcp: command not found`**
The Makefile defaults `KS_MCP_COMMAND` to `.venv/bin/ks-mcp`, which `make setup` installs. If that path is missing, rerun `make setup`. To bypass the workspace build and use the published release:

```bash
KS_MCP_COMMAND=uvx KS_MCP_ARGS=knowledgestack-mcp make demo-credit-memo
```

**Agent hangs on first tool call**
Usually an MCP startup problem. Confirm the server runs standalone:

```bash
uvx knowledgestack-mcp --help
```

If that works but the agent still hangs, run the MCP Inspector with your real key to see what the server is returning:

```bash
npx @modelcontextprotocol/inspector uvx knowledgestack-mcp
```

**`401 Unauthorized` from an MCP tool**
Your `KS_API_KEY` is rejected. Check it's the current key for your tenant and that `KS_BASE_URL` points at the deployment the key was issued for (a SaaS key won't authenticate against a self-hosted URL, and vice versa).

**Empty results from `list_contents` or `search_*`**
The API key's user doesn't have permission to see that folder. This is expected — permission-aware retrieval means a key with no access returns no results, not an error. Re-run with a key whose user can see the corpus, or point the demo at a folder your user does have access to:

```bash
CORPUS_FOLDER_ID=<folder-you-can-see> make demo-<name>
```

**`Citation.chunk_id` validation errors from pydantic**
The model synthesized a UUID instead of copying one from `read` output. The prompt should explicitly forbid this; if you're writing a new flagship, copy the four mandatory prompt rules from [Writing a flagship](writing-a-flagship.md).

**Output artifact is empty or truncated**
The agent ran out of token budget before emitting the structured output. Either raise the model's max-output tokens, narrow the retrieval (smaller `--corpus-folder`, tighter search), or switch to a larger model.

## CI / lint

**`ruff` complains about an import order or unused variable**
Run `make lint` locally; our CI is ruff with `E,F,I,W,UP,B` at line-length 88. Use `uv run ruff check --fix .` to auto-fix most issues.

**`make test` fails without touching MCP code**
`make test` is now a reminder pointing at [knowledgestack/ks-mcp](https://github.com/knowledgestack/ks-mcp) — MCP server tests live there. Flagships aren't unit-tested (non-deterministic LLM output); use `uv run --package ks-cookbook-<slug> ks-cookbook-<slug> --help` as a smoke test.

## Cost and quota

**Demos are burning too many tokens**
The cookbook is optimized for realism, not cost. To keep runs cheap:
- Override `--limit` on `demo-compliance` (default 5 rows).
- Point flagships at smaller folders with `CORPUS_FOLDER_ID`.
- Use a cheaper model via provider env vars when available.

**Rate-limited by OpenAI/Anthropic mid-run**
The pydantic-ai agents don't retry automatically. Rerun the demo; retrieval is idempotent so you won't double-charge for the KS side.
