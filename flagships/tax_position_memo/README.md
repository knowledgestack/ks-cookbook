# Tax: Tax Position Research Memo

Generates a tax research memorandum citing IRC sections and Treasury
Regulations. Uses **LangGraph** ReAct agent.

## Run

```bash
# 1. Seed the tax research corpus
cd ks-backend
uv run --env-file .env.e2e python seed/seed_tax_corpus.py

# 2. From the cookbook
cd knowledgestack-cookbook
make demo-tax-memo QUESTION="Can we deduct R&D expenditures in the current year?"
```

Output: `tax-memo.md` with analysis steps, authorities cited, risk level, and recommendations.
