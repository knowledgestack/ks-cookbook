# Sample inputs

This flagship reads its input directly from the seeded KS tenant — there is no
standalone input file. The default `--contract-name msa` picks the seeded
Acme MSA from the `cookbook-legal/acme-legal` folder.

To point the demo at a different document already in your tenant, pass
`--contract-name <substring>` (e.g. `--contract-name dpa`, `--contract-name nda`).

To bring your own contract, upload it to any folder in your KS tenant and pass
that folder's `folder_id` via `--corpus-folder <uuid>`.
