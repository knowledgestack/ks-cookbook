# Default draft + playbook input

Passed as CLI args to `make demo-contract-redline`:

- `PLAYBOOK_FOLDER_ID=<uuid>` — firm's negotiation playbook in KS
- `DRAFT_FOLDER_ID=<uuid>` — corpus containing the counterparty draft
- `INBOUND_NAME=counterparty_msa_v2`
- `PLAYBOOK_NAME=firm_msa_playbook`

The agent opens both corpora in one MCP session, reads the counterparty
draft + every relevant playbook rule, and emits a Word redline memo. Every
proposed edit cites both the offending clause and the governing playbook rule
by chunk UUID.
