# Audit Workpaper Drafter

Given an account name and trial balance amount, drafts an audit workpaper tying the balance to source documents with citations to audit standards and company accounting policy.

Uses LangGraph ReAct agent with MCP tools.

## Data Sources

- **PCAOB AS 1215:** Audit Documentation standard (pcaobus.org, public)
- **AU-C Section 500:** Audit Evidence procedures (AICPA, public)
- **Accounting Policy:** Synthetic Acme SaaS policy (realistic)
- **Trial Balance:** Synthetic 5-line trial balance (realistic)
