# Knowledge Stack Cookbook

Build production-style, citation-backed enterprise agents on top of Knowledge Stack.

This repo contains 32 runnable flagship demos and a growing set of lightweight recipes across banking, legal, accounting, healthcare, insurance, real estate, sales, HR, engineering, government, pharma, and energy. Each flagship is designed to show the same core pattern:

- retrieve permission-filtered source material from Knowledge Stack
- force structured output through a schema
- attach real chunk citations to non-trivial claims
- write a usable artifact such as `.md`, `.docx`, or `.xlsx`

[Give the repo a star](https://github.com/knowledgestack/ks-cookbook) if this is useful. Starring helps more builders find the project and signals which flagships and recipes we should expand next.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![Flagships](https://img.shields.io/badge/flagships-32-green)](https://github.com/knowledgestack/ks-cookbook/tree/main/flagships)

## Why this repo exists

Most AI demos stop at "here is a chat response." Enterprise teams need something stricter:

- outputs that can be reviewed by legal, finance, compliance, operations, or engineering
- citations that point back to the underlying source material
- permission-aware retrieval so the same agent behaves differently for different users
- patterns that are easy to copy into real internal tooling

Knowledge Stack handles the data layer. This cookbook shows how to build the agent layer on top.

## What Knowledge Stack does

Knowledge Stack is a permission-aware retrieval layer for enterprise agents. You upload your documents, organize them into folders, assign access controls, and then let your agent read only what the current user is allowed to see.

The demos in this repo use the `knowledgestack-mcp` server to expose a stable read-side tool surface to agent frameworks.

```text
Your agent
  -> knowledgestack-mcp
  -> Knowledge Stack API
  -> permission-filtered documents and chunks
  -> structured output with citations
```

This means you can keep your preferred orchestration layer and still get:

- tenant isolation
- per-user and per-folder visibility rules
- version-aware retrieval
- document, section, and chunk-level reads
- grounded outputs that cite real chunk IDs

## Quickstart

### 1. Prerequisites

- Python `3.11+`
- `uv`
- a Knowledge Stack API key
- an OpenAI or Anthropic API key

### 2. Clone and configure

```bash
git clone https://github.com/knowledgestack/ks-cookbook.git
cd ks-cookbook
cp .env.example .env
```

Fill in `.env`:

```env
KS_API_KEY=sk-user-...
KS_BASE_URL=https://api.knowledgestack.ai
OPENAI_API_KEY=sk-proj-...
# or
ANTHROPIC_API_KEY=...
```

### 3. Install everything

```bash
make setup
```

That installs every workspace package into `.venv`, validates env vars, and gets the cookbook ready to run.

### 4. Run a first flagship

```bash
make demo-credit-memo
```

Expected result:

- the flagship runs through the MCP server against the sample tenant corpus
- it writes a file artifact in the repo root
- you get a developer-friendly output such as `credit-memo.md`

Try a few more:

```bash
make demo-contract-obligations
make demo-rev-rec-memo
make demo-prior-auth
make demo-compliance
make demo-earnings-risk
```

To see the full target list:

```bash
make help
```

## Output examples

These are not toy console logs. The flagships write artifacts a team could actually inspect.

Each flagship writes its output into its own package directory as `sample_output.<ext>`:

- `flagships/credit_memo_drafter/sample_output.md` — cited borrower risk memo
- `flagships/contract_obligation_extractor/sample_output.md` — obligations extracted from an MSA
- `flagships/rev_rec_memo/sample_output.md` — ASC 606 position memo
- `flagships/prior_auth_letter/sample_output.docx` — clinical prior-auth submission
- `flagships/compliance_questionnaire/sample_output.xlsx` — auto-completed CAIQ questionnaire
- `flagships/research_brief/sample_output.docx` — research brief built from KB evidence
- `flagships/csv_enrichment/sample_output.csv` — CSV enriched from KB content

Every output lives beside the flagship that produced it.

## Repo map

```text
flagships/<name>/
  README.md              # flagship-specific walkthrough
  pyproject.toml         # package metadata + entrypoint
  src/<module>/
    __main__.py          # CLI entry
    agent.py             # prompt + MCP interaction
    schema.py            # structured output contract
  sample_inputs/         # default demo inputs

recipes/
  INDEX.md               # lightweight patterns and starter recipes

mcp-python/
  README.md              # Python MCP server package details
```

There are currently 32 flagship packages in the workspace and each one is independently runnable.

## How a flagship is structured

A typical flagship follows this flow:

1. Accept a business input such as a borrower name, endpoint, alert, contract, or patient scenario.
2. Connect to `knowledgestack-mcp`.
3. Search, list, and read the relevant folder contents from Knowledge Stack.
4. Ask the model to produce a schema-constrained answer grounded in that source material.
5. Write the output artifact to disk.

The important part is that the retrieval layer and citation discipline are reusable. Once you understand one flagship, the rest are easy to adapt.

## Flagships by vertical

The repo currently includes 32 flagship demos:

### Banking and financial services

- `make demo-credit-memo`
- `make demo-covenant-monitor`
- `make demo-kyc-review`
- `make demo-earnings-risk`

### Legal

- `make demo-contract-obligations`
- `make demo-msa-redline`

### Accounting and tax

- `make demo-rev-rec-memo`
- `make demo-audit-workpaper`
- `make demo-tax-memo`

### Healthcare

- `make demo-prior-auth`
- `make demo-trial-eligibility`

### Insurance

- `make demo-claim-memo`
- `make demo-subro-review`
- `make demo-policy-compare`

### Real estate

- `make demo-lease-abstract`
- `make demo-zoning-check`

### Sales and revenue

- `make demo-csv`
- `make demo-research`
- `make demo-rfp-draft`
- `make demo-battlecard`
- `make demo-compliance`

### HR, engineering, security, and grants

- `make demo-handbook-qa`
- `make demo-runbook`
- `make demo-jd-generator`
- `make demo-api-doc`
- `make demo-release-notes`
- `make demo-pia`
- `make demo-sow-validator`
- `make demo-grant-compliance`

### Government, pharma, and energy

- `make demo-foia-response`
- `make demo-ae-narrative`
- `make demo-nerc-evidence`

See [INDUSTRIES.md](INDUSTRIES.md) for the broader roadmap and proposed next flagships.

## Core commands

```bash
make setup               # install workspace packages and validate env
make help                # list runnable demos
make lint                # ruff across the workspace
make test                # MCP package tests
make demo-credit-memo    # run one flagship
make demo-csv            # run a lightweight batch enrichment demo
make demo-research       # run the research brief demo
```

## Configuration notes

The cookbook auto-loads `.env` from the repo root.

Relevant variables:

- `KS_API_KEY`: required
- `KS_BASE_URL`: defaults to `https://api.knowledgestack.ai`
- `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`: at least one is required
- `CORPUS_FOLDER_ID`: override the default sample corpus for many demos
- demo-specific variables such as `TOPIC`, `QUESTION`, `BORROWER`, `IN`, and `OUT`

Most flagships ship with seeded defaults, so you can run them without hunting down IDs first. When you want to point a demo at your own data, override the folder ID:

```bash
CORPUS_FOLDER_ID=your-folder-id make demo-credit-memo
```

## Bring your own data

To adapt a flagship to your own tenant:

1. Upload your documents to Knowledge Stack.
2. Identify the target folder.
3. Pass that folder ID into a flagship command.
4. Inspect the generated artifact and verify the citations.

The agent code should stay mostly unchanged. The data source changes; the retrieval and schema pattern does not.

## MCP tools used by the flagships

The demos rely on the `knowledgestack-mcp` read-side tool surface, including:

- `list_contents`
- `find`
- `read`
- `read_around`
- `search_knowledge`
- `search_keyword`
- `get_info`
- `view_chunk_image`
- `get_organization_info`
- `get_current_datetime`

That is the contract most builders should care about when adapting these examples.

## For contributors

This repo is set up to be easy to extend:

- copy a flagship and change the prompt and schema
- keep citations mandatory
- make the output a file artifact, not just stdout
- prefer realistic sample corpora and sample inputs

Useful docs:

- [CONTRIBUTING.md](CONTRIBUTING.md)
- [INDUSTRIES.md](INDUSTRIES.md)
- [recipes/INDEX.md](recipes/INDEX.md)
- [mcp-python/README.md](mcp-python/README.md)

## Developer docs

Full developer wiki lives under [`docs/wiki/`](docs/wiki/README.md):

- [Connecting to Knowledge Stack](docs/wiki/connecting.md) — API keys, base URLs, wiring the MCP server into your agent framework.
- [MCP tool reference](docs/wiki/mcp-tools.md) — the ten read-only tools your agent is allowed to call.
- [Seed data required](docs/wiki/seed-data.md) — what each flagship expects in your tenant, and how to seed it.
- [Configuration](docs/wiki/configuration.md) — every env var and per-demo override.
- [Writing a flagship](docs/wiki/writing-a-flagship.md) — file layout, prompt rules, schema shape, Makefile wiring.
- [Writing a recipe](docs/wiki/writing-a-recipe.md) — ≤100-LOC single-file pattern, frontmatter, shared session helper.
- [Troubleshooting](docs/wiki/troubleshooting.md) — common setup and runtime errors.

To scaffold a new flagship:

```bash
cp -r flagships/_template flagships/<your-name>
```

## Using the cookbook from Claude Desktop or Cursor

If you want your assistant to talk directly to Knowledge Stack, add the MCP server to your config:

```json
{
  "mcpServers": {
    "knowledgestack": {
      "command": "uvx",
      "args": ["knowledgestack-mcp"],
      "env": {
        "KS_API_KEY": "sk-user-..."
      }
    }
  }
}
```

## Community ask

If this repo helped you ship or prototype something useful, [star the repository](https://github.com/knowledgestack/ks-cookbook). It materially helps the project: stars improve discoverability, make it easier to prioritize which examples to deepen, and help validate that open-source, enterprise-grade agent patterns are worth maintaining in the open.

## License

MIT. See [LICENSE](LICENSE).
