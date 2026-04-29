# Shared cookbook demo tenant — design

**Status:** Draft for discussion. Lays out what the maintainer-hosted "Path A" tenant looks like and how a fresh ks-cookbook user gets access in under 60 seconds without ingesting anything themselves.

## Why this exists

Every recipe + flagship README today says:

> **Path A — `ingestion: true` (shared cookbook tenant, fastest)** → request a read-only "Cookbook demo" key…

That promise is currently aspirational. We need to actually stand up that tenant + the access flow, because:

1. **Friction kills first impressions.** Path B (clone, ingest, wait ~4 min/doc × 34 docs = ~2 hours) is fine for serious evaluators but kills casual / drive-by traffic. The cookbook is also a marketing surface — most people will never get past Path B's wait.
2. **Today's "98% pass" rate depends on the user having ingested the same 34 PDFs.** Without a stable shared corpus, "live verified" snapshots in READMEs are a lie for anyone who hasn't run `make seed-unified-corpus`.
3. **The `make demo-credit-memo` story breaks** if the user's tenant doesn't have a "Riverway Bank credit policy" doc with the right name. We've been papering over this with `search_knowledge` so it works against any corpus, but a **canonical** corpus makes outputs reproducible across runs.

## What the tenant looks like

A KS organization the maintainers control, kept stable like a public-read database. Concretely:

| Property | Value |
|---|---|
| Tenant name | `cookbook-demo` (proposed) |
| Slug / URL | `cookbook-demo.knowledgestack.ai` (or just lives under `app.knowledgestack.ai` w/ a special role) |
| Owner | knowledgestack/devrel |
| Document count | 34 (matches `seed/ingest/` exactly — same files, same names, same chunk_ids) |
| Refresh policy | Re-ingested only when `seed/ingest/` changes on `main`. Chunk_ids change on each ingest, so the captured "Live verified" outputs in READMEs ALSO need to be regenerated whenever the demo tenant is re-ingested. CI gate: `make e2e-flagships && make verify-clone N=all` against the demo tenant. |
| Permissions model | Single read-only role; users only see the `cookbook-corpus/` folder tree, not anything else in the org. |
| Rate limits | Per-key: 60 req/min, 1000 req/day. Enforced server-side. |
| Cost | KS bears the storage + ingestion cost (~50 MB across 34 docs is trivial); users bring their own LLM key, so KS owes ~zero per-user inference cost. |

## How users get a key — three options (pick one)

### Option A — Self-serve sign-up, instant key (recommended)

```
User                     app.knowledgestack.ai
  │                                │
  │  GET /cookbook-demo            │
  │  ────────────────────────────► │
  │                                │  if no session: GitHub OAuth
  │  ◄──── redirect to GitHub ──── │  (or magic link to email)
  │                                │
  │  POST OAuth callback ─────────►│
  │                                │  Mint a read-only key
  │                                │  scoped to the cookbook-demo
  │                                │  tenant.
  │  ◄────  token + copy button ── │
  │                                │
  │  copy `KS_API_KEY=sk-user-...` │
  │  paste into terminal           │
```

**Pros:** zero friction, works in 30s, deduplicates by GitHub identity so we can rotate or revoke abusers without nuking everyone.
**Cons:** requires building (or wiring up) the OAuth flow + the read-only-tenant-key minting endpoint.

### Option B — Static demo key in a public repo

A single read-only `KS_API_KEY=sk-cookbook-demo-public-...` baked into `.env.example` and the README.

**Pros:** zero infra to build; works the moment we publish the key.
**Cons:**
- Public abuse attractor — anyone clones the repo and burns through the rate limit.
- Hard to rotate if abused (every README sample, every CI job, breaks).
- Gives a misleading impression that auth doesn't matter.

### Option C — Email-gated invite (Discord / Calendly)

Users post in `#cookbook-demo` on Discord (or fill a form), maintainer replies with a key.

**Pros:** highest-touch — real signal of who's evaluating.
**Cons:** slow (hours to days). Defeats "fastest path" purpose.

**My recommendation:** **Option A**. Discord channel as a fallback for keys that get rate-limited or revoked.

## Maintenance: how the corpus stays in sync

The corpus = `seed/ingest/<vertical>/*.{pdf,xlsx,pptx,docx,csv}` in this repo.

When that folder changes on `main`, a CI job re-ingests into the demo tenant:

