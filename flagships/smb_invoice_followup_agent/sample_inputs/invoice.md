# Default invoice input

Passed as CLI args to `make demo-invoice-followup`:

- `CLIENT="Acme Corp"`
- `INVOICE_NUMBER="INV-2031"`
- `DAYS_OVERDUE=14`
- `INVOICE_CORPUS_FOLDER_ID=<uuid>` — folder with past invoices + email
  threads for this client

The agent searches the corpus for prior interactions, observes tone, and
produces a Markdown draft that can be pasted into Gmail or fed into a
draft-creation API.
