# permit_completeness_check

Permit type + applicant + submission summary → cited per-item completeness
check against the ordinance + accept / return / reject decision.

```bash
uv run python recipes/permit_completeness_check/recipe.py \
  --permit-type "residential solar install" --applicant "J. Doe" \
  --submission-summary "site plan yes; structural calcs missing; electrical diagram yes"
```
