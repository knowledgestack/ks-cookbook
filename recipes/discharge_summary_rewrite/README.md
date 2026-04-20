# discharge_summary_rewrite

Clinical discharge summary → patient-friendly rewrite at ~6th-grade level:
what happened, medications, follow-ups, when-to-call. Citations preserved.

```bash
uv run python recipes/discharge_summary_rewrite/recipe.py --summary-file discharge.txt
```
