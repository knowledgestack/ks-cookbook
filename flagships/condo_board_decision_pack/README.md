# condo_board_decision_pack

**CondoStack flagship** — turns a unit-owner architectural request into a
board-meeting-ready decision memo, grounded in the corporation's governing
documents (Declaration, Bylaws, Rules, ACC Guidelines), the reserve-fund
study, and historical board minutes.

**Why it's a moat demo for DB Streams.** Condo docs are a nightmare: 50-page
PDFs, scanned amendments, XLSX reserve-fund schedules. A raw LLM can't cite
into them. Knowledge Stack ingests PDFs + XLSX, returns chunks with UUIDs,
and the agent stitches together a defensible decision pack in one call.

**Shows off:** multi-document reasoning, PDF + XLSX grounding, historical
precedent search via `search_keyword`, reserve-fund cost impact from XLSX
chunks, docx output a property manager can drop straight into a board packet.

**Run:**

```bash
CONDO_CORPUS_FOLDER_ID=<uuid> \
  REQUEST="Unit 4B requests to install 12 solar panels on the roof terrace" \
  make demo-condo-board
```
