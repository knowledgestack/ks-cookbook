# Pharma: Adverse Event Narrative

Generates a CIOMS-style adverse event narrative grounded in drug labels and
pharmacovigilance SOPs. Uses **LangGraph** ReAct agent.

## Run

```bash
# 1. Seed the pharma PV corpus
cd ks-backend
uv run --env-file .env.e2e python seed/seed_pharma_pv_corpus.py

# 2. From the cookbook
cd knowledgestack-cookbook
make demo-ae-narrative EVENT="Patient experienced severe hypoglycemia" DRUG="semaglutide"
```

Output: `ae-narrative.md` with CIOMS narrative, causality assessment, and citations.
