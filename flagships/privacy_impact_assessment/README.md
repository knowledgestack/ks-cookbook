# Legal/Security: Privacy Impact Assessment

New feature description → PIA memo citing GDPR + company template.

## Seed data required

This demo reads from a folder in your Knowledge Stack tenant. You need to create that folder and upload the expected documents **before** running, otherwise retrieval returns nothing and the demo fails with empty output.

**Expected corpus:** GDPR Article 35 guidance, a company PIA template, sample data-flow documentation.

Set-up steps:

1. Sign up at [app.knowledgestack.ai](https://app.knowledgestack.ai).
2. Create a folder in the dashboard and copy its folder ID.
3. Upload the documents described above into that folder.
4. Issue an API key from the dashboard and put it in `.env` as `KS_API_KEY`.
5. Run: `CORPUS_FOLDER_ID=<your-folder-id> make demo-pia`

Full corpus matrix for every flagship: [`docs/wiki/seed-data.md`](../../docs/wiki/seed-data.md).

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
