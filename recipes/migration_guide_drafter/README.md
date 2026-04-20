# migration_guide_drafter

from-version + to-version → cited migration guide: preflight, step-by-step
(breaking-flag + rollback per step), postflight.

```bash
uv run python recipes/migration_guide_drafter/recipe.py \
  --from-version 3.4 --to-version 4.0
```
