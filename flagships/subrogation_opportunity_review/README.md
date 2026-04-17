# Subrogation Opportunity Review (Insurance)


**Tags:** `insurance` `subrogation` `claims`

P&C claim file assessed for subrogation recovery potential, citing NAIC Model
902 standards, Acme Insurance subrogation SOP, and policy endorsement language.

**Framework:** raw OpenAI function calling + ksapi SDK

## Seed data required

This demo reads from a folder in your Knowledge Stack tenant. You need to create that folder and upload the expected documents **before** running, otherwise retrieval returns nothing and the demo fails with empty output.

**Expected corpus:** Subrogation playbook, relevant state-statute excerpts, a sample claim file.

Set-up steps:

1. Sign up at [app.knowledgestack.ai](https://app.knowledgestack.ai).
2. Create a folder in the dashboard and copy its folder ID.
3. Upload the documents described above into that folder.
4. Issue an API key from the dashboard and put it in `.env` as `KS_API_KEY`.
5. Run: `CORPUS_FOLDER_ID=<your-folder-id> make demo-subro-review`

Full corpus matrix for every flagship: [`docs/wiki/seed-data.md`](../../docs/wiki/seed-data.md).

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
