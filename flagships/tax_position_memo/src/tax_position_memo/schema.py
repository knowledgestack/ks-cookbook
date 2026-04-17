"""Tax position memo template for LangGraph markdown output."""


MEMO_TEMPLATE = """\
# Tax Position Research Memorandum

**Question:** {question}
**Date:** {date}
**Prepared By:** Automated Draft (Tax SOP v2025)

## 1. Statement of Facts
<relevant facts and transaction description>

## 2. Issue(s) Presented
<precise tax question(s) to be resolved>

## 3. Conclusion
<bottom-line answer with confidence level: Should / MLTN / Substantial
Authority / Reasonable Basis>

## 4. Analysis

### Step 1: Applicable Code Sections
<identify and cite the relevant IRC sections>

### Step 2: Treasury Regulations
<cite and analyze applicable Treasury Regulations>

### Step 3: Case Law & Administrative Guidance
<relevant court decisions, Revenue Rulings, PLRs — if available in corpus>

### Step 4: Application to Facts
<apply the authorities to the specific facts>

## 5. Risk Assessment
<risk level: Low / Moderate / High / Aggressive>
<potential exposure, penalties, disclosure requirements>

## 6. Recommendations
<recommended position, planning opportunities, next steps>

## 7. Authorities Cited
<numbered list of all authorities referenced>

## Citations
<numbered list; each entry: document_name — [chunk:<uuid>] "quote">
"""
