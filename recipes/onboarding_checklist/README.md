# Onboarding checklist

One-line pain: HR copy-pastes policy bits into a new-hire doc for every role.

```bash
uv run python recipes/onboarding_checklist/recipe.py --role "Backend Engineer"
```

Uses `list_contents` → `read` over the policies folder, emits a cited markdown
checklist. No agent framework — raw OpenAI function-calling against MCP stdio.
