# Government: Grant Compliance Checker

Sub-awardee activity → compliance check citing the NOFO + federal regs.

## Run

```bash
make demo-grant-compliance-checker
```

Or manually:

```bash
ks-cookbook-grant-compliance --input --activity "Sub-awardee hired 3 staff and purchased $45K equipment" --corpus-folder $CORPUS_FOLDER_ID --out grant_compliance_checker.md
```

## Corpus

Grounded in: federal grant NOFO + 2 CFR 200 Uniform Guidance + sub-awardee reports. Seed with the corresponding `seed_*_corpus.py` script.

## Framework

**pydantic-ai** with structured `ComplianceCheck` output type. Every field cites real chunks from the KS tenant.
