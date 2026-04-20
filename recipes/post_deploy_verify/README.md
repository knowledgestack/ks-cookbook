# post_deploy_verify

Service + change → cited post-deploy verification plan: checks (what, how, red
flag) + rollback triggers. Grounded in SRE runbooks and SLOs.

```bash
uv run python recipes/post_deploy_verify/recipe.py \
  --service ingest-worker --change "enable streaming chunker"
```
