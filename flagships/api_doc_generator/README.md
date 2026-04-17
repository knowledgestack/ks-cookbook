# Engineering: API Documentation Generator

Endpoint name → developer docs grounded in API spec + style guide.

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
