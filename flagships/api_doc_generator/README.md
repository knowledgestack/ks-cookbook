# Engineering: API Documentation Generator


**Tags:** `engineering` `api` `documentation` `devex`

Endpoint name → developer docs grounded in API spec + style guide.

## Seed data required

This demo reads from a folder in your Knowledge Stack tenant. You need to create that folder and upload the expected documents **before** running, otherwise retrieval returns nothing and the demo fails with empty output.

**Expected corpus:** OpenAPI spec, integration guide, auth model docs.

Set-up steps:

1. Sign up at [app.knowledgestack.ai](https://app.knowledgestack.ai).
2. Create a folder in the dashboard and copy its folder ID.
3. Upload the documents described above into that folder.
4. Issue an API key from the dashboard and put it in `.env` as `KS_API_KEY`.
5. Run: `CORPUS_FOLDER_ID=<your-folder-id> make demo-api-doc`

Full corpus matrix for every flagship: [`docs/wiki/seed-data.md`](../../docs/wiki/seed-data.md).

## Run

```bash
make demo-api-doc-generator
```

Or manually:

```bash
ks-cookbook-api-doc --input --endpoint "POST /v1/payments" --corpus-folder $CORPUS_FOLDER_ID --out api_doc_generator.md
```

## Corpus

Grounded in: API spec + developer style guide + auth documentation. Seed with the corresponding `seed_*_corpus.py` script.

## Framework

**pydantic-ai** with structured `APIDoc` output type. Every field cites real chunks from the KS tenant.
