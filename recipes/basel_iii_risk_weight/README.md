# basel_iii_risk_weight

Exposure + asset class + counterparty + notional → cited RWA under Basel III
standardised approach.

```bash
uv run python recipes/basel_iii_risk_weight/recipe.py \
  --name "Corp loan 4411" --asset-class corporate --counterparty "BB-rated" --notional 10000000
```
