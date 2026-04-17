# Professional Services: SOW Scope Validator

Proposed SOW → completeness check against template + methodology.

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
