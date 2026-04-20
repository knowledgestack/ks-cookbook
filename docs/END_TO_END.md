# End-to-end: install → seed → run → verify

This page walks a developer from a clean checkout to a cited output from any
of the 132 use cases, in four commands. If anything diverges from what you
see here, open an [issue](https://github.com/knowledgestack/ks-cookbook/issues)
— the doc is wrong until it matches the code.

## 0. Prerequisites

| Requirement | How to check | If missing |
|---|---|---|
| Python 3.11+ | `python --version` | [python.org](https://www.python.org/downloads/) |
| `uv` | `uv --version` | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| Knowledge Stack tenant | [sign up](https://knowledgestack.ai) | N/A |
| `KS_API_KEY` | `echo $KS_API_KEY` | tenant dashboard → Developer → API keys |
| `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` | `echo $OPENAI_API_KEY` | provider dashboard |

## 1. Install

```bash
git clone https://github.com/knowledgestack/ks-cookbook.git
cd ks-cookbook
cp .env.example .env
$EDITOR .env        # fill in KS_API_KEY + LLM key
make setup          # uv sync --all-packages + check-env
```

`make setup` succeeds only when `check-env` sees all required keys. The same
check runs as a dependency of every `demo-*` and `seed-*` target.

## 2. Smoke-test the catalog (no tenant required)

```bash
make smoke
```

Expected tail:

```
Smoke test: 131/131 passed, 0 failed, 1 skipped (env-guarded).
```

This runs `python recipe.py --help` on every recipe and `--help` on every
flagship's CLI entrypoint. It catches broken imports, argparse configs,
pydantic schema errors, and shared-module regressions — the failures you'd
otherwise hit one at a time.

It does **not** call the MCP server, so it's the fastest way to confirm a
branch hasn't regressed the catalog.

## 3. Seed a minimal public corpus (one-time, per tenant)

Every recipe needs *something* to cite against. The cookbook ships a tiny
per-vertical seed pack — one representative fixture doc per vertical — to
prove the plumbing works before you load your real corpus.

```bash
# Pick any existing FOLDER in your tenant (root works). Grab its path_part_id.
export FOLDER_ID=<uuid-of-a-folder-in-your-tenant>

# Seed every vertical, or just one.
make seed-public-corpus FOLDER_ID=$FOLDER_ID
# or:
make seed-public-corpus FOLDER_ID=$FOLDER_ID VERTICAL=healthcare
```

Output (stdout) prints the env-var lines you should paste into `.env`:

```
POLICIES_FOLDER_ID=ab926019-...
CLINICAL_FOLDER_ID=7b5a09d2-...
LEGAL_CORPUS_FOLDER_ID=5fa0e0af-...
ENERGY_FOLDER_ID=e1c3...
GOV_FOLDER_ID=...
HR_FOLDER_ID=...
FINANCE_FOLDER_ID=...
INSURANCE_FOLDER_ID=...
REGULATORY_FOLDER_ID=...
```

Vertical env-var conventions are stable across the catalog — see the top of
any recipe's `recipe.py` for which `*_FOLDER_ID` it reads.

### Swapping to real public corpora

The seed pack is a fixture, not a benchmark. For real evaluation, ingest from
the canonical public sources — the cookbook recipes were designed against
these:

| Vertical | Public corpus | URL |
|---|---|---|
| Healthcare — ICD-10 | CMS ICD-10-CM files | `https://www.cms.gov/medicare/icd-10/2026-icd-10-cm` |
| Healthcare — Drug labels | DailyMed | `https://dailymed.nlm.nih.gov/dailymed/` |
| Banking — Financial filings | SEC EDGAR | `https://www.sec.gov/edgar` |
| Banking — Regulations | Basel III (BIS) | `https://www.bis.org/bcbs/basel3.htm` |
| Legal — Contracts | CUAD dataset | `https://www.atticusprojectai.org/cuad` |
| Legal — Dockets | PACER / CourtListener | `https://www.courtlistener.com/` |
| Legal — Patents | USPTO bulk data | `https://bulkdata.uspto.gov/` |
| Insurance — Forms | ACORD (via members) + NAIC filings | `https://content.naic.org/` |
| Energy | DOE OpenEnergy + state RRCs | `https://openei.org/`, `https://www.rrc.texas.gov/` |
| Government | SAM.gov + Regulations.gov | `https://sam.gov/`, `https://www.regulations.gov/` |
| Tax | IRS Code + Regs | `https://www.irs.gov/` |

Ingest these into your tenant with the SDK's `ingest_document` — the same
call the seeder uses. Swap the corresponding `*_FOLDER_ID` env var to your
larger folder and every recipe picks it up without code changes.

## 4. Run a use case

### A flagship (produces a .md / .docx / .xlsx artifact)

```bash
make demo-credit-memo    # or demo-compliance, demo-lease-abstract, …
make help                # list every demo target
```

Output land next to the flagship's source, e.g.
`flagships/credit_memo_drafter/sample_output.md`. Every artifact contains
`[chunk:<uuid>]` citations that resolve against your tenant.

### A recipe (prints JSON / writes a single file)

```bash
uv run python recipes/icd10_coder/recipe.py --note-file sample-note.txt
uv run python recipes/compensation_band_check/recipe.py \
    --role "Staff SWE" --level Staff --location NYC --proposed "$240,000"
uv run python recipes/version_drift_review/seed.py         # seeds 3 versions
uv run python recipes/version_drift_review/recipe.py --doc-id <id>
```

Every recipe's header docstring names the framework, tools used, and output
format.

## 5. Verify the output

A "working" run means three things:

1. **Exit 0**. If a recipe's pydantic schema rejected the LLM output, it
   won't exit 0 — that's the signal your retrieval didn't surface enough
   context. Re-seed or widen the corpus.
2. **≥1 citation per output**. Every recipe's result type declares
   `citations: list[Citation] = Field(..., min_length=1)` (or embeds
   `Citation` inside a required nested model). An ungrounded output is
   physically rejected at parse time.
3. **Real `chunk_id`s**. Copy a `chunk_id` from the JSON, plug into the
   MCP `read` tool or the KS dashboard's chunk viewer. If it resolves to
   the snippet you see in the output, the citation is genuine.

If any of these fails, the first debugging move is:

```bash
# Is MCP reachable at all?
uv run python -c "from mcp import ClientSession, StdioServerParameters; print('ok')"

# Can I list folders under the folder I set?
uv run python recipes/policy_qa/recipe.py --question "test"   # simplest recipe
```

## What "end-to-end" guarantees, honestly

| Layer | Verified by | Signal |
|---|---|---|
| Python imports | `make smoke` | fail-on-any-import-error |
| CLI arg schema | `make smoke` | fail-on-argparse-error |
| Pydantic schemas | `make smoke` | fail-on-schema-build-error |
| MCP reachability | run any recipe with real `KS_API_KEY` | network / auth error surfaces |
| Corpus retrieval | `seed-public-corpus` + run a recipe | citations returned |
| LLM grounding | run a recipe; inspect `citations[].chunk_id` | chunks resolve in `read` |
| Citation truthfulness | compare `citations[].snippet` to `read(chunk_id)` | human review |

Pieces 1-5 can be fully automated; 6-7 require a tenant and a human to
spot-check. Every recipe prompts the LLM with an explicit "never fabricate
UUIDs" constraint, but the only truthful verification is comparing the
returned snippet to the `read` tool's output.

The **nightly canary** (`.github/workflows/canary.yml`) exercises pieces 4-6
against a dedicated staging tenant — one-time setup in
[CANARY_SETUP.md](CANARY_SETUP.md).

## When things go wrong

- **`make smoke` fails after your change** — run `make lint` and
  `uv run python scripts/smoke_recipes.py --verbose` to see which recipe.
- **A recipe hangs** — the MCP stdio subprocess is waiting on an LLM tool
  call. Check `KS_API_KEY` + LLM key; tail your tenant's request logs.
- **A recipe returns `ValidationError`** — the LLM returned something the
  pydantic schema rejected. Usually means retrieval was empty. Widen the
  folder or seed more fixtures.
- **Citations look made-up** — resolve the `chunk_id` via `read`. If the
  chunk doesn't exist in the tenant, the model fabricated. Tighten the
  system prompt or switch to a larger model; file an issue with the offending
  recipe name.
