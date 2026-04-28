# PR — openai/openai-agents-python (examples)

**Section to add to:** `Third-party MCP integrations`

**One-line addition (copy-paste):**

- [Knowledge Stack](https://github.com/knowledgestack/ks-cookbook) — MCP server + 40 cited-output flagships compatible with the Agents SDK.

---

## PR description (paste into PR body)

Adding Knowledge Stack to the Third-party MCP integrations section.

**What it is:** Document intelligence layer for agents. MCP-native, citation-first, multi-tenant. The cookbook ships 40+ production-style flagship agents that use the OpenAI Agents SDK.

**Why it fits this list:** Real production patterns with verifiable citations — not toy demos. Every flagship calls MCP tools and emits `[chunk:<uuid>]` markers, CI-enforced.

**Repos:**
- Cookbook (open-source, MIT): https://github.com/knowledgestack/ks-cookbook
- MCP server: https://github.com/knowledgestack/ks-mcp
- Python SDK (PyPI `ksapi`): https://github.com/knowledgestack/ks-sdk-python
- TypeScript SDK (`@knowledge-stack/ksapi`): https://github.com/knowledgestack/ks-sdk-ts
- Docs: https://docs.knowledgestack.ai

Happy to adjust placement, wording, or section per your preferences.
