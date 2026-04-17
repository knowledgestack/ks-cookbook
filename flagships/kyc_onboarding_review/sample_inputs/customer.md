# Default customer file

The seed script `ks-backend/seed/seed_kyc_corpus.py` inserts a sample customer
onboarding package alongside the bank's CDD policy. The flagship reads the
package from the tenant — no business-input file is needed.

Default customer in the seeded corpus: **Verdant Sourcing Group LLC**
(Delaware LLC, commodity trading, beneficial owners disclosed, adverse media
hits present).

## Use with your own customer

Upload the customer's documents into the same seeded folder, then rerun:

```bash
KYC_CORPUS_FOLDER_ID=<your-folder> make demo-kyc-review
```
