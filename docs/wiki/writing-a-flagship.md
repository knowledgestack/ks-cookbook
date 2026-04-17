# Writing a flagship

A flagship is a full end-to-end demo: CLI entrypoint, MCP-backed agent, pydantic output schema, a sample input, and a file artifact. Each lives in its own workspace package under `flagships/<name>/`.

## Scaffold

```bash
cp -r flagships/_template flagships/<your_name>
```

Then:

1. Add the new path to the `[tool.uv.workspace].members` list in the root `pyproject.toml`.
2. Rename the package directory under `src/` and update `[project.scripts]` in the new `pyproject.toml`.
3. Add a `demo-<your-slug>` target to the root `Makefile`.
4. `make setup` to re-sync.

## File layout

```text
flagships/<name>/
├── pyproject.toml            # package metadata + [project.scripts] entrypoint
├── README.md                 # one-page walkthrough
├── src/<module>/
│   ├── __main__.py           # argparse → calls agent.draft_*()
│   ├── agent.py              # pydantic-ai Agent + system prompt + MCP wiring
│   └── schema.py             # pydantic output model, includes Citation field(s)
└── sample_inputs/            # tiny fixture inputs the Makefile points at by default
```

## The agent shape

Every flagship's `agent.py` is a minor variation on this:

```python
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio

from .schema import MyOutput

SYSTEM_TEMPLATE = """..."""  # see "Prompt rules" below

async def draft(*, corpus_folder_id: str, model: str, ...) -> MyOutput:
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={"KS_API_KEY": os.environ["KS_API_KEY"],
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(
        model=f"openai:{model}",
        mcp_servers=[mcp],
        system_prompt=SYSTEM_TEMPLATE.replace("__CORPUS_FOLDER_ID__", corpus_folder_id),
        output_type=MyOutput,
    )
    async with agent.run_mcp_servers():
        result = await agent.run(user_prompt)
    return result.output
```

## Prompt rules (non-negotiable)

Copy these into your system prompt verbatim — they're the reason outputs stay grounded:

1. **Enumerate first.** Call `list_contents(folder_id=__CORPUS_FOLDER_ID__)` before anything else.
2. **Pass UUIDs to `read`.** Use the `path_part_id` from `list_contents` results. Do not pass document names.
3. **Copy citation UUIDs verbatim.** `read` returns `[chunk:<uuid>]` markers; every `Citation.chunk_id` in the output must be one of those markers. No synthesis.
4. **No fabrication.** If a fact isn't in the retrieved material, say so and lower confidence rather than inventing numbers.

## Schema shape

Output models always include a `Citation` field (or a list of them) on every non-trivial claim:

```python
from pydantic import BaseModel, Field
from uuid import UUID

class Citation(BaseModel):
    chunk_id: UUID
    quote: str = Field(..., max_length=400)

class RiskFactor(BaseModel):
    description: str
    citations: list[Citation]

class MyOutput(BaseModel):
    summary: str
    risks: list[RiskFactor]
```

The CI reviewer rejects flagships that let the model emit claims without citation fields.

## CLI entrypoint

`__main__.py` should be thin:

```python
def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--corpus-folder", required=True)
    p.add_argument("--out", required=True)
    # ...per-demo args
    args = p.parse_args()
    result = asyncio.run(draft(corpus_folder_id=args.corpus_folder, ...))
    Path(args.out).write_text(render_markdown(result))
```

## Makefile target

Add a seeded-default target so `make demo-<slug>` works without flags:

```makefile
demo-<slug>: check-env ## <One-line description>
	@uv run --package ks-cookbook-<slug> ks-cookbook-<slug> \
		--corpus-folder $${CORPUS_FOLDER_ID:-<seeded-uuid>} \
		--out <slug>.md
	@echo "Output written to: $(abspath <slug>.md)"
```

## Checklist before opening a PR

- [ ] Runs with zero flags against the seeded corpus.
- [ ] Every claim in the output has a `[chunk:<uuid>]` citation or populated `Citation` field.
- [ ] Output is a file artifact (`.md` / `.docx` / `.xlsx`), not just stdout.
- [ ] `make lint` passes.
- [ ] Workspace `pyproject.toml` and `Makefile` updated.
- [ ] README in the flagship folder documents the business use case and sample output.
