# construction_rfi_agent

RFI number + question → cited draft response with CSI spec section,
schedule/cost impact, and architect-routing flag.

```bash
uv run python recipes/construction_rfi_agent/recipe.py \
  --rfi-number "RFI-0412" --text "VAV box tag VAV-3-12 shown on M3.2 conflicts with schedule M6.1."
```
