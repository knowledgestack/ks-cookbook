# chiro_visit_autopilot

**ChiroCRM flagship** — a single visit SOAP note becomes three fully cited
artifacts in one run: a CPT/ICD-10 coding sheet (XLSX), a payer prior-auth
letter (DOCX), and a patient-friendly plan-of-care (MD). Every output cites
chunks from the clinic's payer policy PDF, treatment protocol PDF, and
fee-schedule XLSX.

**Why it's a moat demo for DB Streams.** Chiropractic and dental practices
drown in PDFs (scanned visit notes, EOBs, insurance policies) and XLSX
(clinic fee schedules, CPT references). No raw LLM can cite into all of
them at the row + page level. Knowledge Stack can, and the agent turns a
single MCP session into three different deliverables for three audiences.

**Shows off:** one-call → three outputs, PDF + XLSX grounding, coding
rationale tied to both the visit note and the payer policy, patient-facing
language vs payer-facing language from the same evidence.

**Run:**

```bash
CHIRO_CORPUS_FOLDER_ID=<uuid> \
  PATIENT_ID=PT-4401 VISIT_DATE=2026-04-18 \
  make demo-chiro-autopilot
```
