# Banking: KYC Onboarding Review


**Tags:** `banking` `kyc` `aml` `compliance`

Given a new customer's submitted documents, checks them against the bank's
KYC/CDD policy and federal regulations, produces a checklist of what's present
vs missing, with risk tier assignment and citations.

## Seed data required

This demo reads from a folder in your Knowledge Stack tenant. You need to create that folder and upload the expected documents **before** running, otherwise retrieval returns nothing and the demo fails with empty output.

**Expected corpus:** Bank CDD policy, sanctions guidance, sample customer onboarding file.

Set-up steps:

1. Sign up at [app.knowledgestack.ai](https://app.knowledgestack.ai).
2. Create a folder in the dashboard and copy its folder ID.
3. Upload the documents described above into that folder.
4. Issue an API key from the dashboard and put it in `.env` as `KS_API_KEY`.
5. Run: `KYC_CORPUS_FOLDER_ID=<your-folder-id> make demo-kyc-review`

Full corpus matrix for every flagship: [`docs/wiki/seed-data.md`](../../docs/wiki/seed-data.md).

## Data sources

All policy and regulatory content is sourced from real public data:

- **FFIEC BSA/AML Examination Manual** — Customer Due Diligence section
  (https://bsaaml.ffiec.gov/manual/AssessingComplianceWithBSARegulatoryRequirements/02)
- **31 CFR 1010.230** — Beneficial ownership requirements for legal entity
  customers (https://www.law.cornell.edu/cfr/text/31/1010.230)
- **FinCEN CDD Final Rule** guidance
  (https://www.fincen.gov/resources/statutes-and-regulations/cdd-final-rule)

The bank's internal KYC policy is modeled on FFIEC guidance. The sample
customer application uses entirely fictitious names and details.

## Run

```bash
# One-time: seed the KYC corpus into your KS tenant.
cd ks-backend
uv run --env-file .env.e2e python seed/seed_kyc_corpus.py
# (prints CORPUS_FOLDER_ID)

# Then, from the cookbook:
cd knowledgestack-cookbook
make demo-kyc-review
```

Output: `kyc-review.md` with a structured checklist, risk tier, risk factors,
pending items, and policy citations.

## What's in the corpus

4 documents seeded under `/shared/cookbook-banking-kyc/Verdant`:

| Doc | Purpose |
|---|---|
| `ffiec_cdd_examination_procedures` | FFIEC BSA/AML Manual CDD section — risk categories, EDD requirements, ongoing monitoring. |
| `beneficial_ownership_31cfr1010_230` | Full text of 31 CFR 1010.230 — beneficial ownership definitions, identification, verification, exemptions. |
| `acme_bank_kyc_policy` | Bank's internal KYC policy — onboarding checklist, risk tiers, EDD procedures, SAR filing. |
| `sample_customer_application` | Verdant Sourcing Group LLC application — beneficial owners, submitted docs, pending items. |

## Framework

**pydantic-ai** with a strict `KYCReview` output type. The agent must produce
a structured checklist with each item citing the specific policy or regulatory
chunk that mandates the requirement.

## Bring your own data

Replace the corpus with your bank's real KYC policy and a customer application:

1. Modify `seed/seed_kyc_corpus.py` in ks-backend with your documents.
2. Pass `--corpus-folder <your-folder-id>`.

The agent code is corpus-agnostic.
