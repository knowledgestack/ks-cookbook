# change_management_review

Given a proposed production change + risk level, prints a markdown checklist of policy-required gates with `[chunk:<uuid>]` citations.

```bash
uv run python recipes/change_management_review/recipe.py
uv run python recipes/change_management_review/recipe.py \
  --change "Rotate KMS key for billing service" --risk medium
```

Framework: raw OpenAI chat completions + MCP stdio.
