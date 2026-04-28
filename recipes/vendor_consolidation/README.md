# `Vendor Consolidation`

**Generate a cited vendor-by-vendor consolidation strategy from enterprise contracts, renewal notes, and usage reports stored in Knowledge Stack.**

```bash
uv run python recipes/vendor_consolidation/recipe.py --category observability
```

---

## What this recipe does

`vendor_consolidation` analyzes procurement documents inside Knowledge Stack and produces a **structured consolidation plan** for a specific software category such as:

* observability
* CRM
* contact-center platforms
* identity providers
* analytics tooling
* security vendors

The output is a **vendor-level action plan** recommending whether each vendor should be:

* `keep`
* `migrate`
* `terminate`
* `renegotiate`

Each recommendation includes:

* grounded citations to source documents
* rationale tied to contract or usage evidence
* estimated savings
* risk signals
* overlap detection across tools

The result is a **defensible procurement strategy artifact**, not a generic AI summary.

---

## The problem this solves

Most enterprises accumulate overlapping vendors over time because:

| Cause                         | Example                                                             |
| ----------------------------- | ------------------------------------------------------------------- |
| Teams purchase independently  | Engineering adopts Datadog while platform team already uses Grafana |
| Contracts renew automatically | Legacy SaaS renews yearly without review                            |
| Ownership changes             | Vendor survives org restructuring without re-evaluation             |
| Usage declines silently       | Licenses paid but unused                                            |
| Migration plans stall         | Replacement tool exists but switch never completed                  |

Procurement and CIO teams often ask:

> “Why are we paying for six tools that do the same thing?”

Answering this normally requires manual review across:

* contracts
* renewal notices
* license counts
* architecture decisions
* evaluation memos
* usage exports

This recipe automates that analysis using **grounded document evidence**.

---

## What makes this different from a normal LLM summary

The agent:

✔ reads actual contract chunks
✔ prefers latest document versions
✔ extracts pricing only when explicitly present
✔ detects overlapping functionality
✔ evaluates switching risk
✔ estimates savings using documented signals
✔ cites the exact chunk used for each decision

It does **not fabricate procurement data**.

---

## Example output structure

The recipe returns structured JSON like:

```json
{
  "category": "observability",
  "vendors": [
    {
      "vendor": "Datadog",
      "action": "renegotiate",
      "rationale": "renewal upcoming within 90 days; duplicate log ingestion already available in OpenSearch",
      "annual_spend": "$420,000",
      "estimated_savings": "$90,000",
      "citation": {
        "chunk_id": "...",
        "document_name": "Datadog Renewal Memo",
        "snippet": "Contract renewal scheduled for Q3..."
      }
    }
  ],
  "overall_savings_estimate": "$180,000",
  "risks": [
    "migration dependency on logging pipeline stabilization"
  ]
}
```

This makes the result directly usable in:

* procurement review decks
* CIO vendor rationalization initiatives
* transformation programs
* cost-reduction planning cycles

---

## Typical users

This recipe is designed for:

### Procurement operations teams

Identify redundant SaaS vendors and reduce spend.

### Finance transformation teams

Support annual cost-optimization initiatives.

### CIO / CTO offices

Drive platform standardization.

### Platform engineering leadership

Align tooling decisions across teams.

---

## How Knowledge Stack enables this workflow

The recipe works because Knowledge Stack provides:

* version-aware contract storage
* chunk-level citations
* structured document traversal
* renewal-note retrieval
* usage-report grounding
* safe agent execution boundaries

Instead of asking:

> “What tools do we use?”

the agent answers:

> “Which vendors should we consolidate, why, and how much will we save — with evidence.”

---

## When to run this recipe

Run it whenever you want to evaluate consolidation within a category:

```bash
uv run python recipes/vendor_consolidation/recipe.py \
  --category observability
```

Typical cadence:

* before renewal season
* during platform standardization
* ahead of budgeting cycles
* during post-merger integration
* during enterprise cost-reduction initiatives

---

## Why this matters strategically

Vendor sprawl is one of the largest silent cost centers inside modern enterprises.

Most organizations:

* don’t track overlap well
* don’t link contracts to usage
* don’t connect renewal timing to architecture decisions
* don’t maintain defensible consolidation plans

This recipe turns Knowledge Stack into a **procurement intelligence layer**, not just a document store.

---

## Developer setup

### 1) Get your Knowledge Stack API key

1. Sign in to [app.knowledgestack.ai](https://app.knowledgestack.ai).
2. Open your workspace/account API keys page.
3. Create or copy an API key for your tenant.
4. Export it in your shell:

```bash
export KS_API_KEY="your_ks_api_key"
export KS_BASE_URL="https://api.knowledgestack.ai"
```

### 2) Get your OpenAI API key

1. Sign in to [platform.openai.com](https://platform.openai.com/).
2. Go to **API keys** and create a new secret key.
3. Copy the key once (full key is shown only at creation).
4. Export it in your shell:

```bash
export OPENAI_API_KEY="your_openai_api_key"
export MODEL="gpt-4o"
```

### 3) Run this recipe

```bash
uv run python recipes/vendor_consolidation/recipe.py --help
```

## Common automation pitfalls

- Missing or stale source documents in the target corpus
- No citation enforcement in output schema
- Prompt too generic for domain-specific constraints
- Inconsistent output shape for downstream systems
- Environment drift across local/CI (`KS_API_KEY`, `OPENAI_API_KEY`, `MODEL`)