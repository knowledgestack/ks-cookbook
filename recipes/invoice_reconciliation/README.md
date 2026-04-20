# invoice_reconciliation

Invoice line + PO + contract → cited 3-way match result with suggested action
(approve / short_pay / hold / reject).

```bash
uv run python recipes/invoice_reconciliation/recipe.py \
  --invoice-line "50 hrs @ \$225" --po "PO-4421" --contract "msa-acme-2025"
```
