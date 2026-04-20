# api_deprecation_notice

Endpoint + replacement + sunset date → cited deprecation notice (reason,
migration steps, Sunset header) per your deprecation policy.

```bash
uv run python recipes/api_deprecation_notice/recipe.py \
  --endpoint "POST /v1/ingest" --replacement "POST /v2/ingest" --sunset 2026-10-01
```
