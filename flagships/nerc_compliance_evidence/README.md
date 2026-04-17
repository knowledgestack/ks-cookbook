# Energy: NERC CIP Compliance Evidence Pack

Generates a compliance evidence memorandum for a NERC CIP standard
requirement, citing procedures and controls. Uses **pydantic-ai** with
structured output.

## Run

```bash
# 1. Seed the NERC CIP corpus
cd ks-backend
uv run --env-file .env.e2e python seed/seed_energy_nerc_corpus.py

# 2. From the cookbook
cd knowledgestack-cookbook
make demo-nerc-evidence STANDARD="CIP-007-6" REQUIREMENT="R2"
```

Output: `nerc-evidence.md` with evidence items, gap analysis, and auditor notes.
