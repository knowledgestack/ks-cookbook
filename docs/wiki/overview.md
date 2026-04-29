# Overview — what this repo is and why

Knowledge Stack is the document intelligence layer behind your agents — ingestion, chunking, permissions, versioning, and citation tracking — exposed through a stable **MCP** surface. This cookbook shows how to plug that layer into agent workflows you already run.

## Why this repo exists

Orchestration tooling (LangChain, LangGraph, CrewAI, Temporal) is mature. **Enterprise document infrastructure is still rebuilt from scratch by every team.** Most demos stop at "here is a chat response." Enterprise teams need:

- outputs reviewable by legal, finance, compliance, operations, or engineering
- citations that point back to source material (chunk-level, verifiable)
- permission-aware retrieval — the same agent behaves differently for different users
- version-aware reads so audits reference the document as of a specific date
- patterns that copy cleanly into real internal tooling

## What Knowledge Stack manages for your agent

Instead of building this yourself:

- document ingestion pipelines (PDF, DOCX, HTML, Markdown, …)
- chunk storage and structured navigation
- permission filtering and ACLs
- version-aware retrieval
- citation grounding (chunk-level UUIDs)
- folder-level access control per user
- structured document read surface (folders → documents → sections → chunks)

KS exposes these as APIs and **MCP tools**. Your team focuses on agent workflows, orchestration logic, output schemas, automation pipelines, and business logic.

## Pipeline mental model

```
┌──────────────────────────────────────────────────────────────┐
│  Agent logic      (LangChain / LangGraph / CrewAI / Temporal │
│                    / OpenAI Agents SDK / pydantic-ai)        │
└────────────────────────────┬─────────────────────────────────┘
                             ↓
┌──────────────────────────────────────────────────────────────┐
│  Knowledge Stack MCP tools  (read, search, list_contents, …) │
└────────────────────────────┬─────────────────────────────────┘
                             ↓
┌──────────────────────────────────────────────────────────────┐
│  Permission-aware retrieval   +   version-aware reads        │
└────────────────────────────┬─────────────────────────────────┘
                             ↓
┌──────────────────────────────────────────────────────────────┐
│  Chunk citations  →  schema-enforced output  →  .md/.docx    │
└──────────────────────────────────────────────────────────────┘
```

Knowledge Stack sits between your agent runtime and your document corpus. Your orchestration layer doesn't change.

## Build enterprise RAG faster

| You would normally build | With Knowledge Stack you skip to |
|---|---|
| ingestion pipelines + chunking + metadata | ✅ done — upload and go |
| ACL filtering per user / group / folder | ✅ enforced on every read |
| version pinning + historical retrieval | ✅ version-aware by default |
| citation-grounded output tracking | ✅ every chunk has a UUID |
| schema-enforced agent outputs | ✅ patterns shown in this cookbook |

## How a flagship is structured

Each flagship follows the same flow:

1. Accept a business input (borrower, contract, alert, claim, patient scenario, …).
2. Connect to `knowledgestack-mcp` over stdio.
3. Search, list, and read folder contents.
4. Produce a schema-constrained answer grounded in the source material.
5. Write the artifact to disk (`.md` / `.docx` / `.xlsx` / `.csv`).

Once you understand one flagship, the rest are easy to adapt. See [Writing a flagship](writing-a-flagship.md) for the file layout and prompt rules.

## Output examples

These aren't toy console logs. Each flagship writes its output beside its package:

- `flagships/credit_memo_drafter/sample_output.md` — cited borrower risk memo
- `flagships/contract_obligation_extractor/sample_output.md` — obligations extracted from an MSA
- `flagships/rev_rec_memo/sample_output.md` — ASC 606 position memo
- `flagships/prior_auth_letter/sample_output.docx` — clinical prior-auth submission
- `flagships/compliance_questionnaire/sample_output.xlsx` — auto-completed CAIQ questionnaire
- `flagships/research_brief/sample_output.docx` — research brief built from KB evidence
- `flagships/csv_enrichment/sample_output.csv` — CSV enriched from KB content

## Repo map

```text
flagships/<name>/
  README.md              # flagship-specific walkthrough
  pyproject.toml         # package metadata + entrypoint
  src/<module>/
    __main__.py          # CLI entry
    agent.py             # prompt + MCP interaction
    schema.py            # structured output contract
  sample_inputs/         # default demo inputs

recipes/
  INDEX.md               # lightweight patterns and starter recipes
  _shared/mcp_client.py  # ks_mcp_session() helper
```

The MCP server and SDKs live in their own repos:

- **[knowledgestack/ks-mcp](https://github.com/knowledgestack/ks-mcp)** — MCP server (`uvx knowledgestack-mcp`)
- **[knowledgestack/ks-sdk-python](https://github.com/knowledgestack/ks-sdk-python)** — Python SDK (`ksapi` on PyPI)
- **[knowledgestack/ks-sdk-ts](https://github.com/knowledgestack/ks-sdk-ts)** — TypeScript SDK (`@knowledge-stack/ksapi` on npm)
- **[knowledgestack/ks-docs](https://github.com/knowledgestack/ks-docs)** — central docs site (docs.knowledgestack.ai)
