# smb_invoice_followup_agent

SMB flagship — drafts an overdue-invoice follow-up email whose tone matches
the client's historical communication style, grounded in past invoices +
email threads stored in Knowledge Stack.

**Market gap.** An r/smallbusiness thread (cited in the GTM research) called
out the missing sub-$200/month tool: nothing ties Stripe invoice data to
tone-matched Gmail drafts. Freelancers copy-paste manually. This flagship
is the smallest-possible KS showcase — `find` + `read` replacing a bespoke
retrieval pipeline — and proves you don't need a data lake to do grounded AI.

**Run:**

```bash
INVOICE_CORPUS_FOLDER_ID=<uuid> CLIENT="Acme Corp" \
  INVOICE_NUMBER="INV-2031" make demo-invoice-followup
```
