# icp_matcher

Score a prospect company against your Ideal Customer Profile with cited
criterion-by-criterion verdicts (hit / miss / unclear) and an A/B/C/DQ tier.

```bash
uv run python recipes/icp_matcher/recipe.py \
  --company "Verdant Sourcing Group" \
  --blurb "Mid-market procurement SaaS, 180 FTE, US + UK."
```

Set `ICP_FOLDER_ID` to point at your ICP folder; the default is the seeded
policies corpus. Every criterion cites real `[chunk:<uuid>]` IDs from the ICP
document.
