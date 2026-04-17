# Serena Context: knowledgestack-cookbook

This `.serena` workspace is the agent-facing control plane for the cookbook.

## Mission

Help agents learn **Knowledge Stack (KS) as a service** quickly:

- one MCP server (`knowledgestack-mcp`)
- one API key (`KS_API_KEY`)
- one stable read-side tool surface (10 tools)
- many agent frameworks

The goal is to scale this repo to **100+ practical agents** while keeping the
retrieval/grounding surface constant and enterprise-safe.

## Required posture

- Use **KS tooling only** for MCP access.
- Treat this repo as a **KS onboarding + implementation cookbook**, not a
  generic MCP playground.
- Keep outputs grounded in KS chunk citations.

## Key references

- Tool inventory: `tasks/ks_mcp_tooling_inventory.md`
- KS-only contract: `tasks/ks_only_contract.md`
- Behavior skill: `skills/karpathy-guidelines/SKILL.md`
