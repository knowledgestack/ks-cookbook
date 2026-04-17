# HR: Employee Handbook Q&A


**Tags:** `hr` `handbook` `q-and-a`

Employee question → cited answer from the company handbook.

## Seed data required

This demo reads from a folder in your Knowledge Stack tenant. You need to create that folder and upload the expected documents **before** running, otherwise retrieval returns nothing and the demo fails with empty output.

**Expected corpus:** Employee handbook: PTO, remote work, expenses, travel, code of conduct.

Set-up steps:

1. Sign up at [app.knowledgestack.ai](https://app.knowledgestack.ai).
2. Create a folder in the dashboard and copy its folder ID.
3. Upload the documents described above into that folder.
4. Issue an API key from the dashboard and put it in `.env` as `KS_API_KEY`.
5. Run: `CORPUS_FOLDER_ID=<your-folder-id> make demo-handbook-qa`

Full corpus matrix for every flagship: [`docs/wiki/seed-data.md`](../../docs/wiki/seed-data.md).

## Run

```bash
make demo-employee-handbook-qa
```

Or manually:

```bash
ks-cookbook-handbook-qa --input --question "What is our PTO policy?" --corpus-folder $CORPUS_FOLDER_ID --out employee_handbook_qa.md
```

## Corpus

Grounded in: employee handbook (PTO, remote work, expense, travel, code of conduct). Seed with the corresponding `seed_*_corpus.py` script.

## Framework

**pydantic-ai** with structured `HandbookAnswer` output type. Every field cites real chunks from the KS tenant.
