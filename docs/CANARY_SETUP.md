# Canary setup (one-time, human)

The nightly canary workflow (`.github/workflows/canary.yml`) runs a small set
of representative recipes against a **dedicated staging tenant** every day.
This page covers the one-time provisioning — CI never creates or destroys
tenants.

## Why a dedicated tenant, not prod

- Prod tenants contain real customer data; canary runs should not touch them.
- Canary writes fixtures (via `version_drift_review/seed.py`) — a prod tenant
  would accumulate garbage documents.
- Rate limits and LLM-key quotas should be isolated from real traffic.

## Why CI does not create the tenant

The public Python SDK (`ksapi`) intentionally **does not expose
`create_tenant`** — tenants come from the signup flow or from a superuser-only
path in `ks-backend`. CI creating tenants against a live backend would:
- pollute prod telemetry
- require shipping superuser credentials to GitHub
- make outages harder to debug (which run created which tenant?)

The sane pattern is: **one staging tenant, provisioned once, reused forever.**

## One-time steps

### 1. Create the staging tenant

Either:
- Sign up at your staging URL with an email alias
  (`ks-cookbook-canary@yourco.com`), **or**
- Have a superuser run the minting script in `ks-backend` (the exact command
  lives in that repo — not duplicated here on purpose).

### 2. Create the canary parent folder

Inside the staging tenant, create **one** folder named `cookbook-canary`.
Grab its `path_part_id` from the URL or the KS dashboard's folder view.

### 3. Mint a long-lived API key

Dashboard → Developer → API keys → **Create**. Give it a descriptive name
(`ci-canary-2026-04`), no expiry. This key should only see the canary folder
(least-privilege).

### 4. Set GitHub repo secrets

Repo → Settings → Secrets and variables → Actions → **New repository secret**
for each:

| Secret | Value |
|---|---|
| `KS_STAGING_API_KEY` | The key you just minted |
| `KS_STAGING_BASE_URL` | `https://api.knowledgestack.ai` (or your staging host) |
| `CANARY_FOLDER_ID` | `path_part_id` of `cookbook-canary` folder |
| `OPENAI_API_KEY_CI` | OpenAI key with a **low monthly spend cap** (e.g. $20) |

### 5. Trigger the canary manually once

Actions → Nightly canary → **Run workflow**. Verify it passes. If any secret
is missing, the first step will warn and exit 0 — that's intentional so the
canary doesn't fail loud before setup is done.

## What runs every night

| Step | What it proves |
|---|---|
| `make smoke` | Catalog still imports / parses / builds schemas. |
| `seed_public_corpus.py --vertical policies` | SDK ingest works; fresh fixtures. |
| `policy_qa` | Simplest MCP-only path returns citations. |
| `soc2_evidence` | Deterministic MCP-only pull emits `[chunk:uuid]` tags. |
| `version_drift_review` (seed + recipe) | Document versioning CRUD via SDK + cited drift review. |
| `icd10_coder` | pydantic-ai schema w/ strict regex passes on real LLM output. |

All artifacts are uploaded under
`canary-outputs-<run-id>` with 14-day retention.

## Housekeeping

The canary folder accumulates a small amount of data per run (fresh seed
fixtures + new `version_drift_review` documents). Options:

1. **Do nothing** — storage is cheap for a dozen fixture docs per day.
2. **Weekly cleanup workflow** — add a separate workflow that runs Sunday
   and lists + deletes documents older than 14 days in the canary folder via
   `DocumentsApi.list_documents` + `DocumentsApi.delete_document`. I can
   scaffold this on request.

## Rotating secrets

- API key: mint a new one, add as `KS_STAGING_API_KEY_NEW`, update the
  workflow to use it, verify a run, then delete the old secret and the old
  key in the dashboard.
- OpenAI key: same pattern; rotate every 90 days.

## If the canary starts failing

Three most common causes:

1. **Staging API key expired or revoked.** Mint a new one, update the secret.
2. **LLM key hit rate/spend limit.** Check the OpenAI dashboard; raise cap or
   switch to `MODEL=gpt-4o-mini` inside the workflow env.
3. **Real regression in a recipe.** `make smoke` will pass but the canary
   recipe's assertion (`grep -q 'chunk:'` / `assert citations`) will fail —
   this is the bug you wanted the canary to catch.

Logs + uploaded artifacts for each failed step land on the workflow run page.
