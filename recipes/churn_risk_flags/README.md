# churn_risk_flags

Account → cited risk signals (with severity) from QBRs, tickets, CSM notes, +
recommended save play.

```bash
uv run python recipes/churn_risk_flags/recipe.py --account "Northwind Foods"
```

Set `CS_NOTES_FOLDER_ID` to point at your Customer Success notes folder.
