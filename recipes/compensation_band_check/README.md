# compensation_band_check

Role + level + location + proposed salary → cited verdict (in_band / above /
below / exception_needed) + band min / mid / max.

```bash
uv run python recipes/compensation_band_check/recipe.py \
  --role "Staff SWE" --level Staff --location "NYC" --proposed "$240,000"
```
