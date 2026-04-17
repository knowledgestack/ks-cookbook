# Clinical Trial Eligibility (Healthcare)

Patient profile matched against real clinical trial inclusion/exclusion criteria
from ClinicalTrials.gov (NCT03855137 PROGRESS trial, atogepant for chronic migraine),
AHS CGRP clinical guidance, and CMS NCD coverage criteria.

**Framework:** pydantic-ai with MCP

## Seed data required

This demo reads from a folder in your Knowledge Stack tenant. You need to create that folder and upload the expected documents **before** running, otherwise retrieval returns nothing and the demo fails with empty output.

**Expected corpus:** Trial protocol with inclusion/exclusion criteria, clinical guidance, coverage criteria.

Set-up steps:

1. Sign up at [app.knowledgestack.ai](https://app.knowledgestack.ai).
2. Create a folder in the dashboard and copy its folder ID.
3. Upload the documents described above into that folder.
4. Issue an API key from the dashboard and put it in `.env` as `KS_API_KEY`.
5. Run: `CORPUS_FOLDER_ID=<your-folder-id> make demo-trial-eligibility`

Full corpus matrix for every flagship: [`docs/wiki/seed-data.md`](../../docs/wiki/seed-data.md).

## Data Sources
- ClinicalTrials.gov API: NCT03855137 (PROGRESS trial protocol)
- American Headache Society consensus statement (2024)
- CMS National Coverage Determination framework for CGRP inhibitors

## Quick Start

```bash
# 1. Seed the corpus (from ks-backend/)
uv run --env-file .env.e2e python seed/seed_healthcare_trials_corpus.py

# 2. Run the demo (from knowledgestack-cookbook/)
make demo-trial-eligibility CORPUS_FOLDER_ID=<id-from-step-1>
```

## Output
`trial-eligibility.md` with per-criterion ELIGIBLE/INELIGIBLE/UNCERTAIN
determinations, each backed by chunk citations from the trial protocol.
