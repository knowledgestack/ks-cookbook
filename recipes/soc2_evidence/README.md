# soc2_evidence

Given a SOC 2 control ID (CC6.1, CC7.2, …), pulls cited policy excerpts into a single markdown evidence pack. Pure MCP — no LLM call, no fabrication.

```bash
uv run python recipes/soc2_evidence/recipe.py --control CC6.1
uv run python recipes/soc2_evidence/recipe.py --control CC8.1 --out change-mgmt.md
```

Framework: MCP-only (deterministic keyword search + read).
