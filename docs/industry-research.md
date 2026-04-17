# Industry Research Appendix

> Research scan of ~30 popular open-source agent, RAG, and AI-tooling repos. Maps what developers actually build today, where the vertical gaps are, and which flagship demos close enterprise sales.
>
> Scope as of 2026-04. Star counts approximate (±10%).

## A. Top 20 repos inspected

| # | Repo | ~Stars | Category | What it does (1 line) |
|---|---|---|---|---|
| 1 | [langchain-ai/langchain](https://github.com/langchain-ai/langchain) | 125k | Agent framework | Modular LLM/agent/RAG toolkit; the "default" starting point. |
| 2 | [langgenius/dify](https://github.com/langgenius/dify) | 114k | Low-code agent/RAG | Visual workflow builder for RAG + agents + chatbots. |
| 3 | [Shubhamsaboo/awesome-llm-apps](https://github.com/Shubhamsaboo/awesome-llm-apps) | 105k | Cookbook (curated) | 100+ single-file agent/RAG apps across verticals. |
| 4 | [infiniflow/ragflow](https://github.com/infiniflow/ragflow) | 70k | RAG template | Deep-document parsing (tables, scans, XBRL) for enterprise RAG. |
| 5 | [FoundationAgents/MetaGPT](https://github.com/FoundationAgents/MetaGPT) | 62k | Multi-agent framework | Simulated software company (PM/arch/eng) as agents. |
| 6 | [microsoft/autogen](https://github.com/microsoft/autogen) | 53k | Agent framework | Multi-agent conversational orchestration. |
| 7 | [pathwaycom/pathway](https://github.com/pathwaycom/pathway) | 50k+ | RAG template | Real-time/streaming RAG pipeline. |
| 8 | [run-llama/llama_index](https://github.com/run-llama/llama_index) | 46k | RAG framework | 150+ data connectors, doc agents, workflows. |
| 9 | [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI) | 42k | Multi-agent framework | Role-based "crew" orchestration. |
| 10 | [FlowiseAI/Flowise](https://github.com/FlowiseAI/Flowise) | 51k | Low-code RAG | LangChain on a drag-and-drop canvas. |
| 11 | [agno-agi/agno](https://github.com/agno-agi/agno) | 36k | Agent framework | Runtime + control plane for scaling agents. |
| 12 | [HKUDS/LightRAG](https://github.com/HKUDS/LightRAG) | 27k | GraphRAG | Knowledge-graph retrieval. |
| 13 | [NirDiamant/RAG_Techniques](https://github.com/NirDiamant/RAG_Techniques) | 27k | Cookbook | 30+ notebook recipes for RAG patterns. |
| 14 | [deepset-ai/haystack](https://github.com/deepset-ai/haystack) | 24k | RAG framework | Production RAG pipelines; finance/gov focus. |
| 15 | [assafelovic/gpt-researcher](https://github.com/assafelovic/gpt-researcher) | ~16k | Vertical agent | Autonomous web-research report generator. |
| 16 | [pydantic/pydantic-ai](https://github.com/pydantic/pydantic-ai) | ~12k | Agent framework | Type-safe FastAPI-style agents. |
| 17 | [stanfordnlp/dspy](https://github.com/stanfordnlp/dspy) | ~22k | Agent framework | "Programming not prompting"; optimizer-driven pipelines. |
| 18 | [openai/openai-cookbook](https://github.com/openai/openai-cookbook) | ~65k | Cookbook | Canonical examples; agents, RAG, evals, fine-tuning. |
| 19 | [anthropics/anthropic-cookbook](https://github.com/anthropics/anthropic-cookbook) | ~15k | Cookbook | Tool use, MCP, extended thinking, agents. |
| 20 | [dgunning/edgartools](https://github.com/dgunning/edgartools) | ~2k | Vertical template | SEC EDGAR + XBRL MCP server; finance agents. |

Also surveyed: [run-llama/llamacloud-demo](https://github.com/run-llama/llamacloud-demo) (auto-insurance claims), [rh-aiservices-bu/insurance-claim-processing](https://github.com/rh-aiservices-bu/insurance-claim-processing), [kaymen99/sales-outreach-automation-langgraph](https://github.com/kaymen99/sales-outreach-automation-langgraph), [filip-michalsky/SalesGPT](https://github.com/filip-michalsky/SalesGPT), [epfLLM/meditron](https://github.com/epfLLM/meditron), [vas3k/TaxHacker](https://github.com/vas3k/TaxHacker), [bigcapitalhq/bigcapital](https://github.com/bigcapitalhq/bigcapital), [getprobo/probo](https://github.com/getprobo/probo), [trycomp.ai](https://www.helpnetsecurity.com/2026/04/07/comp-ai-open-source-compliance-platform/), [FoloUp/FoloUp](https://github.com/FoloUp/FoloUp), [AleksNeStu/ai-real-estate-assistant](https://github.com/AleksNeStu/ai-real-estate-assistant), [langchain-ai/open_deep_research](https://github.com/langchain-ai/open_deep_research), [ashishpatel26/500-AI-Agents-Projects](https://github.com/ashishpatel26/500-AI-Agents-Projects).

## B. Recurring use-case categories

| Business function | Coverage (of 20) | Canonical examples |
|---|---|---|
| Document Q&A / RAG over PDFs | 18/20 | LlamaIndex "chat-with-10K" is reference. |
| Customer support / triage + handoff | 12/20 | OpenAI "Orchestrating Agents", LangGraph customer-support tutorial, Dify templates. |
| Deep web research + report | 10/20 | GPT-Researcher, open_deep_research, awesome-llm-apps. |
| Coding agent / code review | 9/20 | OpenAI cookbook, autogen, MetaGPT. |
| Data extraction / structured parsing | 8/20 | pydantic-ai, LlamaParse, TaxHacker. |
| Sales outreach / lead qualification | 6/20 | SalesGPT, sales-outreach-automation-langgraph. |
| Financial doc analysis (10-K/earnings) | 6/20 | edgartools, sec-edgar-agentkit, Haystack. |
| Meeting notes / summarization | 5/20 | awesome-llm-apps. |
| Multi-agent "company simulation" | 4/20 | MetaGPT, CrewAI, AutoGen. |
| Voice / real-time agents | 4/20 | FoloUp, OpenAI realtime. |
| Medical Q&A / clinical RAG | 3/20 | Meditron, Medical-RAG-LLM. |
| Legal contract review | 3/20 | claude-legal-skill, ai-legal-claude. |
| HR / recruiting / resume | 3/20 | AI-Recruitment-Agent, FoloUp. |
| Insurance claim processing | 2/20 | llamacloud-demo, rh-aiservices-bu. |
| SOC2/compliance evidence | 2/20 | Probo, Comp AI (products, not cookbook recipes). |
| Real estate / property search | 2/20 | ai-real-estate-assistant. |
| Accounting / AP automation | 2/20 | TaxHacker, OpenAccountants. |

**Takeaway:** the *horizontal* plumbing (RAG, support, research, coder) is saturated. *Verticals* are thin — that's where Knowledge Stack wins.

## C. Vertical gaps (clear enterprise TAM, weak OSS coverage)

| Gap | Market signal | OSS coverage today |
|---|---|---|
| **Insurance claim adjudication** | $400B+ P&C claims/yr; Sprout.ai / Five Sigma funded | 1 LlamaCloud notebook, 1 RH Lab — no flagship |
| **SOC2 / security questionnaire auto-fill** | Drata/Vanta at $2B+ | Products only, not OSS cookbook recipes |
| **Clinical prior authorization** | $25B manual cost; Cohere Health raised $200M | Zero |
| **Pharma MSL / medical affairs RAG** | Regulated; Veeva/Within3 territory | Zero |
| **Oil & gas / utility disputes** | Halliburton, utilities spend billions | Zero |
| **Government RFP response** | $30B govtech; GovGPT/Govly commercial | Zero OSS flagship |
| **Corporate tax research** | $14B market | TaxHacker = receipts only |
| **Title / real estate diligence** | $20B title insurance | Only property-search demos |
| **Construction RFI / submittal review** | $1.6T; Procore ecosystem | Zero |
| **Banking KYC / AML SAR narratives** | Multi-billion ops cost | Zero open |
| **Audit sampling / evidence review** | Big4 internal; zero OSS | Zero |

**Opportunity thesis:** *clone-the-enterprise-SaaS-in-a-cookbook-recipe* is the wedge.

## D. 10 flagship demo ideas (closing the enterprise sale)

| # | Demo | Vertical | B2B pain | Public corpus | Framework | Closing line |
|---|---|---|---|---|---|---|
| 1 | **Auto-adjudicate P&C claim** | Insurance | Adjusters spend 2–5 h/claim on policy + FNOL + photos | ACORD forms + Insurance-LLM-framework data + NAIC filings | LangGraph + vision | "60% of sub-$5k claims cleared without an adjuster." |
| 2 | **Security-questionnaire autofill** | SaaS/SOC2 | SIG/CAIQ deals stall for weeks | CAIQ v4 (CSA), SIG Lite, SANS templates | pydantic-ai + RAG | "Close deals 3× faster; every answer cites evidence." — **✅ shipped** |
| 3 | **10-K red-flag agent** | Finance / IR | Analysts skim 200 filings/quarter | SEC EDGAR XBRL, edgartools | CrewAI (analyst + writer + critic) | "Hebbia-quality memos without Hebbia pricing." |
| 4 | **Clinical prior-auth agent** | Healthcare payer | 14-day reviews; denials cost $11/letter | CMS LCDs, ICD-10, DailyMed | LangGraph + structured output | "PA turnaround days → minutes, fully audited." — **🟡 scaffolded** |
| 5 | **Contract redline + playbook** | Legal | Mid-market can't afford Harvey | CUAD dataset, EDGAR exhibits | DSPy (optimizer-tuned) | "Spellbook-class redlines on-prem — data never leaves." — **🟡 scaffolded** |
| 6 | **Government RFP responder** | GovTech | 120-page RFPs, past-performance reuse | SAM.gov, GSA eBuy, USASpending.gov | Mastra (TS) + RAG | "Win rate +15%, proposal cost −40%." |
| 7 | **Well-log / drilling report summarizer** | Energy | Engineers triage 100s of reports/day | US DOE OpenEnergy, SPE papers, TX RRC | LlamaIndex doc agents | "Surface HSE events before they escalate." |
| 8 | **SAR / AML narrative writer** | Banking | 200-word SARs written by hand | FinCEN SAR format, OFAC SDN, FFIEC BSA/AML | Agno + evals | "Analyst narrative time −70%, FinCEN-format output." |
| 9 | **Construction RFI / submittal agent** | Construction | RFIs pile up, specs cross-ref'd | CSI MasterFormat, ASHRAE, FHWA | AutoGen | "60% of RFIs answered from spec + drawings in minutes." |
| 10 | **Tax research memo agent** | Tax / Big4 | 10 h/memo for court + ruling lookup | IRS Code, Treas Regs, Tax Court opinions, OpenFisca | LangGraph + citation-checker | "Checkpoint at 1/20 the cost, with citations." |

## E. 50 quick-hit recipe ideas (≤100 LOC each)

### Legal
- NDA clause extractor
- MSA indemnity diff vs playbook
- Patent prior-art retrieval
- Privacy-policy GDPR gap audit
- Court-docket monitor (competitor sued in N.D. Cal.?)

### Accounting / FinOps
- Vendor-invoice line-item extractor
- Expense-report categorizer (IRS Schedule C)
- Cash-flow anomaly detector (bank CSV)
- Chart-of-accounts mapper (QB → NetSuite)
- Month-end close narrative (CFO memo from trial balance)

### Banking / Fintech
- KYC adverse-media screener
- AML transaction-pattern narrative
- Loan-application doc classifier (paystubs vs W2s)
- Basel III risk-weight calculator agent
- Credit-memo generator — **✅ shipped as `credit_memo_drafter`**

### Healthcare
- Clinical-note ICD-10 coder
- Patient intake symptom-triage bot
- Drug-drug interaction checker (DailyMed)
- Clinical-trial eligibility matcher (ClinicalTrials.gov)
- Discharge-summary plain-language rewrite

### Insurance
- FNOL → structured claim
- Policy-coverage QA over declarations
- Subrogation-potential flagger
- Fraud-pattern detector (photos + metadata)
- Medicare supplement plan-compare agent

### HR / Recruiting
- Resume-to-JD scorer with bias guardrails
- Interview-transcript competency grader
- 9-box performance synthesizer
- Benefits-enrollment Q&A from SPDs
- Policy-handbook chatbot

### Sales / CRM
- Inbound-lead enrichment + routing
- Call-recording MEDDIC coach
- Account-plan from 10-K + news
- Win/loss analysis from Salesforce notes
- RFP autofill from past wins

### SaaS / DevOps / Security
- Incident post-mortem from PagerDuty + Slack — **✅ shipped as `incident_postmortem` recipe**
- Cloud-cost anomaly explainer (AWS CUR)
- CVE-to-ticket triager
- SOC2 control-evidence collector
- On-call runbook agent

### Real Estate
- MLS-listing enrichment + valuation
- Lease-abstraction (commercial) — **🟡 scaffolded**
- Title-defect spotter (recorded-deed PDFs)
- HOA-document compliance check
- Zoning Q&A over city-code PDFs

### Government / Public-Sector
- SAM.gov RFP-match notifier
- FOIA-response redaction agent
- Policy-comment summarizer (Regulations.gov)
- 311 citizen-intent router
- Permit-application completeness checker

## Notes for the roadmap

- The Drata/Vanta/Hebbia/Harvey analogues in OSS are still missing. A cookbook recipe that demos each closes the "but what's the enterprise use case?" question instantly.
- Data sources matter: **every recipe should seed from a PUBLIC corpus** (SEC EDGAR, CMS, SAM.gov, USPTO, CUAD, OpenEnergy, state RRCs, IRS.gov). Never private competitor data.
- Framework diversity is a marketing asset on its own — "here's the same thing in 6 frameworks" is a rare artifact.
- The top cookbooks (OpenAI, Anthropic, awesome-llm-apps) get stars via *breadth of use cases*, not depth of one. Target 100+ recipes long-term.
