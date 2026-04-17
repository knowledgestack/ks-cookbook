# Banking: Credit Memo Drafter

Every commercial loan officer writes a credit memo for every facility. Same
structure, different borrower. This flagship drafts one automatically, grounded
in the bank's credit policy + the borrower's financials + industry benchmarks,
with every risk factor citing a real policy chunk.

## Seed data required

This demo reads from a folder in your Knowledge Stack tenant. You need to create that folder and upload the expected documents **before** running, otherwise retrieval returns nothing and the demo fails with empty output.

**Expected corpus:** Bank credit policy, borrower financials (3y), business plan, industry benchmarks.

Set-up steps:

1. Sign up at [app.knowledgestack.ai](https://app.knowledgestack.ai).
2. Create a folder in the dashboard and copy its folder ID.
3. Upload the documents described above into that folder.
4. Issue an API key from the dashboard and put it in `.env` as `KS_API_KEY`.
5. Run: `CORPUS_FOLDER_ID=<your-folder-id> make demo-credit-memo`

Full corpus matrix for every flagship: [`docs/wiki/seed-data.md`](../../docs/wiki/seed-data.md).

## Run

```bash
# One-time: seed the banking corpus into your KS tenant.
cd ks-backend
uv run --env-file .env.e2e python seed/seed_banking_corpus.py
# (prints CORPUS_FOLDER_ID — default hardcoded below matches the seeded demo tenant)

# Then, from the cookbook:
cd knowledgestack-cookbook
make demo-credit-memo   # defaults: BORROWER="Riverway Logistics LLC" LOAN_AMOUNT=750000
```

Output: `credit-memo.md` with a structured credit memo — recommendation, 1-9
risk rating, risk factors (each cited), recommended covenants, and any policy
exceptions flagged.

## What's in the corpus

4 fake-but-realistic documents seeded under `/shared/cookbook-banking/Riverway`:

| Doc | Purpose |
|---|---|
| `credit_policy` | Bank's underwriting standards, collateral rules, covenant minimums, concentration limits, 1-9 risk rating scale. |
| `borrower_riverway_logistics_financials` | 3 years of balance sheet, income statement, ratios for a regional trucking company. |
| `borrower_riverway_business_plan` | Borrower's loan request + use-of-proceeds + repayment case. |
| `industry_benchmarks_trucking` | ATA-style norms for leverage, DSCR, concentration in regional trucking. |

## Framework

**pydantic-ai** with a strict `CreditMemo` result type. The agent cannot end
with unstructured prose — it must produce the exact schema, including ≥1
citation per risk factor. That's what makes the memo auditable by the bank's
credit committee.

## Bring your own data

Swap the corpus with your bank's real credit policy + your CRM-exported
financials:

1. Point `seed/seed_banking_corpus.py` at your own docs (modify `CORPUS` dict
   or write your own seeder that follows the same pattern).
2. Pass `--corpus-folder <your-folder-id>`.

The agent code doesn't change — the prompt is corpus-agnostic.
