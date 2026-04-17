# Default loan request

Passed as CLI args to `make demo-credit-memo`:

- `BORROWER="Riverway Logistics LLC"`
- `LOAN_AMOUNT=750000`

A senior secured term facility for a regional trucking company. The corpus
(see `../README.md`) contains the bank's credit policy, three years of
Riverway financials, the business plan, and industry benchmarks.

## Use with your own borrower

```bash
BORROWER="Acme Co" LOAN_AMOUNT=2500000 make demo-credit-memo
```
