# court_docket_monitor

Party + period → cited docket entries (court, filing date, role, status) from
your ingested PACER / state-court filings.

```bash
uv run python recipes/court_docket_monitor/recipe.py --party "Acme Corp" --period "Q1 2026"
```
