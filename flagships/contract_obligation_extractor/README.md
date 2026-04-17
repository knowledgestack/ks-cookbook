# Contract obligation extractor (Legal flagship)

Reads a contract already seeded into your Knowledge Stack tenant and extracts
**every `shall` / `must` / `will` obligation**, categorized by obligation-holder
(Provider, Customer, Mutual), with inline `[chunk:<uuid>]` citations an auditor
can click through.

## Seed data required

This demo reads from a folder in your Knowledge Stack tenant. You need to create that folder and upload the expected documents **before** running, otherwise retrieval returns nothing and the demo fails with empty output.

**Expected corpus:** Sample MSA, DPA, NDA.

Set-up steps:

1. Sign up at [app.knowledgestack.ai](https://app.knowledgestack.ai).
2. Create a folder in the dashboard and copy its folder ID.
3. Upload the documents described above into that folder.
4. Issue an API key from the dashboard and put it in `.env` as `KS_API_KEY`.
5. Run: `LEGAL_CORPUS_FOLDER_ID=<your-folder-id> make demo-contract-obligations`

Full corpus matrix for every flagship: [`docs/wiki/seed-data.md`](../../docs/wiki/seed-data.md).

## Run

```bash
# One-time: seed the sample legal corpus (MSA + DPA + NDA)
PYTHONPATH=. uv run --env-file .env.e2e python seed/seed_legal_corpus.py   # from ks-backend/

# Then, from knowledgestack-cookbook/:
export KS_API_KEY="sk-user-..."
export OPENAI_API_KEY="sk-..."
make demo-contract-obligations

# Or pick a different seeded contract:
uv run --package ks-cookbook-contract-obligations ks-cookbook-contract-obligations \
    --contract-name dpa --out dpa-obligations.md
```

## What it does

1. Spawns `uvx knowledgestack-mcp` over stdio.
2. `list_contents(corpus_folder_id)` → picks the contract whose name matches
   `--contract-name` (default: first document in the folder).
3. `read(path_part_id=<doc>, max_chars=15000)` → returns the full markdown
   with inline `[chunk:<uuid>]` markers.
4. Sends to `gpt-4o-mini` (OpenAI Responses) with a strict system prompt
   demanding verbatim chunk-id citations.
5. Filters out any obligations whose `chunk_id` is not present in the retrieved
   text (no fabrication), validates through pydantic, and renders a markdown
   report grouped by obligation-holder.

## Framework

Raw OpenAI + MCP (no agent framework). This keeps the code <300 LOC and shows
the shortest possible path from MCP retrieval → grounded extraction → file
artifact.

## Bring your own corpus

Upload contracts into any folder in your KS tenant and pass that folder_id via
`--corpus-folder <uuid>` or the `CORPUS_FOLDER_ID` env var. The flagship does
not care whether the contract is an MSA, DPA, NDA, SOW, or anything else — as
long as it contains shall/must/will clauses.
