# cashflow_anomaly_detector

Bank CSV → cited anomalies (duplicate vendors, weekend ACH bursts, above-
threshold cash) + suggested controls grounded in AP/AR + policy.

```bash
uv run python recipes/cashflow_anomaly_detector/recipe.py --csv march-bank.csv
```
