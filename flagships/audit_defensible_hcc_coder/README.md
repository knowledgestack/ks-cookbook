# audit_defensible_hcc_coder

Healthcare flagship — assigns HCC / ICD-10 codes from a longitudinal chart,
with a line-level rationale and a `[chunk:<uuid>]` citation per code.

**Market gap.** Existing AI coders return codes but no defense — when CMS
audits, the provider can't show *why* the code was assigned. This flagship
shows how Knowledge Stack's chunk-level provenance gives you an audit trail
for free.

**Run:**

```bash
HCC_CORPUS_FOLDER_ID=<your-folder> make demo-hcc-coder
```
