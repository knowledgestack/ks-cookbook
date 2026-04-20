# MSA Redline vs Playbook


**Tags:** `legal` `contracts` `redline` `negotiations`

Compare an inbound MSA clause-by-clause against your company's standard playbook. Produces a redline memo with deviation severity and recommended changes, citing both documents.

Uses raw OpenAI function-calling with inline MCP client.

## Seed data required

This demo reads from a folder in your Knowledge Stack tenant. You need to create that folder and upload the expected documents **before** running, otherwise retrieval returns nothing and the demo fails with empty output.

**Expected corpus:** Your company's MSA playbook + an inbound MSA to compare against.

Set-up steps:

1. Sign up at [app.knowledgestack.ai](https://app.knowledgestack.ai).
2. Create a folder in the dashboard and copy its folder ID.
3. Upload the documents described above into that folder.
4. Issue an API key from the dashboard and put it in `.env` as `KS_API_KEY`.
5. Run: `LEGAL_REDLINE_FOLDER_ID=<your-folder-id> make demo-msa-redline`

Full corpus matrix for every flagship: [`docs/wiki/seed-data.md`](../../docs/wiki/seed-data.md).

## Run

```bash
make demo-msa-redline
# override:
PLAYBOOK_NAME=bonterms_playbook INBOUND_NAME=commonpaper_inbound \
LEGAL_REDLINE_FOLDER_ID=<your-folder-id> make demo-msa-redline
```

Output: `flagships/msa_redline_vs_playbook/sample_output.md` — per-clause
diff vs the playbook with severity, a proposed redline, and the chunk
citations on both sides.

## Data Sources

- **Playbook:** Bonterms Cloud Terms v1.0 (CC BY 4.0) - https://github.com/Bonterms/Cloud-Terms
- **Inbound MSA:** Common Paper Cloud Service Agreement v2.1 (CC BY 4.0) - https://github.com/CommonPaper/CSA
