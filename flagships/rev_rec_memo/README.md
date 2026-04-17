# Rev-rec memo (Accounting flagship)


**Tags:** `accounting` `asc-606` `revenue-recognition` `memos`

Given a customer contract summary, drafts a **five-step ASC 606 revenue
recognition memo** grounded in your company's own revenue-recognition policy
and historical judgments (seeded into your Knowledge Stack tenant).

## Seed data required

This demo reads from a folder in your Knowledge Stack tenant. You need to create that folder and upload the expected documents **before** running, otherwise retrieval returns nothing and the demo fails with empty output.

**Expected corpus:** ASC 606 policy, sample MSA, historical judgments memo.

Set-up steps:

1. Sign up at [app.knowledgestack.ai](https://app.knowledgestack.ai).
2. Create a folder in the dashboard and copy its folder ID.
3. Upload the documents described above into that folder.
4. Issue an API key from the dashboard and put it in `.env` as `KS_API_KEY`.
5. Run: `ACCOUNTING_CORPUS_FOLDER_ID=<your-folder-id> make demo-rev-rec-memo`

Full corpus matrix for every flagship: [`docs/wiki/seed-data.md`](../../docs/wiki/seed-data.md).

## Run

```bash
# One-time: seed the sample accounting corpus (policy + sample MSA + judgments memo)
PYTHONPATH=. uv run --env-file .env.e2e python seed/seed_accounting_corpus.py   # from ks-backend/

# Then, from knowledgestack-cookbook/:
export KS_API_KEY="sk-user-..."
export OPENAI_API_KEY="sk-..."
make demo-rev-rec-memo

# Or point at a different contract JSON:
uv run --package ks-cookbook-rev-rec-memo ks-cookbook-rev-rec-memo \
    --in flagships/rev_rec_memo/sample_inputs/globex_contract.json --out my-memo.md
```

## Input shape

A JSON file with:

```json
{
  "customer": "Globex Industries, Inc.",
  "product": "Acme Platform Enterprise",
  "total_contract_value_usd": 220000,
  "contract_summary": "12-month SaaS subscription at $12,500/month plus a $40,000 onboarding fee and 120 hours of optional advanced implementation at $250/hour..."
}
```

## What it does

1. Spawns `uvx knowledgestack-mcp` over stdio.
2. A [pydantic-ai](https://ai.pydantic.dev) `Agent` with `result_type=RevRecMemo`
   iteratively calls `list_contents` + `read` against the seeded policy corpus.
3. Produces a strictly-validated five-step memo (Identify contract / Performance
   obligations / Transaction price / Allocate / Recognize), with inline
   `[chunk:<uuid>]` citations copied verbatim from the policy text.
4. Writes the memo as a markdown file.

## Framework

[pydantic-ai](https://ai.pydantic.dev) + MCP — the agent's `result_type` is the
pydantic `RevRecMemo`, so the LLM is forced into the five-step structure.

## Bring your own corpus

Upload your company's actual ASC 606 policy and any historical-judgment memos
into a KS folder, then pass that `folder_id` via `--corpus-folder <uuid>` or the
`CORPUS_FOLDER_ID` env var. Drop any new customer contract into a JSON file
matching the input shape above and run the demo.
