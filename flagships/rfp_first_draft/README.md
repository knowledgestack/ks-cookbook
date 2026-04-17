# Sales: RFP First Draft

Drafts RFP responses grounded in your company's past proposals and
capability documents stored in Knowledge Stack. Uses **pydantic-ai** with
structured output.

## Run

```bash
# 1. Seed the sales/RFP corpus
cd ks-backend
uv run --env-file .env.e2e python seed/seed_sales_rfp_corpus.py

# 2. From the cookbook
cd knowledgestack-cookbook
make demo-rfp-draft QUESTION="Describe your approach to data security"
```

Output: `rfp-draft.md` with cited responses, confidence ratings, and gap notes.
