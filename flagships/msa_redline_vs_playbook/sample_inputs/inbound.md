# Default playbook + inbound

Passed as CLI args to `make demo-msa-redline`:

- `PLAYBOOK_NAME="bonterms_playbook"` — the company's standard position (seeded).
- `INBOUND_NAME="commonpaper_inbound"` — the counterparty's inbound MSA (seeded).

Both documents must exist in the tenant at the folder referenced by
`LEGAL_REDLINE_FOLDER_ID`. The seed script
`ks-backend/seed/seed_legal_redline_corpus.py` inserts both.

## Use with your own documents

Upload your playbook + the inbound under the same folder, then rerun:

```bash
PLAYBOOK_NAME="acme_playbook" INBOUND_NAME="vendor_msa_v2" \
  LEGAL_REDLINE_FOLDER_ID=<your-folder> make demo-msa-redline
```
