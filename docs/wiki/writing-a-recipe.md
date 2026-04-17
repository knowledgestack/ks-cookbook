# Writing a recipe

Recipes are short (**≤100 LOC**), single-file patterns that show one useful trick with Knowledge Stack. If your idea is bigger than that, make it a [flagship](writing-a-flagship.md) instead.

The repo ships recipes across a handful of agent frameworks on purpose — pydantic-ai, LangGraph, raw Anthropic, raw OpenAI, MCP-only — to make it easy to copy the style you're already using into your own project.

## Scaffold

```bash
cp -r recipes/_template recipes/<your_name>
$EDITOR recipes/<your_name>/recipe.py
$EDITOR recipes/<your_name>/README.md
uv run python recipes/<your_name>/recipe.py --help
```

Then add a one-line row to [`recipes/INDEX.md`](../../recipes/INDEX.md).

## Frontmatter

The first docstring of `recipe.py` must follow this shape — it's what `INDEX.md` and the contribution bot read:

```python
"""<Title>.

Pain point: <who feels this and why in one sentence>
Framework: <pydantic-ai | LangGraph | raw-openai | raw-anthropic | mcp-only>
Tools used: list_contents, read, ...
Output: <where the result goes — stdout / file / workbook>
"""
```

## Connecting to MCP

Use the shared session wrapper, not a hand-rolled `MCPServerStdio`:

```python
from recipes._shared.mcp_client import ks_mcp_session

async with ks_mcp_session() as session:
    listing = await session.call_tool("list_contents", {"folder_id": folder_id})
    passage = await session.call_tool("read", {"path_part_id": path_part_id})
```

The wrapper honours `KS_MCP_COMMAND` / `KS_MCP_ARGS`, so a reviewer can repoint every recipe at a different MCP build without touching recipe code.

## Hard rules (enforced in CI)

1. **≤100 lines of code.** Docstrings and comments don't count. Bigger → flagship.
2. **Mandatory grounding.** Every recipe calls at least one MCP tool. No ungrounded LLM output.
3. **KS-only MCP contract.** Recipes connect only to `knowledgestack-mcp`. Do not add a second MCP server.
4. **Visible citations.** Inline `[chunk:<uuid>]` tags from `read` output, or an explicit `citations` field in the structured output.
5. **Defaults must just work.** Your recipe runs with no flags against the default seeded policies corpus (`ab926019-ac7a-579f-bfda-6c52a13c5f41`).
6. **No secrets in source.** `KS_API_KEY`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY` come from `.env` only.

## Smoke test

We don't unit-test every recipe (they're short and LLM-non-deterministic). The bar is:

```bash
uv run python recipes/<your_name>/recipe.py --help    # must exit 0
```

If your recipe is complex enough to warrant more, add `recipes/<name>/test_smoke.py` that mocks `ks_mcp_session` with canned responses and asserts the output shape. `flagships/compliance_questionnaire/` shows the pattern.

## Examples to learn from

| Recipe | Framework | Why it's worth reading |
|---|---|---|
| `recipes/policy_qa/` | pydantic-ai | Minimal Q&A over a single folder. |
| `recipes/llama_index_rag/` | LlamaIndex + MCP | How to plug KS into an existing RAG stack. |
| `recipes/permission_aware_retrieval/` | raw MCP | Demonstrates the same code returning different answers for different API keys. |
| `recipes/vendor_security_review/` | raw OpenAI function-calling | Pure OpenAI tool-call style without an agent framework. |
