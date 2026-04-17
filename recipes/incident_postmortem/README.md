# Incident post-mortem drafter

Pain: SREs re-derive post-mortem structure per incident; policy refs go stale.

```bash
uv run python recipes/incident_postmortem/recipe.py \
  --incident "Degraded API latency 2026-04-10 14:03-15:22 UTC caused by a misconfigured rate limiter during the v1.68 rollout."
```

Uses **pydantic-ai** with a `PostMortem` schema so the LLM is forced into the
auditor-friendly shape. Writes `post-mortem.md` with cited policy references.
