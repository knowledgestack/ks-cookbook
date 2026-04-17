# Tax: Tax Position Research Memo

Generates a tax research memorandum citing IRC sections and Treasury
Regulations. Uses **LangGraph** ReAct agent.

## Seed data required

This demo reads from a folder in your Knowledge Stack tenant. You need to create that folder and upload the expected documents **before** running, otherwise retrieval returns nothing and the demo fails with empty output.

**Expected corpus:** IRC section text, Treasury Regs, Rev. Ruls, Tax Court opinions.

Set-up steps:

1. Sign up at [app.knowledgestack.ai](https://app.knowledgestack.ai).
2. Create a folder in the dashboard and copy its folder ID.
3. Upload the documents described above into that folder.
4. Issue an API key from the dashboard and put it in `.env` as `KS_API_KEY`.
5. Run: `CORPUS_FOLDER_ID=<your-folder-id> make demo-tax-memo`

Full corpus matrix for every flagship: [`docs/wiki/seed-data.md`](../../docs/wiki/seed-data.md).

## Run

```bash
# 1. Seed the tax research corpus
cd ks-backend
uv run --env-file .env.e2e python seed/seed_tax_corpus.py

# 2. From the cookbook
cd knowledgestack-cookbook
make demo-tax-memo QUESTION="Can we deduct R&D expenditures in the current year?"
```

Output: `tax-memo.md` with analysis steps, authorities cited, risk level, and recommendations.
