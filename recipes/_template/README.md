# _template

Starter for a new recipe.

```bash
cp -r recipes/_template recipes/my_new_recipe
$EDITOR recipes/my_new_recipe/recipe.py
```

Then add it to `recipes/INDEX.md` with one line describing the pain point.

## Rules (enforced by CI)

1. ≤100 lines of actual code (docstrings + comments don't count).
2. Uses at least one MCP tool via `_shared/mcp_client.ks_mcp_session()`.
3. Emits cited output — `[chunk:<uuid>]` tags OR a structured evidence section.
4. No real credentials in the source. `KS_API_KEY` comes from env only.
5. Runs against the default seeded corpus (folder `ab926019-ac7a-579f-bfda-6c52a13c5f41`)
   unless the recipe specifies another tenant/folder.
