# Recipes index

Each recipe is a self-contained script under `recipes/<name>/recipe.py` solving one real B2B pain point. All use the same KS MCP stdio plumbing (`knowledgestack-mcp` only); what differs is the **agent framework** and the **use case**.

| Recipe | Pain point | Framework | Tools used |
|---|---|---|---|
| [compliance_questionnaire](../flagships/compliance_questionnaire/) | CAIQ/SIG questionnaires take days. Fill them from your policies. | LangGraph | list_contents, read |
| [onboarding_checklist](onboarding_checklist/) | HR copy-pastes policy bits for every new role. | OpenAI function-calling | list_contents, read |
| [incident_postmortem](incident_postmortem/) | SREs re-derive post-mortem shape + policy refs. | pydantic-ai | list_contents, read |
| [vendor_security_review](vendor_security_review/) | 3rd-party risk review starts from scratch each time. | Anthropic tool use | list_contents, read |
| [policy_qa](policy_qa/) | "#ask-it" channel gets the same 20 questions forever. | Raw OpenAI (shortest path) | list_contents, read |
| [sdlc_checklist](sdlc_checklist/) | Engineers forget per-PR required steps (threat model, licence scan). | LangGraph | list_contents, read |
| [permission_aware_retrieval](permission_aware_retrieval/) | **The auth-boundary demo.** Same code, different per-user keys, different docs returned — enforced by KS. | pydantic-ai | list_contents, read |
| [llama_index_rag](llama_index_rag/) | Proves "any framework": LlamaIndex VectorStoreIndex over KS-filtered docs. | LlamaIndex | list_contents, read |

## Add your own

```bash
cp -r recipes/_template recipes/my_recipe
# Edit recipes/my_recipe/recipe.py + README.md
# Add a row to this table.
uv run python recipes/my_recipe/recipe.py --help
```

Rules in [`_template/README.md`](_template/README.md).

## Roadmap

The v1 cookbook ships the 8 recipes above plus multiple flagship agents under `flagships/`. The scaffold supports unlimited additions — aiming for 100+ via community PRs built on the same KS tool surface. Suggested next batches:

- **Sales/RevOps** (8): sales battlecard, ICP matcher, account research brief, prospecting email personalizer, deal loss retro, churn risk flags, QBR deck drafter, renewal risk evidence pack.
- **Legal/Contracts** (6): MSA redline vs playbook, NDA review, clause extractor, obligation tracker, DPA gap check, force-majeure impact.
- **People** (5): JD generator from role, interview bank, perf review draft, offer letter, policy-Q&A bot (already shipped).
- **Engineering** (8): ADR drafter, API docs from spec, changelog from commits, migration guide, tech debt ledger, runbook lookup, incident drill, release notes.
- **Finance/Ops** (5): invoice reconciliation, expense policy violation, vendor consolidation, runway scenarios, board deck.
- **Marketing** (4): content brief, SEO draft, case study, email variants.

Pick one, `cp -r recipes/_template recipes/<yours>`, send a PR.
