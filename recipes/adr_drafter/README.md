# adr_drafter

Drafts an Architecture Decision Record grounded in your security/engineering policies, with `[chunk:<uuid>]` citations in the Policy Constraints section.

```bash
uv run python recipes/adr_drafter/recipe.py \
  --decision "Move sessions to Redis" \
  --context "DB session table is a hot spot."
```

Framework: raw Anthropic Messages + MCP stdio.
