# security_finding_triage

Scanner finding → cited triage: classification (TP/likely/FP/more-info),
severity, exception applicability, remediation, SLA days.

```bash
uv run python recipes/security_finding_triage/recipe.py \
  --id CVE-2025-1234 --description "requests<2.32 in build image"
```
