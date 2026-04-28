# Changelog From Commits

> **Changelog from commits — commit summaries → cited user-facing changelog.**

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

Pain point: Engineers write dense commits; users need the "what changed,
why you care" version. This recipe takes raw commit messages and asks
Knowledge Stack about your product docs / security policies for context,
then produces a Keep-A-Changelog–style entry list with citations where
the change touches documented behavior.

Framework: pydantic-ai. KS access via the knowledgestack-mcp stdio server.
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

| `--version` | str | yes | — |  |

| `--date` | str | yes | — |  |

| `--commits-file` | str | yes | — | Text file with commit subjects (one per line). |


**Sample inputs available** in `sample_inputs/`:

- `commits_v2_4_0.txt`

## Output schema

`Changelog` — pydantic model emitted as JSON to stdout.

| Field | Type |
|---|---|

| `version` | `str` |

| `date` | `str` |

| `entries` | `list[ChangelogEntry]` |

## Run

```bash
uv run python recipes/changelog_from_commits/recipe.py \
    --version v2.4.0 \
    --date 2026-04-27 \
    --commits-file recipes/changelog_from_commits/sample_inputs/commits_v2_4_0.txt
```

## Live verified output

Verified end-to-end against `api.knowledgestack.ai` on **2026-04-28** with `MODEL=gpt-4o-mini` (~16.2s):

```json
{
  "version": "v2.4.0",
  "date": "2026-04-27",
  "entries": [
    {
      "category": "Added",
      "summary": "Introduced a new /v2/ingest endpoint with support for batch uploads.",
      "why_user_cares": "Users can now upload multiple
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
recipes/changelog_from_commits/
├── README.md            ← you are here
├── recipe.py            ← agent + schema (no FOLDER_ID env vars)

└── sample_inputs/

    └── commits_v2_4_0.txt

```
