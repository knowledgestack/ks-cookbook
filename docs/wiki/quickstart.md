# Quickstart

> **Junior-engineer path: from `git clone` to a working recipe in ~5 minutes.**

There are two ways to run the cookbook. Pick one:

| Path | Use this when… | What you do |
| ---- | -------------- | ----------- |
| **A — pre-ingested tenant** | You just want to see the recipes work against pre-ingested data. | Sign up at <https://app.knowledgestack.ai>, request a read-only "Cookbook demo" key, run any recipe. |
| **B — your own tenant**     | You want to ingest real PDFs/XLSX/PPTX into your **own** tenant and run the recipes against your data. | Clone, run `scripts/seed_unified_corpus.py` against your tenant, then run any recipe. |

## Architecture (one diagram)

```text
                                     ┌────────────────────────┐
   recipes/<name>/recipe.py ───stdio─►   knowledgestack-mcp   │  ── HTTPS ──► api.knowledgestack.ai
   (≤100 LOC, no FOLDER_IDs)         │   (search/read/find)   │                (your tenant)
                                     └────────────────────────┘
              │                                   ▲
              │                                   │
              ▼                                   │
   pydantic-ai Agent ─── tools: search_knowledge ─┘
        │                       └─► read(path_part_id=<hit>)  ─► [chunk:<uuid>] marker
        ▼
   Structured output (pydantic schema) with citations[chunk_id, document_name, snippet]
```

Every recipe asks Knowledge Stack questions in **natural language** (`search_knowledge(query="When does the {company} agreement expire?")`) and follows each hit with `read(path_part_id=<hit>)` to retrieve the chunk text and the `[chunk:<uuid>]` citation marker. There are no folder UUIDs in any recipe — KS finds the right document by content.

## 1. Prerequisites

- Python `3.11+`
- [`uv`](https://docs.astral.sh/uv/) (install: `curl -LsSf https://astral.sh/uv/install.sh | sh`)
- A Knowledge Stack API key — sign in at <https://app.knowledgestack.ai>
- An OpenAI key (`gpt-4o`) — `gpt-4o-mini` skips grounding and produces empty citations

## 2. Clone and configure

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
MODEL=gpt-4o
```

## 3. Install everything

```bash
make setup
```

Installs every workspace package into `.venv` and validates env vars.

## 4a. Path A — shared cookbook tenant

The maintainers run a public-read cookbook tenant where the corpus is pre-ingested. Use the cookbook key from <https://app.knowledgestack.ai> and skip to step 5.

## 4b. Path B — ingest the unified corpus into your own tenant

```bash
# 1. Create a parent folder in your tenant via the UI; copy its path_part_id
# 2. Run the unified ingest:
uv run python scripts/seed_unified_corpus.py \
    --parent-folder-id <YOUR_PARENT_FOLDER_PATH_PART_ID>
```

The script uploads every file under `seed/<vertical>/` (29 real public-domain documents — CMS, NIST, IRS, FDA, FAR, NERC, NAIC, OCC, FinCEN, AWS, SEC EDGAR, BLS XLSX, CDC PPTX, …) and waits for KS ingestion (~4 min/doc).

Format coverage:

- 25 PDF (multi-page, with tables/images)
- 2 PPTX (CDC PowerPoint decks)
- 2 XLSX (BLS occupational data, FRED GDP)

## 5. Run your first recipe

```bash
uv run python recipes/icd10_coder/recipe.py \
    --note-file recipes/icd10_coder/sample_inputs/deid_visit_001.txt
```

You'll see the agent make ~10–20 MCP tool calls (`search_knowledge`, `read`), then emit a JSON `CodingResult` with real `chunk_id`s pointing into `cms_fy2026_icd10cm_coding_guidelines.pdf`.

Other quick wins:

```bash
uv run python recipes/clause_extractor/recipe.py --contract "Apple 2024 proxy"
uv run python recipes/contract_renewal_checker/recipe.py --contract "Donna Huang software development"
uv run python recipes/benefits_enrollment_qa/recipe.py \
    --question "What ERISA disclosures must an employer provide to participants in the company SPD?"
uv run python recipes/aml_sar_narrative/recipe.py --case-id "structuring-cash-deposits"
```

Each recipe folder has its own `README.md` with a captured live output, sign-in steps, and troubleshooting.

To see every demo target: `make help`.

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

## Bring your own data

To adapt a flagship to your own tenant:

1. Upload your documents to Knowledge Stack.
2. Identify the target folder.
3. Pass that folder ID into a flagship command.
4. Inspect the generated artifact and verify the citations.

```bash
CORPUS_FOLDER_ID=your-folder-id make demo-credit-memo
```

The agent code stays unchanged. The data source changes; the retrieval and schema pattern does not.

See [Configuration](configuration.md) for every env var, and [Framework integrations](frameworks.md) for wiring KS into LangChain / LangGraph / CrewAI / Temporal / OpenAI Agents SDK.
