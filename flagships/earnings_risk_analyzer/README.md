# Finance: 10-K Risk-Flag Analyst Memo

Every buy-side analyst reads 200+ 10-K filings per quarter. This flagship
produces a **Hebbia-quality risk-flag memo** — automatically, grounded in the
actual SEC filing, with every claim citing a real chunk from the document.

**This demo uses REAL data** — Cloudflare's FY2025 10-K, downloaded live from
[SEC EDGAR](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001477333&type=10-K).
Not a fake corpus. Not lorem ipsum. The actual filing the company submitted to
the SEC.

## Seed data required

This demo reads from a folder in your Knowledge Stack tenant. You need to create that folder and upload the expected documents **before** running, otherwise retrieval returns nothing and the demo fails with empty output.

**Expected corpus:** A 10-K filing (e.g. downloaded from EDGAR), uploaded as PDF or HTML.

Set-up steps:

1. Sign up at [app.knowledgestack.ai](https://app.knowledgestack.ai).
2. Create a folder in the dashboard and copy its folder ID.
3. Upload the documents described above into that folder.
4. Issue an API key from the dashboard and put it in `.env` as `KS_API_KEY`.
5. Run: pass your folder ID via `CORPUS_FOLDER_ID` when running.

Full corpus matrix for every flagship: [`docs/wiki/seed-data.md`](../../docs/wiki/seed-data.md).

## Run

```bash
# 1. Seed the real 10-K (downloads from EDGAR, parses, chunks, inserts into KS)
cd ks-backend
python3 parse_cloudflare_10k.py   # → /tmp/cloudflare_10k_chunks.json
uv run --env-file .env.e2e python seed/seed_10k_corpus.py

# 2. From the cookbook:
cd knowledgestack-cookbook
make demo-earnings-risk
```

Output: `risk-flag-memo.md` — a structured memo with 5-15 risk flags, each
categorized (Market / Competition / Operational / Regulatory / Financial /
Technology / Cybersecurity / Legal), severity-rated (CRITICAL → LOW), and cited
to a verbatim excerpt from the filing.

## What the output looks like

```
# Risk-Flag Memo — Cloudflare, Inc. (NET)
**Filing:** FY2025 (Dec 31, 2025)
**Overall posture:** Elevated risk profile driven by customer concentration...

## 1. [HIGH] Revenue concentration in large enterprise customers
*Category: Market*

Cloudflare's growth is increasingly dependent on large enterprise...
[chunk:a8f3b2c1-...]

**Mitigation:** Company notes diversification across 185+ countries but...
```

## Why this is different from generic RAG

1. **Real data, not a toy corpus.** The 10-K is verbatim from EDGAR.
2. **Structured output, not chat prose.** The `EarningsRiskMemo` schema enforces: categorization, severity, citations per flag, and a synthesis section.
3. **Permission-enforced.** The 10-K is in a KS tenant. Different API keys see different filings. An analyst at Fund A can't accidentally query Fund B's proprietary annotations.
4. **Framework-swappable.** This uses pydantic-ai; the same MCP tools work with LangGraph, LlamaIndex, or raw OpenAI.

## Bring your own filing

```bash
# Download any company's 10-K from EDGAR
curl -sS "https://data.sec.gov/submissions/CIK{YOUR_CIK}.json" \
  -H "User-Agent: YourName/1.0 your@email.com" | python3 -c "..."
# Then adapt seed/seed_10k_corpus.py to point at your parsed file.
```

## Data source

[SEC EDGAR](https://www.sec.gov/) — all filings are public domain per SEC policy. No license restrictions on reproduction of SEC filings.
