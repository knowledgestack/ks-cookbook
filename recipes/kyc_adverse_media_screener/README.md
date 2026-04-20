# KYC adverse-media screener

One-line pain: analysts manually Google every new counterparty for negative
news (sanctions hits, enforcement actions, fraud reports, regulatory
orders) and copy-paste findings into the onboarding packet.

```bash
uv run python recipes/kyc_adverse_media_screener/recipe.py \
  --entity "Verdant Sourcing Group LLC"
```

This recipe:

1. `search_knowledge` over your KS corpus (seed with OFAC SDN, OpenSanctions
   snapshots, DOJ press releases, state enforcement bulletins, curated
   news archive).
2. `read` the top hits and extracts event-level flags.
3. Emits a pydantic-validated `AdverseMediaReport` — list of hits with
   severity, source document, and `[chunk:<uuid>]` citations copied verbatim
   from `read` output.

Framework: pydantic-ai. ≤100 LOC, no fabricated chunk IDs.
