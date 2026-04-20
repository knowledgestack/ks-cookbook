# dpa_gap_check

Compares an inbound DPA against your data-protection policy and prints a markdown list of missing/weak clauses with `[chunk:<uuid>]` citations.

```bash
uv run python recipes/dpa_gap_check/recipe.py
uv run python recipes/dpa_gap_check/recipe.py --dpa-file ./vendor_dpa.txt
```

Framework: raw OpenAI chat completions + MCP stdio.
