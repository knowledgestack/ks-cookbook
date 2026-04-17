# Changelog

All notable changes to `ks-cookbook` are documented here.

Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning: SemVer once we tag `v0.2.0` and beyond.

## [Unreleased]

### Added
- `.pre-commit-config.yaml` with `make fix` + `make lint` hooks.
- `.cursor/rules/` — `python_clean_code.mdc`, `flagship_author.mdc`, `recipe_author.mdc` (mirrors ks-backend's clean-code convention, adapted for the cookbook).
- `make fix`, `make format`, `make install-dev` Makefile targets.
- `pre-commit` pinned in `[dependency-groups].dev`.

## [0.1.1] - 2026-04-17

### Added
- Developer wiki under `docs/wiki/` — connecting, MCP tool reference, seed data, configuration, writing a flagship, writing a recipe, troubleshooting.
- Standardized **Seed data required** block in every flagship README, pointing external developers at the app.knowledgestack.ai signup + upload flow.
- Concrete `sample_inputs/` fixture in every flagship that was missing one.
- `CLAUDE.md` for future agent sessions.
- Discoverability tags on every flagship plus a root-README "Browse by tag" index.
- Framework links and badges: LangChain, LangGraph, CrewAI, Temporal, OpenAI Agents SDK, pydantic-ai, Claude Desktop, Cursor.
- "Contributing" and "Building with Knowledge Stack? Reach out" sections.
- GitHub repo topics (20 total) and homepage for SEO.
- Branch protection on `main`: PR required, 2 status checks, no force-push, no deletion, enforce on admins.

### Changed
- Root README rewritten as a developer-platform entrypoint ("Focus on agents. We handle document intelligence.").
- "Flagships by vertical" section switched from `make` commands to links pointing at each flagship's README.
- All sample output artifacts moved from the repo root into `flagships/<slug>/sample_output.<ext>`; Makefile, `.gitignore`, and README updated accordingly.
- `ksapi` resolves from PyPI instead of the local `../ks-backend/codegen/ks-backend-python` path — no sibling checkout needed for `uv sync`.
- `ruff` line-length raised to 100; `E501`/`UP042` ignored pending a broader cleanup.
- CI workflow fixed: installs `ruff` via dev group; MCP tests run with `--extra dev`.

## [0.1.0] - 2026-04-16

### Added
- Initial cookbook — 32 flagships across banking, legal, accounting, tax, healthcare, insurance, real estate, sales, HR, engineering, government, pharma, and energy.
- `knowledgestack-mcp` read-side tool surface (`list_contents`, `find`, `get_info`, `read`, `read_around`, `view_chunk_image`, `search_knowledge`, `search_keyword`, `get_organization_info`, `get_current_datetime`).
- Makefile with per-flagship `demo-*` targets.
- Recipes directory with templates and shared MCP session helper.
