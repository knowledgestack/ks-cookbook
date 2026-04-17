# Insurance: Insurance Policy Comparison


**Tags:** `insurance` `policy-comparison` `coverage`

Current vs proposed policy → side-by-side analysis with coverage gaps.

## Seed data required

This demo reads from a folder in your Knowledge Stack tenant. You need to create that folder and upload the expected documents **before** running, otherwise retrieval returns nothing and the demo fails with empty output.

**Expected corpus:** Current + proposed renewal policy documents and a comparison checklist.

Set-up steps:

1. Sign up at [app.knowledgestack.ai](https://app.knowledgestack.ai).
2. Create a folder in the dashboard and copy its folder ID.
3. Upload the documents described above into that folder.
4. Issue an API key from the dashboard and put it in `.env` as `KS_API_KEY`.
5. Run: `CORPUS_FOLDER_ID=<your-folder-id> make demo-policy-compare`

Full corpus matrix for every flagship: [`docs/wiki/seed-data.md`](../../docs/wiki/seed-data.md).

## Run

```bash
make demo-insurance-policy-comparison
```

Or manually:

```bash
ks-cookbook-policy-compare --input --scenario "Compare current HO-3 vs proposed renewal" --corpus-folder $CORPUS_FOLDER_ID --out insurance_policy_comparison.md
```

## Corpus

Grounded in: insurance policies (current + proposed renewal) + comparison checklist. Seed with the corresponding `seed_*_corpus.py` script.

## Framework

**pydantic-ai** with structured `PolicyComparison` output type. Every field cites real chunks from the KS tenant.
