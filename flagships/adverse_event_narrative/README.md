# Pharma: Adverse Event Narrative

Generates a CIOMS-style adverse event narrative grounded in drug labels and
pharmacovigilance SOPs. Uses **LangGraph** ReAct agent.

## Seed data required

This demo reads from a folder in your Knowledge Stack tenant. You need to create that folder and upload the expected documents **before** running, otherwise retrieval returns nothing and the demo fails with empty output.

**Expected corpus:** Drug label (SmPC), pharmacovigilance SOP, CIOMS narrative template.

Set-up steps:

1. Sign up at [app.knowledgestack.ai](https://app.knowledgestack.ai).
2. Create a folder in the dashboard and copy its folder ID.
3. Upload the documents described above into that folder.
4. Issue an API key from the dashboard and put it in `.env` as `KS_API_KEY`.
5. Run: `CORPUS_FOLDER_ID=<your-folder-id> make demo-ae-narrative`

Full corpus matrix for every flagship: [`docs/wiki/seed-data.md`](../../docs/wiki/seed-data.md).

## Run

```bash
# 1. Seed the pharma PV corpus
cd ks-backend
uv run --env-file .env.e2e python seed/seed_pharma_pv_corpus.py

# 2. From the cookbook
cd knowledgestack-cookbook
make demo-ae-narrative EVENT="Patient experienced severe hypoglycemia" DRUG="semaglutide"
```

Output: `ae-narrative.md` with CIOMS narrative, causality assessment, and citations.
