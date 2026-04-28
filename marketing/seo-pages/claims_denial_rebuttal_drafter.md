---
title: "Claims Denial Rebuttal Drafter agent — grounded in your docs, with citations"
description: "Healthcare flagship — draft a payer-ready claim denial rebuttal letter grounded in the patient chart + payer medical policy corpus."
keywords: ["claims denial rebuttal drafter", "Healthcare agent", "Healthcare RAG", "document AI", "MCP"]
---

# Claims Denial Rebuttal Drafter

Healthcare flagship — draft a payer-ready claim denial rebuttal letter grounded in the patient chart + payer medical policy corpus.

Built on **Knowledge Stack** — the document intelligence layer for agents. Every output cites the exact `[chunk:<uuid>]` it came from, so reviewers can trace any sentence back to source.

## What it does

- Connects to your `knowledgestack-mcp` server over stdio.
- Enumerates the `Healthcare` corpus folder, reads relevant chunks, and produces a structured pydantic output.
- Writes a Word/Markdown/Excel artifact your team can ship to a customer, regulator, or internal reviewer.
- Refuses to fabricate citations: every `chunk_id` is copied verbatim from `read` tool output (CI-enforced).

## Try it in 60 seconds

```bash
git clone https://github.com/knowledgestack/ks-cookbook
cd ks-cookbook
echo "KS_API_KEY=ks_..." > .env
echo "OPENAI_API_KEY=sk-..." >> .env
make setup
make demo-claims-denial-rebuttal-drafter
```

Output: a cited `.md` / `.docx` / `.xlsx` you can hand to a reviewer.

## SDKs

- **Python:** `pip install ksapi`
- **TypeScript:** `npm i @knowledge-stack/ksapi`
- **MCP:** `uvx knowledgestack-mcp` (works in Claude Desktop, Cursor, any MCP host)

## Why citations matter for Healthcare

In Healthcare, an unsourced AI answer is a liability. Knowledge Stack threads `[chunk:<uuid>]` markers through every read, and the schema rejects outputs that lack them. That's the difference between a demo and a control your auditors accept.

## Source

- Flagship: [`flagships/claims_denial_rebuttal_drafter/`](https://github.com/knowledgestack/ks-cookbook/tree/main/flagships/claims_denial_rebuttal_drafter)
- Get a free API key: [knowledgestack.ai](https://knowledgestack.ai)
- Docs: [docs.knowledgestack.ai](https://docs.knowledgestack.ai)
- Discord: [join](https://discord.gg/McHmxUeS)
