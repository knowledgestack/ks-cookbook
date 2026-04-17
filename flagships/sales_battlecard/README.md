# Sales: Sales Battlecard Generator

Competitor name → battlecard with differentiators, objection handlers, win themes.

## Seed data required

This demo reads from a folder in your Knowledge Stack tenant. You need to create that folder and upload the expected documents **before** running, otherwise retrieval returns nothing and the demo fails with empty output.

**Expected corpus:** Product overview, competitive analyses.

Set-up steps:

1. Sign up at [app.knowledgestack.ai](https://app.knowledgestack.ai).
2. Create a folder in the dashboard and copy its folder ID.
3. Upload the documents described above into that folder.
4. Issue an API key from the dashboard and put it in `.env` as `KS_API_KEY`.
5. Run: `CORPUS_FOLDER_ID=<your-folder-id> make demo-battlecard`

Full corpus matrix for every flagship: [`docs/wiki/seed-data.md`](../../docs/wiki/seed-data.md).

## Run

```bash
make demo-sales-battlecard
```

Or manually:

```bash
ks-cookbook-battlecard --input --competitor "Competitor A" --corpus-folder $CORPUS_FOLDER_ID --out sales_battlecard.md
```

## Corpus

Grounded in: product overview + competitive analysis docs. Seed with the corresponding `seed_*_corpus.py` script.

## Framework

**pydantic-ai** with structured `Battlecard` output type. Every field cites real chunks from the KS tenant.
