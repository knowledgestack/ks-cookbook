# Security Policy

We take security seriously. This document covers how to report a vulnerability in `ks-cookbook`, the `knowledgestack-mcp` server, or any code distributed from this repository.

## Supported versions

Only the `main` branch receives security updates. Pinned or tagged releases are best-effort — please upgrade to the latest before filing a report.

| Version | Supported |
|---------|-----------|
| `main`  | ✅ |
| tagged releases | ⚠️ best effort — upgrade first |
| forks / patches | ❌ |

## Reporting a vulnerability

**Do not open a public GitHub issue for security vulnerabilities.**

Please report privately via one of:

1. **GitHub Private Vulnerability Reporting** (preferred) — on this repo, click **Security → Report a vulnerability**. This creates a private advisory only visible to maintainers. Link: [report here](https://github.com/knowledgestack/ks-cookbook/security/advisories/new).
2. **Email** — `security@knowledgestack.ai` (if you don't use GitHub). Please include "ks-cookbook" in the subject.

Include, where possible:

- Affected component (flagship name, `knowledgestack-mcp`, a recipe, etc.)
- Reproduction steps (minimum viable command or diff)
- Impact (data exposure, code execution, privilege escalation, denial of service)
- Affected commit / version
- Any proof-of-concept you're willing to share

## What counts as a security issue

Examples of things we do want to hear about:

- Secret/credential exposure in example code or logs
- Prompt-injection or tool-invocation vulnerabilities in the MCP server itself (not in downstream agent code — that's the user's responsibility)
- Dependency vulnerabilities with a clear exploit path in our code
- Supply-chain concerns in our published artifacts (`knowledgestack-mcp` on PyPI, generated SDKs)
- CI/CD or GitHub Actions misconfigurations that could allow unauthorized writes

Things that are **not** security issues here:

- Bugs in your own agent logic that leak data (that's an agent-level concern; file a normal issue if you need help)
- Vulnerabilities in the hosted Knowledge Stack API — file those privately at [security@knowledgestack.ai](mailto:security@knowledgestack.ai); they don't belong in this repo
- Prompt-injection in flagships you've forked and modified (we can't triage unbounded variants)

## Response expectations

- **Acknowledgement:** within **2 business days** of your report
- **Triage & severity assessment:** within **5 business days**
- **Fix timeline:** depends on severity — critical issues target **7 days**; lower-severity issues within the next release cycle
- We will coordinate on disclosure timing — default is 90 days from report, with mutual agreement on earlier or later publication if warranted

## Safe harbor

Security research conducted in good faith against this repository and the referenced MCP server is welcomed. We won't pursue legal action against researchers who:

- Avoid privacy violations, destruction of data, and disruption of service
- Only interact with accounts they own or have explicit permission to test
- Give us a reasonable window to fix before publicly disclosing
- Do not monetize the vulnerability before disclosure

Thanks for helping keep the Knowledge Stack ecosystem safe.
