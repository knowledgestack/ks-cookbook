# Claim adjudication memo


**Tags:** `insurance` `claims` `coverage-analysis` `p-and-c`

Given a P&C claim narrative (e.g. a kitchen-fire homeowners loss), produce a
**coverage-analysis memorandum** grounded in the applicable policy wording
and the claims-department SOP.

## Seed data required

This demo reads from a folder in your Knowledge Stack tenant. You need to create that folder and upload the expected documents **before** running, otherwise retrieval returns nothing and the demo fails with empty output.

**Expected corpus:** Homeowners policy form, state regulations, adjuster manual.

Set-up steps:

1. Sign up at [app.knowledgestack.ai](https://app.knowledgestack.ai).
2. Create a folder in the dashboard and copy its folder ID.
3. Upload the documents described above into that folder.
4. Issue an API key from the dashboard and put it in `.env` as `KS_API_KEY`.
5. Run: `CORPUS_FOLDER_ID=<your-folder-id> make demo-claim-memo`

Full corpus matrix for every flagship: [`docs/wiki/seed-data.md`](../../docs/wiki/seed-data.md).

## Run

```bash
# Seed the sample corpus:
uv run --env-file ../../ks-backend/.env.e2e python ../../ks-backend/seed/seed_insurance_corpus.py
export CORPUS_FOLDER_ID="<printed by the seed script>"

make demo-claim-memo
```

Output: `claim-memo.md` — a coverage memo with inline `[chunk:<uuid>]`
citations to specific policy provisions.

## Framework

**LangGraph** with `create_react_agent` — a ReAct loop over the KS MCP tools.
The agent iteratively pulls policy sections until it can map each
coverage-analysis step in the SOP to specific wording.
