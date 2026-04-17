# Clinical Trial Eligibility (Healthcare)

Patient profile matched against real clinical trial inclusion/exclusion criteria
from ClinicalTrials.gov (NCT03855137 PROGRESS trial, atogepant for chronic migraine),
AHS CGRP clinical guidance, and CMS NCD coverage criteria.

**Framework:** pydantic-ai with MCP

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
