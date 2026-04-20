# Default SAR case input

Passed as CLI args to `make demo-sar-narrative`:

- `CASE_ID="SAR-2026-0417"`
- `SUBJECT="Paloma Holdings LLC"`

A fictitious case: rapid structured cash deposits across 6 branches,
outbound wires to a high-risk jurisdiction, no clear business rationale.
The corpus (see `../README.md`) contains 90 days of transactions, the KYC
file, an alert rationale memo, and the FFIEC BSA/AML examination manual
excerpt.

## Use with your own case

```bash
CASE_ID="SAR-2026-0999" SUBJECT="Acme Corp" make demo-sar-narrative
```
