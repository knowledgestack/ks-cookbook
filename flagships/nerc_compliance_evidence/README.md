# Energy: NERC CIP Compliance Evidence Pack

Generates a compliance evidence memorandum for a NERC CIP standard
requirement, citing procedures and controls. Uses **pydantic-ai** with
structured output.

## Seed data required

This demo reads from a folder in your Knowledge Stack tenant. You need to create that folder and upload the expected documents **before** running, otherwise retrieval returns nothing and the demo fails with empty output.

**Expected corpus:** NERC CIP standard text, internal evidence packets, audit-response templates.

Set-up steps:

1. Sign up at [app.knowledgestack.ai](https://app.knowledgestack.ai).
2. Create a folder in the dashboard and copy its folder ID.
3. Upload the documents described above into that folder.
4. Issue an API key from the dashboard and put it in `.env` as `KS_API_KEY`.
5. Run: `CORPUS_FOLDER_ID=<your-folder-id> make demo-nerc-evidence`

Full corpus matrix for every flagship: [`docs/wiki/seed-data.md`](../../docs/wiki/seed-data.md).

## Run

```bash
# 1. Seed the NERC CIP corpus
cd ks-backend
uv run --env-file .env.e2e python seed/seed_energy_nerc_corpus.py

# 2. From the cookbook
cd knowledgestack-cookbook
make demo-nerc-evidence STANDARD="CIP-007-6" REQUIREMENT="R2"
```

Output: `nerc-evidence.md` with evidence items, gap analysis, and auditor notes.
