# legal_matter_intake

**Sertain flagship** — a new client + matter triggers a full intake dossier
grounded in the firm's conflicts database (XLSX), practice-area risk playbook
(PDF), jurisdiction rules (PDF), and fee schedule (XLSX).

**Why it's a moat demo for DB Streams.** Sertain-style small/mid-firm legal
software stores these artifacts as PDFs and Excel files. A raw LLM can't
audit a conflicts XLSX at the row level or cite into an LSO/Bar Association
PDF. Knowledge Stack gives the agent chunk-level access to all of them in a
single MCP session.

**Shows off:** XLSX row-level conflict hits, cross-corpus reasoning
(conflicts + playbook + jurisdiction rules + fees), structured dossier with
a risk tier and recommended engagement-letter terms.

**Run:**

```bash
LEGAL_CORPUS_FOLDER_ID=<uuid> \
  CLIENT="Northstar Biotech Ltd." \
  MATTER="Series B financing + license-in from MIT" \
  make demo-legal-intake
```
