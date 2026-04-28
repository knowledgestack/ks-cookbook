---
title: "Employee Handbook Qa agent — grounded in your docs, with citations"
description: "Employee question → cited answer from the company handbook."
keywords: ["employee handbook qa", "General agent", "General RAG", "document AI", "MCP"]
---

# Employee Handbook Qa

Employee question → cited answer from the company handbook.

Built on **Knowledge Stack** — the document intelligence layer for agents. Every output cites the exact `[chunk:<uuid>]` it came from, so reviewers can trace any sentence back to source.

## What it does

- Connects to your `knowledgestack-mcp` server over stdio.
- Enumerates the `General` corpus folder, reads relevant chunks, and produces a structured pydantic output.
- Writes a Word/Markdown/Excel artifact your team can ship to a customer, regulator, or internal reviewer.
- Refuses to fabricate citations: every `chunk_id` is copied verbatim from `read` tool output (CI-enforced).

## Try it in 60 seconds

```bash
git clone https://github.com/knowledgestack/ks-cookbook
cd ks-cookbook
echo "KS_API_KEY=ks_..." > .env
echo "OPENAI_API_KEY=sk-..." >> .env
make setup
make demo-employee-handbook-qa
```

Output: a cited `.md` / `.docx` / `.xlsx` you can hand to a reviewer.

## SDKs

- **Python:** `pip install ksapi`
- **TypeScript:** `npm i @knowledge-stack/ksapi`
- **MCP:** `uvx knowledgestack-mcp` (works in Claude Desktop, Cursor, any MCP host)

## Why citations matter for General

In General, an unsourced AI answer is a liability. Knowledge Stack threads `[chunk:<uuid>]` markers through every read, and the schema rejects outputs that lack them. That's the difference between a demo and a control your auditors accept.

## Source

- Flagship: [`flagships/employee_handbook_qa/`](https://github.com/knowledgestack/ks-cookbook/tree/main/flagships/employee_handbook_qa)
- Get a free API key: [knowledgestack.ai](https://knowledgestack.ai)
- Docs: [docs.knowledgestack.ai](https://docs.knowledgestack.ai)
- Discord: [join](https://discord.gg/McHmxUeS)
