# Meeting Notes Action Items

## Problem This Recipe Solves

Teams in **enterprise document workflows** repeatedly face high-friction document analysis tasks that are too nuanced for simple keyword search and too repetitive for manual-only review. This recipe demonstrates a practical automation pattern that keeps outputs grounded in source evidence instead of producing uncited summaries.

## Why This Is Needed

- Manual review is slow, expensive, and often inconsistent across reviewers.
- Point-in-time decisions need traceable evidence for audit, QA, or stakeholder sign-off.
- LLM automation without retrieval usually misses critical clauses/details or hallucinates context.
- Teams need repeatable workflows that can run daily/weekly with predictable structure.

## Typical Documents Used

- SOPs, policy docs, operational handbooks, and process guides
- Structured exports (CSV/XLSX), tickets, logs, and status updates
- Supporting evidence files used for auditability and citations

## How Frequently This Problem Appears

This is usually a **high-frequency operational problem**. In most organizations, similar requests appear:

- Daily in frontline workflows (ops, support, legal, compliance, finance, clinical, or engineering queues)
- Weekly in review cycles (approvals, controls, leadership reporting, and escalations)
- Monthly/quarterly during audits, board prep, renewals, and policy refreshes

## Common Automation Failure Modes

- Missing document context (wrong file version, partial retrieval, stale corpus)
- Non-cited outputs that cannot be defended in audit or compliance review
- Over-generalized prompts that ignore domain constraints and required fields
- Inconsistent schema/output shape that breaks downstream systems
- Hidden environment misconfiguration (`KS_API_KEY`, `OPENAI_API_KEY`, base URL, model)

## Developer Setup

### 1) Get your Knowledge Stack API key

1. Sign in to [app.knowledgestack.ai](https://app.knowledgestack.ai).
2. Open your account/workspace API key section.
3. Create or copy a key for your tenant.
4. Export it in your terminal:

```bash
export KS_API_KEY="your_ks_api_key"
export KS_BASE_URL="https://api.knowledgestack.ai"
```

### 2) Get your OpenAI API key

1. Sign in to [platform.openai.com](https://platform.openai.com/).
2. Go to **API keys** and create a new secret key.
3. Copy it once (OpenAI only shows full key at creation time).
4. Export it in your terminal:

```bash
export OPENAI_API_KEY="your_openai_api_key"
export MODEL="gpt-4o"
```

### 3) Run this recipe

```bash
uv run python recipes/meeting_notes_action_items/recipe.py --help
```


## Notes for Production Use

- Keep retrieval grounded: require citations/chunk references in outputs.
- Add strict output schemas before wiring to downstream automations.
- Start in read-only mode, then progressively allow write/actions with approvals.
- Monitor token cost, latency, and exception rates per run.

<!-- ks-cookbook auto-generated section: live verification -->
## Live verified — meeting_notes_action_items

Verified end-to-end on the unified cookbook corpus on **2026-04-28** (model `gpt-4o-mini`, ~29.4s).

### Run

```bash

```

### Output (head)

```json
{
  "meeting_id": "demo",
  "attendees": [
    "<unassigned>"
  ],
  "tl_dr": "No transcript found for the specified meeting ID.",
  "decisions": [],
  "action_items": [
    {
      "task": "Follow up on meeting transcript",
      "owner":
```

All `chunk_id` values in citations are verbatim UUIDs from `[chunk:<uuid>]` markers; document filenames and snippets are real chunk content from the ingested corpus.
<!-- end ks-cookbook auto-generated section -->
