# Sales: Sales Battlecard Generator

Competitor name → battlecard with differentiators, objection handlers, win themes.

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
