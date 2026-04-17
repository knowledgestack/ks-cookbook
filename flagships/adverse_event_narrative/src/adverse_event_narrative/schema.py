"""CIOMS narrative memo template for LangGraph markdown output."""


MEMO_TEMPLATE = """\
# Adverse Event Narrative — CIOMS Format

**Case ID:** {case_id}
**Drug Name:** {drug_name}
**Event Term(s):** {event_terms}
**Reporter:** Automated Draft (PV SOP v2025)

## 1. Patient Information
<demographics, relevant medical history if available>

## 2. Drug Information
<drug name, indication, dose, route, start/stop dates — cite drug label>

## 3. Event Description
<detailed narrative of the adverse event in chronological order>

## 4. Relevant Lab/Diagnostic Data
<any labs, imaging, or diagnostic findings — or "Not available">

## 5. Dechallenge / Rechallenge
<response to drug withdrawal/reintroduction — or "Not applicable">

## 6. Causality Assessment
<assessment per WHO-UMC or Naranjo scale, citing PV SOP criteria>

## 7. Seriousness Criteria
<which ICH E2A seriousness criteria are met: death, life-threatening,
hospitalization, disability, congenital anomaly, medically important>

## 8. Reporter Assessment
<reporter's own causality opinion if available>

## Citations
<numbered list; each entry: document_name — [chunk:<uuid>] "quote">
"""
