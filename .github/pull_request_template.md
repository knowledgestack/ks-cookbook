<!--
Thanks for contributing! A clear PR description helps reviewers move fast.
Delete sections that don't apply — don't leave them empty.
-->

## Summary

<!-- 1–3 sentences. What changed and why? -->

## Type of change

<!-- Check all that apply. -->

- [ ] 🚀 New flagship (`flagships/<name>/`)
- [ ] 🧑‍🍳 New recipe (`recipes/<name>/`)
- [ ] 🔌 New framework integration (LangChain, LangGraph, CrewAI, Temporal, …)
- [ ] 🐛 Bug fix
- [ ] 📖 Documentation / wiki
- [ ] 🧰 Tooling / CI / dev setup
- [ ] 🧹 Refactor (no behavior change)
- [ ] 💥 Breaking change (describe migration in "Notes")

## Related issues

<!-- "Closes #123" / "Fixes #456" / "Related to #789" -->

## What changed

<!-- Bullet the concrete changes — files, behaviors, flags. -->

-
-

## How to review

<!-- Suggest a reading order or a specific thing to try. -->

```bash
# e.g.
CORPUS_FOLDER_ID=<your-folder> make demo-<slug>
```

## Test plan

- [ ] `make lint` passes
- [ ] `make test` passes (MCP unit tests)
- [ ] `make demo-<slug>` runs end-to-end (if flagship/recipe work)
- [ ] Screenshots / sample output attached (if UI-ish or format change)

## Checklist

<!-- Required before merge. -->

- [ ] I've read [CONTRIBUTING.md](../blob/main/CONTRIBUTING.md) and the relevant [cursor rule](../tree/main/.cursor/rules/)
- [ ] No API keys, tokens, or PII in the diff
- [ ] Every non-trivial claim in the agent output is cited (`Citation.chunk_id` or `[chunk:<uuid>]`)
- [ ] Seed-data expectations documented (either in the flagship README or updating the [Seed data wiki page](https://github.com/knowledgestack/ks-cookbook/wiki/seed-data))
- [ ] Workspace `pyproject.toml` updated if a new package was added
- [ ] Makefile target added/updated if a new flagship was added
- [ ] CHANGELOG.md updated under `[Unreleased]`

## Notes

<!-- Anything reviewers should know: tradeoffs, follow-ups, open questions. -->
