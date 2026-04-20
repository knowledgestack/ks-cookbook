# password_policy_audit

Pulls password / MFA / session / lockout excerpts from your auth policies and writes a side-by-side audit report next to an observed config snapshot.

```bash
uv run python recipes/password_policy_audit/recipe.py
uv run python recipes/password_policy_audit/recipe.py --config-file ./prod-auth.json
```

Framework: MCP-only (deterministic, no LLM).
