# drug_interaction_checker

Medication list → cited interaction report with severity (none / monitor /
moderate / major / contraindicated) + clinical guidance, grounded in DailyMed.

```bash
uv run python recipes/drug_interaction_checker/recipe.py --meds "warfarin,amiodarone,simvastatin"
```
