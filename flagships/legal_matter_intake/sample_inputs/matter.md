# Sample matter inputs

Use with `make demo-legal-intake`:

1. **Life sciences financing (high risk):**
   - `CLIENT="Northstar Biotech Ltd."`
   - `MATTER="Series B financing + technology license-in from MIT"`

2. **Employment litigation (conflicts check hot):**
   - `CLIENT="Mercer Industrial Services"`
   - `MATTER="Defend constructive dismissal claim by former VP Ops"`

3. **Commercial real estate (fee-estimate focus):**
   - `CLIENT="Harbourfront Holdings Inc."`
   - `MATTER="Acquisition of mixed-use property in downtown Toronto, 18M CAD"`

The agent reads the firm's conflicts XLSX, practice playbook PDF, LSO rules
PDF, engagement letter template PDF, and fee schedule XLSX, then produces a
docx dossier with conflicts, risk tier, fee estimate, required disclosures,
and recommended engagement-letter terms.