```
GitHub Action: on push to main, paths: seed/ingest/**
  ├── checkout
  ├── pip install ksapi
  ├── DELETE old cookbook-corpus folder via DELETE /v1/folders
  ├── re-create cookbook-corpus folder
  ├── upload every file under seed/ingest/<vertical>/
  ├── poll workflow status until all DONE
  ├── chunk_ids in the demo tenant are now stable for the new corpus state
  ├── trigger `make e2e-flagships` against the demo tenant — proves recipes
  │   produce the same shape of output (chunk_ids will differ, but the
  │   structure stays the same)
  └── if anything fails, rollback (re-upload the previous seed/ingest snapshot)
```

For READMEs: the captured "Live verified output" sections show **examples** of citation IDs, not promises that the same UUID will appear. The verifier scans for the *shape* of citations (chunk_id is a UUID, document_name matches a real file in the corpus, snippet substring-matches the chunk), not exact UUID equality.

## Token budget — who pays for the LLM?

KS does **not** pay for LLM inference. Every user runs against their own `OPENAI_API_KEY`. This means:

- **No abuse vector** on the LLM side — KS never spends money on a recipe call.
- **Per-recipe cost transparency**: `gpt-4o-mini` is ~$0.0001 / recipe call. A user running every recipe once = ~$0.01.
- **gpt-5-nano** would drop that to ~$0.00001 / call when supported.

The only KS cost is the per-key **chunks-search** + **path_part read** API calls. Those are ~50 KS API calls per recipe, well within free-tier or near-free pricing.

## Concrete next steps to build this

1. **Decide on Option A vs B vs C.** (Recommendation: A.)
2. **In ks-backend:**
   - Add a `tenant_kind = "cookbook_demo"` flag.
   - Add a `mint_cookbook_key(github_user_id)` endpoint that returns a read-only API key scoped to that tenant + tenant-wide rate limits.
   - Block all WRITE endpoints on cookbook-demo keys (PUT/POST/DELETE → 403).
3. **In ks-frontend:**
   - Add a `/cookbook-demo` landing page with the OAuth → key flow.
   - Show the key once with a copy button; instruct user to paste into `.env`.
4. **In ks-cookbook:**
   - Replace every README's `Path A` block with the actual app.knowledgestack.ai/cookbook-demo URL.
   - Add `make seed-unified-corpus` reference only as a fallback (Path B) — make Path A the default.
5. **In ks-cookbook CI:**
   - On push to main, run `make e2e-flagships` + `make verify-clone N=all` against the demo tenant. Block merges that drop pass rate below a threshold.
6. **Marketing:**
   - Twitter / Discord / blog: "Run any of 152 production-style RAG patterns against a public KS tenant in 30 seconds."

## Estimated effort

| Item | Effort |
|---|---|
| ks-backend: cookbook-demo tenant + mint endpoint | **1 day** (one new tenant kind + a route + tests) |
| ks-frontend: `/cookbook-demo` page + OAuth flow | **1 day** if reusing existing GitHub OAuth on the marketing site; **2 days** if building fresh |
| ks-cookbook: ingest the corpus into the demo tenant | **30 min** (script exists; we just point it at the demo tenant once) |
| ks-cookbook: README rewrites pointing at the real URL | **1 hour** (regenerate via `regenerate_readmes.py` with new template) |
| ks-cookbook: CI job for corpus re-ingest on push | **2 hours** (GitHub Action + `seed_unified_corpus.py` + e2e check) |
| **Total** | **~3 dev-days, single engineer** |

## Open questions

1. **Single demo tenant or per-user tenant?** A single shared tenant is simpler. Per-user tenants (one per GitHub login) gives users their own sandbox to upload extra docs into — closer to a real eval. **My take:** start with single shared, add per-user later if demand emerges.
2. **Document-level provenance for cookbook-demo:** if we re-ingest weekly and chunk_ids change, captured "Live verified output" snippets in READMEs go stale. Should we (a) accept that — the snippets are illustrative, or (b) freeze chunk_ids using a snapshot-and-replay tool? **My take:** (a). The READMEs say "captured 2026-04-28" so a careful reader knows it's a snapshot.
3. **What model do we recommend in the demo flow?** gpt-4o-mini (cheap, ~73% first-shot) vs gpt-4o (reliable, expensive). **My take:** README says `MODEL=gpt-4o-mini` and adds a footnote that gpt-4o is more reliable.
4. **Rate-limit policy:** 60/min / 1000/day per key — generous enough for evaluation, tight enough to prevent scrape attacks?

## TL;DR

Build a **single read-only `cookbook-demo` tenant** in KS, ingest the same `seed/ingest/` corpus, and expose a **GitHub-OAuth-gated `/cookbook-demo` page** that mints a per-user read-only key. ~3 dev-days, eliminates the cookbook's biggest first-run friction, and KS pays ~zero ongoing cost because users bring their own LLM key.
