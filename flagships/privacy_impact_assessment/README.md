# Legal/Security: Privacy Impact Assessment

New feature description → PIA memo citing GDPR + company template.

## Run

```bash
make demo-privacy-impact-assessment
```

Or manually:

```bash
ks-cookbook-pia --input --feature "User analytics dashboard collecting page views + session duration" --corpus-folder $CORPUS_FOLDER_ID --out privacy_impact_assessment.md
```

## Corpus

Grounded in: GDPR Article 35 + company PIA template + data flow documentation. Seed with the corresponding `seed_*_corpus.py` script.

## Framework

**pydantic-ai** with structured `PIAMemo` output type. Every field cites real chunks from the KS tenant.
