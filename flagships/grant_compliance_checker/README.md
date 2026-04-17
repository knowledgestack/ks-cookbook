# Government: Grant Compliance Checker

Sub-awardee activity → compliance check citing the NOFO + federal regs.

## Seed data required

This demo reads from a folder in your Knowledge Stack tenant. You need to create that folder and upload the expected documents **before** running, otherwise retrieval returns nothing and the demo fails with empty output.

**Expected corpus:** Federal NOFO, 2 CFR 200 Uniform Guidance, sub-awardee reports.

Set-up steps:

1. Sign up at [app.knowledgestack.ai](https://app.knowledgestack.ai).
2. Create a folder in the dashboard and copy its folder ID.
3. Upload the documents described above into that folder.
4. Issue an API key from the dashboard and put it in `.env` as `KS_API_KEY`.
5. Run: `CORPUS_FOLDER_ID=<your-folder-id> make demo-grant-compliance`

Full corpus matrix for every flagship: [`docs/wiki/seed-data.md`](../../docs/wiki/seed-data.md).

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
