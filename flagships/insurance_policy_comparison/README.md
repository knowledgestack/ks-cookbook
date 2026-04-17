# Insurance: Insurance Policy Comparison

Current vs proposed policy → side-by-side analysis with coverage gaps.

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
