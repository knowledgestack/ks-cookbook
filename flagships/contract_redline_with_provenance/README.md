# contract_redline_with_provenance

Legal flagship — generates a Word (.docx) redline memo for any inbound
contract. Every proposed edit carries both the offending clause chunk UUID
(from the counterparty draft corpus) and the governing playbook rule chunk
UUID (from the firm's playbook corpus).

**Market gap.** The Harvey AI Reddit debate (Feb 2026) crystallized the GC
complaint: agentic drafting hides the middle steps. This flagship shows how
multi-corpus grounding in a single Knowledge Stack MCP session gives you
traceable redlines without a dual-pipeline build.

Distinct from `msa_redline_vs_playbook` (markdown memo): this flagship
outputs a Word redline doc with tracked-change language, suitable for sending
directly to opposing counsel.

**Run:**

```bash
PLAYBOOK_FOLDER_ID=<uuid> DRAFT_FOLDER_ID=<uuid> make demo-contract-redline
```
