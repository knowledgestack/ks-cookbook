# Engineering: Incident Runbook Lookup


**Tags:** `engineering` `sre` `runbooks` `incident-response`

PagerDuty alert → matched runbook section with cited remediation steps.

## Seed data required

This demo reads from a folder in your Knowledge Stack tenant. You need to create that folder and upload the expected documents **before** running, otherwise retrieval returns nothing and the demo fails with empty output.

**Expected corpus:** SRE runbooks: DB failover, API 5xx, cert expiry, memory pressure.

Set-up steps:

1. Sign up at [app.knowledgestack.ai](https://app.knowledgestack.ai).
2. Create a folder in the dashboard and copy its folder ID.
3. Upload the documents described above into that folder.
4. Issue an API key from the dashboard and put it in `.env` as `KS_API_KEY`.
5. Run: `CORPUS_FOLDER_ID=<your-folder-id> make demo-runbook`

Full corpus matrix for every flagship: [`docs/wiki/seed-data.md`](../../docs/wiki/seed-data.md).

## Run

```bash
make demo-incident-runbook-lookup
```

Or manually:

```bash
ks-cookbook-runbook --input --alert "High CPU on prod-api-3, 95% for 10 minutes" --corpus-folder $CORPUS_FOLDER_ID --out incident_runbook_lookup.md
```

## Corpus

Grounded in: SRE runbooks (database failover, API gateway 5xx, certificate expiry, memory pressure). Seed with the corresponding `seed_*_corpus.py` script.

## Framework

**pydantic-ai** with structured `RunbookMatch` output type. Every field cites real chunks from the KS tenant.
