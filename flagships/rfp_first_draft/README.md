# Sales: RFP First Draft


**Tags:** `sales` `rfp` `proposals` `go-to-market`

Drafts RFP responses grounded in your company's past proposals and
capability documents stored in Knowledge Stack. Uses **pydantic-ai** with
structured output.

## Seed data required

This demo reads from a folder in your Knowledge Stack tenant. You need to create that folder and upload the expected documents **before** running, otherwise retrieval returns nothing and the demo fails with empty output.

**Expected corpus:** Past RFP responses, security questionnaire answers, capability docs.

Set-up steps:

1. Sign up at [app.knowledgestack.ai](https://app.knowledgestack.ai).
2. Create a folder in the dashboard and copy its folder ID.
3. Upload the documents described above into that folder.
4. Issue an API key from the dashboard and put it in `.env` as `KS_API_KEY`.
5. Run: `CORPUS_FOLDER_ID=<your-folder-id> make demo-rfp-draft`

Full corpus matrix for every flagship: [`docs/wiki/seed-data.md`](../../docs/wiki/seed-data.md).

## Run

```bash
# 1. Seed the sales/RFP corpus
cd ks-backend
uv run --env-file .env.e2e python seed/seed_sales_rfp_corpus.py

# 2. From the cookbook
cd knowledgestack-cookbook
make demo-rfp-draft QUESTION="Describe your approach to data security"
```

Output: `rfp-draft.md` with cited responses, confidence ratings, and gap notes.
