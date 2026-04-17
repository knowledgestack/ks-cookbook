# Professional Services: SOW Scope Validator

Proposed SOW → completeness check against template + methodology.

## Seed data required

This demo reads from a folder in your Knowledge Stack tenant. You need to create that folder and upload the expected documents **before** running, otherwise retrieval returns nothing and the demo fails with empty output.

**Expected corpus:** SOW template, project methodology, rate card.

Set-up steps:

1. Sign up at [app.knowledgestack.ai](https://app.knowledgestack.ai).
2. Create a folder in the dashboard and copy its folder ID.
3. Upload the documents described above into that folder.
4. Issue an API key from the dashboard and put it in `.env` as `KS_API_KEY`.
5. Run: `CORPUS_FOLDER_ID=<your-folder-id> make demo-sow-validator`

Full corpus matrix for every flagship: [`docs/wiki/seed-data.md`](../../docs/wiki/seed-data.md).

## Run

```bash
make demo-sow-scope-validator
```

Or manually:

```bash
ks-cookbook-sow-validator --input --sow "12-week implementation of Acme Platform for 500 users" --corpus-folder $CORPUS_FOLDER_ID --out sow_scope_validator.md
```

## Corpus

Grounded in: SOW template + project methodology + rate card. Seed with the corresponding `seed_*_corpus.py` script.

## Framework

**pydantic-ai** with structured `SOWReview` output type. Every field cites real chunks from the KS tenant.
