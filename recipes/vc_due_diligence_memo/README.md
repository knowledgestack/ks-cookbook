# VC due-diligence memo

One-line pain: a VC associate spends a week turning a data-room + market
corpus into a partner-ready IC memo — team, market, product, traction,
competition, terms, risks — and half the claims ship without citations.

```bash
uv run python recipes/vc_due_diligence_memo/recipe.py \
  --company "Paloma Networks" --round "Series A"
```

This recipe reads the data room (pitch, financial model, customer refs,
market report, team bios) + any prior competitive notes from your KS
corpus and emits a structured IC memo. Every fact carries a
`[chunk:<uuid>]` citation.

Framework: pydantic-ai. ≤100 LOC.
