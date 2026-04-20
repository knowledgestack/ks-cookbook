# insurance_fraud_pattern

Claim ID + file text → cited fraud-pattern flags (shop-attorney-injury
clusters, …) with severity and per-flag recommended action.

```bash
uv run python recipes/insurance_fraud_pattern/recipe.py \
  --claim-id "CL-2026-04-1234" --file-text "$(cat claim-file.txt)"
```
