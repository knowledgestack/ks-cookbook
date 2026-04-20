# bcp_drill_plan

Generates a tabletop drill plan grounded in your BCP/DR/IR policies, with success criteria tied to real RTO/RPO chunk citations.

```bash
uv run python recipes/bcp_drill_plan/recipe.py
uv run python recipes/bcp_drill_plan/recipe.py --scenario "ransomware on the file share"
```

Framework: raw Anthropic Messages + MCP stdio.
