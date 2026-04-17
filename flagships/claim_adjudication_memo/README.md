# Claim adjudication memo

Given a P&C claim narrative (e.g. a kitchen-fire homeowners loss), produce a
**coverage-analysis memorandum** grounded in the applicable policy wording
and the claims-department SOP.

## Run

```bash
# Seed the sample corpus:
uv run --env-file ../../ks-backend/.env.e2e python ../../ks-backend/seed/seed_insurance_corpus.py
export CORPUS_FOLDER_ID="<printed by the seed script>"

make demo-claim-memo
```

Output: `claim-memo.md` — a coverage memo with inline `[chunk:<uuid>]`
citations to specific policy provisions.

## Framework

**LangGraph** with `create_react_agent` — a ReAct loop over the KS MCP tools.
The agent iteratively pulls policy sections until it can map each
coverage-analysis step in the SOP to specific wording.
