# access_review

Reviews a user/system/role tuple against access-control + data-classification policies, returning a structured verdict (approve / revoke / modify) with cited findings.

```bash
uv run python recipes/access_review/recipe.py
uv run python recipes/access_review/recipe.py \
  --user "alice@" --system "billing-prod" --role "read-only"
```

Framework: pydantic-ai with structured output.
