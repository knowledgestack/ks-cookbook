# Contributing

Thanks for extending the cookbook. The repo's goal is 100+ short, real, cited
recipes and flagship agents on top of **KS-as-a-service** — adding one is a
<1h PR.

## Quick start (10 min)

```bash
cp .env.example .env               # fill KS_API_KEY + OPENAI_API_KEY
make setup                         # installs all workspace packages
cp -r recipes/_template recipes/my_recipe
$EDITOR recipes/my_recipe/recipe.py
$EDITOR recipes/my_recipe/README.md
uv run python recipes/my_recipe/recipe.py --help
```

## Recipe rules

Enforced by CI on every PR:

1. **≤100 lines of code** (docstrings + comments don't count). If it's bigger, it's a demo, not a recipe — put it under `flagships/` instead.
2. **Grounding is mandatory.** Every recipe calls at least one MCP tool via `recipes/_shared/mcp_client.ks_mcp_session()`. No ungrounded LLM output.
3. **KS-only MCP contract.** Recipes/flagships connect only to `knowledgestack-mcp` (server id `knowledgestack`). Do not add secondary MCP servers.
4. **Citations are visible.** Every output includes either inline `[chunk:<uuid>]` tags copied from `read` output, or an explicit `citations` field in structured output.
5. **No secrets in source.** `KS_API_KEY`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY` come from `.env` only. CI scans every PR for leaked keys.
6. **Framework variety is encouraged.** Five of the shipped recipes use five different frameworks on purpose — pydantic-ai, LangGraph, raw Anthropic, raw OpenAI, OpenAI function-calling. Your recipe can use any agent framework; declare it in the frontmatter / `INDEX.md` row.
7. **Defaults must just work.** The recipe runs against the default seeded corpus (folder `ab926019-ac7a-579f-bfda-6c52a13c5f41`) with no extra flags.

## Recipe frontmatter

First docstring of `recipe.py`:

```python
"""<Title>.

Pain point: <who feels this and why in one sentence>
Framework: <pydantic-ai | LangGraph | raw-openai | raw-anthropic | mcp-only>
Tools used: list_contents, read, ...
Output: <where the result goes — stdout / file / workbook>
"""
```

## INDEX.md

After adding your recipe, add a row to [`recipes/INDEX.md`](recipes/INDEX.md). Keep it one line.

## Tests

We don't unit-test every recipe (they're short, LLMs are non-deterministic). Instead:

- **Smoke test**: `uv run python recipes/<name>/recipe.py --help` must exit 0.
- **Mock e2e** (optional): if your recipe is complex, add `recipes/<name>/test_smoke.py` that mocks `ks_mcp_session` with canned responses and asserts the output shape. See `flagships/compliance_questionnaire/` for the pattern.

## Non-recipe contributions

- **New MCP tools** → PR against `mcp-python/src/ks_mcp/tools/`. Must include a respx-mocked test.
- **New flagship demos** (longer end-to-end apps) → `flagships/<name>/` with its own `pyproject.toml`, README, and `Makefile` target.
- **Bug fixes**: always welcome.

## License

By opening a PR you agree your contribution is MIT-licensed.
