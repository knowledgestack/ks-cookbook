# Permission Aware Retrieval

> **Two-tier auth demo — same agent code, different user, different answers.**

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

Pain point every enterprise buyer asks about:
  "If my agent queries our knowledge base, how do I stop it from leaking a
   document to a user who wouldn't otherwise have access?"

KS's answer: identity lives in your IdP (Okta/Azure AD/Google); permissions
live in KS. Your developer holds a dev-issued API key per END-USER, and KS
enforces that user's ``PathPermission`` tuple on every retrieval call.

This recipe runs the SAME ReAct agent loop twice — once with Alice's key
(scoped to access + ir policies), once with Bob's (scoped to sdlc + vendor).
Each agent is asked the same question: "Summarise every policy you can see."

If KS enforcement works, Alice and Bob's answers will be different.

Framework: pydantic-ai (swap to any — auth is about the API key, not the framework).

Seed two users + keys first:
    uv run --env-file .env.e2e python seed/seed_cookbook_users.py

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

This recipe takes no CLI arguments.

## Output schema

Output is JSON printed to stdout.

## Run

```bash
uv run python recipes/permission_aware_retrieval/recipe.py
```

## Live verified output

⚠️ **Last verification (fail, 0.8s)** — see `e2e_recipes_merged.json` for full stderr. This recipe is currently a known-issue; see [`docs/RFC_KS_MCP_HANDHOLDING.md`](../../docs/RFC_KS_MCP_HANDHOLDING.md) for the upstream fix that unblocks small-model first-shot pass rate.

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
recipes/permission_aware_retrieval/
├── README.md            ← you are here
├── recipe.py            ← agent + schema (no FOLDER_ID env vars)

```
