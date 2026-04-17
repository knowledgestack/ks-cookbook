# Audit Workpaper Drafter


**Tags:** `accounting` `audit` `pcaob` `workpapers`

Given an account name and trial balance amount, drafts an audit workpaper tying the balance to source documents with citations to audit standards and company accounting policy.

Uses LangGraph ReAct agent with MCP tools.

## Seed data required

This demo reads from a folder in your Knowledge Stack tenant. You need to create that folder and upload the expected documents **before** running, otherwise retrieval returns nothing and the demo fails with empty output.

**Expected corpus:** PCAOB AS 1215, company revenue-recognition policy, trial balance, sample invoices.

Set-up steps:

1. Sign up at [app.knowledgestack.ai](https://app.knowledgestack.ai).
2. Create a folder in the dashboard and copy its folder ID.
3. Upload the documents described above into that folder.
4. Issue an API key from the dashboard and put it in `.env` as `KS_API_KEY`.
5. Run: `AUDIT_CORPUS_FOLDER_ID=<your-folder-id> make demo-audit-workpaper`

Full corpus matrix for every flagship: [`docs/wiki/seed-data.md`](../../docs/wiki/seed-data.md).

## Data Sources

- **PCAOB AS 1215:** Audit Documentation standard (pcaobus.org, public)
- **AU-C Section 500:** Audit Evidence procedures (AICPA, public)
- **Accounting Policy:** Synthetic Acme SaaS policy (realistic)
- **Trial Balance:** Synthetic 5-line trial balance (realistic)
