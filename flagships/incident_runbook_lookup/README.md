# Engineering: Incident Runbook Lookup

PagerDuty alert → matched runbook section with cited remediation steps.

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
