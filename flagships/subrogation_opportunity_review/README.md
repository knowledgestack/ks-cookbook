# Subrogation Opportunity Review (Insurance)

P&C claim file assessed for subrogation recovery potential, citing NAIC Model
902 standards, Acme Insurance subrogation SOP, and policy endorsement language.

**Framework:** raw OpenAI function calling + ksapi SDK

## Data Sources
- NAIC Model Regulation 902-1 (Unfair Property/Casualty Claims Settlement)
- Standard ISO subrogation principles and anti-subrogation doctrine
- Illinois Insurance Code 215 ILCS 5/143b

## Quick Start

```bash
# 1. Seed the corpus (from ks-backend/)
uv run --env-file .env.e2e python seed/seed_insurance_subro_corpus.py

# 2. Run the demo (from knowledgestack-cookbook/)
make demo-subro-review CORPUS_FOLDER_ID=<id-from-step-1>
```

## Output
`subro-review.md` with recovery potential classification (HIGH/MEDIUM/LOW/NONE),
liable party analysis, basis of liability, anti-subrogation check, and estimated
recovery with deductible refund calculation.
