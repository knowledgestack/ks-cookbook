# Sprint planner

One-line pain: every sprint planning meeting re-debates capacity, carry-over,
and prioritization from scratch because nobody reads the last 3 retros.

```bash
uv run python recipes/sprint_planner/recipe.py \
  --team "platform" --sprint "2026-S08" --capacity-days 28
```

This recipe reads the team's backlog, last-sprint retro, and any planning
policy doc from your KS corpus; proposes an ordered sprint plan with
owner/size hints and a risks list. Every line cites its source chunk.

Framework: pydantic-ai. ≤100 LOC.
