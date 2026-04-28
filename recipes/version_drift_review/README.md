# Version Drift Review

> **Version drift review — summarize changes across document versions and flag regressions (controls weakened vs. a prior version) with chunk citations.**

## Table of contents

1. [What this recipe does](#what-this-recipe-does)
2. [How it works](#how-it-works)
3. [Sign in to Knowledge Stack](#sign-in-to-knowledge-stack)
4. [Ingest the unified corpus](#ingest-the-unified-corpus)
5. [Inputs](#inputs)
6. [Output schema](#output-schema)
7. [Run](#run)
8. [Live verified output](#live-verified-output)
9. [Troubleshooting](#troubleshooting)
10. [Files](#files)

## What this recipe does

Pain point: A policy was tightened in v2, then quietly loosened in v3. Nobody
noticed until an audit. This recipe lists every version of a document, pulls
each version's chunks (with real chunk IDs), and asks an LLM to produce a cited
changelog plus a list of *regressions* — changes that weaken a control.

Framework: pydantic-ai + ksapi SDK (the MCP v1 `read` tool only returns the
current version, so historical versions are fetched via the SDK; citations are
still real chunk UUIDs from the backend).
Tools used: SDK list_document_versions, SDK get_document_version_contents.
Output: file (version-drift.md).

Companion: ``seed.py`` creates a demo Access Control Policy with three versions
whose drift is deliberately engineered (v2 tightens, v3 regresses).

## How it works

1. The recipe spawns the `knowledgestack-mcp` stdio server (auth via `KS_API_KEY`).
2. A pydantic-ai `Agent` is built with a strict pydantic output schema and `gpt-4o`/`gpt-4o-mini`.
3. The agent asks Knowledge Stack natural-language questions via `search_knowledge`. **It never passes folder UUIDs** — KS finds the right document by content.
4. For every search hit the agent calls `read(path_part_id=<hit>)` to retrieve the full chunk text. The trailing `[chunk:<uuid>]` marker is the citation.
5. The validated pydantic object is printed as JSON to stdout. Every `chunk_id` is a verbatim UUID from a real chunk in your tenant.

## Sign in to Knowledge Stack

**Path A — `ingestion: true` (shared cookbook tenant, fastest)**

Sign in at <https://app.knowledgestack.ai>, request a read-only "Cookbook demo" key, then:

```bash
export KS_API_KEY=sk-user-...
export KS_BASE_URL=https://api.knowledgestack.ai
export OPENAI_API_KEY=sk-...
export MODEL=gpt-4o-mini
```

Skip to step 5 (Run).

**Path B — `ingestion: false` (clone repo, ingest into your own tenant)**

```bash
git clone https://github.com/knowledgestack/ks-cookbook
cd ks-cookbook
make install
export KS_API_KEY=sk-user-...   # your own KS key
export KS_BASE_URL=https://api.knowledgestack.ai
export OPENAI_API_KEY=sk-...
export MODEL=gpt-4o-mini
```

## Ingest the unified corpus

Path B only — one-time. The bundled `seed/` folder has 34 real public-domain documents (CMS ICD-10, NIST 800-53, IRS Pubs, OCC Handbook, KO 10-K, AAPL 2024 proxy, FAR, NERC CIP, FDA Orange Book, BLS XLSX, CDC PPTX, …). Create a parent folder in your tenant via the UI, then:

```bash
make seed-unified-corpus PARENT_FOLDER_ID=<your-folder-uuid>
```

## Inputs

| Flag | Type | Required | Default | Help |
|---|---|---|---|---|

| `--doc-id` | str | yes | — | Document ID (run seed.py to create a demo). |

| `--out` | str | no | — |  |

## Output schema

`DriftReport` — pydantic model emitted as JSON to stdout.

| Field | Type |
|---|---|

| `summary` | `str` |

| `changes` | `list[str]` |

| `regressions` | `list[Regression]` |

## Run

```bash
uv run python recipes/version_drift_review/recipe.py \
    --doc-id "demo" \
    --out "demo"
```

## Live verified output

⚠️ **Last verification (fail, 1.1s)** — see `e2e_recipes_merged.json` for full stderr. This recipe is currently a known-issue; see [`docs/RFC_KS_MCP_HANDHOLDING.md`](../../docs/RFC_KS_MCP_HANDHOLDING.md) for the upstream fix that unblocks small-model first-shot pass rate.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `Set KS_API_KEY and OPENAI_API_KEY.` | Export both env vars before running. |
| `Tool 'read' exceeded max retries` | gpt-4o-mini occasionally calls `read(<chunk_id>)` instead of `read(<path_part_id>)`. Re-run; the prompt self-corrects within `retries=4`. Switching to `MODEL=gpt-4o` removes the flake. |
| Empty / non-grounded output | The corpus isn't ingested into your tenant. Run `make seed-unified-corpus PARENT_FOLDER_ID=<uuid>`. |
| `Connection error` from OpenAI | Transient; retry. |
| `request_limit of 50` exceeded | The agent looped too many tools. Re-run; this is rare. |

## Files

```text
recipes/version_drift_review/
├── README.md            ← you are here
├── recipe.py            ← agent + schema (no FOLDER_ID env vars)

```
