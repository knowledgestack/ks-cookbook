# Banking: Loan Covenant Monitor

Reads a borrower's quarterly financial report, compares against loan covenants
in the credit agreement, and flags breaches or near-breaches with citations.

## Data sources

All corpus content is sourced from real public data:

- **Credit agreement covenants** adapted from SEC EDGAR public filings:
  CKX Inc. / UBS Revolving Credit Agreement (SEC File 000119312506107949,
  Exhibit 10.1); Tenneco Inc. Second Amendment (SEC File 000119312520041262,
  Exhibit 10.2); LSTA MCAPs (May 2023 public edition).
- **Quarterly financials** adapted from Cloudflare, Inc. FY2025 10-K
  (SEC CIK 0001477333), scaled to a hypothetical mid-market borrower.

## Run

```bash
# One-time: seed the covenant corpus into your KS tenant.
cd ks-backend
uv run --env-file .env.e2e python seed/seed_covenant_corpus.py
# (prints CORPUS_FOLDER_ID)

# Then, from the cookbook:
cd knowledgestack-cookbook
make demo-covenant-monitor  # defaults: BORROWER="Nimbus Networks, Inc."
```

Output: `covenant-report.md` with per-covenant analysis, compliance status
(COMPLIANT/WARNING/BREACH), cure rights, and chunk-level citations.

## What's in the corpus

2 documents seeded under `/shared/cookbook-banking-covenants/Nimbus`:

| Doc | Purpose |
|---|---|
| `credit_agreement_covenants` | Full credit agreement with defined terms (EBITDA, leverage ratio, etc.), financial covenants with step-down schedules, cure rights, events of default. |
| `nimbus_q4_2025_financials` | Quarterly financial report with balance sheet, income statement, EBITDA reconciliation, covenant compliance summary, and debt schedule. |

## Framework

**LangGraph** ReAct agent with KS MCP tools. The agent reads both documents,
extracts each covenant's required threshold, compares to the actual reported
value, and produces a structured compliance report in Markdown.

## Bring your own data

Replace the corpus with your borrower's real credit agreement and financials:

1. Modify `seed/seed_covenant_corpus.py` in ks-backend with your documents.
2. Pass `--corpus-folder <your-folder-id>`.

The agent code is corpus-agnostic.
