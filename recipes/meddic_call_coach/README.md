# Meddic Call Coach

> **MEDDIC call coach — call transcript → cited MEDDIC coverage + gaps.**

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

Pain point: AEs miss MEDDIC fields on discovery calls (Metrics, Economic
buyer, Decision criteria, Decision process, Identify pain, Champion). This
recipe scores coverage from the transcript and flags gaps with citations to
your sales playbook.

Framework: pydantic-ai. Tools: list_contents, search_knowledge, read.
Output: stdout (JSON).

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

| `--call-name` | str | yes | — |  |

| `--transcript-file` | str | yes | — |  |


**Sample inputs available** in `sample_inputs/`:

- `discovery_call_001.txt`

## Output schema

`MEDDICReport` — pydantic model emitted as JSON to stdout.

| Field | Type |
|---|---|

| `call` | `str` |

| `fields` | `list[MEDDICField]` |

| `overall_grade` | `str` |

| `top_3_followups` | `list[str]` |

## Run

```bash
uv run python recipes/meddic_call_coach/recipe.py \
    --call-name "demo" \
    --transcript-file recipes/meddic_call_coach/sample_inputs/discovery_call_001.txt
```

## Live verified output

Verified end-to-end against `api.knowledgestack.ai` on **2026-04-28** with `MODEL=gpt-4o-mini` (~70.2s):

```json
{
  "call": "demo",
  "fields": [
    {
      "field": "identify_pain",
      "coverage": "strong",
      "evidence_in_call": "Average resolution time is 4 hours for field techs to get engineering documents, leading to financial losses due
```

Every `chunk_id` is a verbatim UUID from a `[chunk:<uuid>]` marker; snippets and document names are real chunk content from the ingested corpus.

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
recipes/meddic_call_coach/
├── README.md            ← you are here
├── recipe.py            ← agent + schema (no FOLDER_ID env vars)

└── sample_inputs/

    └── discovery_call_001.txt

```
