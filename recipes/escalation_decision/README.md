# escalation_decision

Ticket summary + severity + SLA remaining → cited escalate/hold decision per
escalation matrix.

```bash
uv run python recipes/escalation_decision/recipe.py \
  --summary "Customer reports PII leak in export" --severity high --sla-min 30
```
