# Government: FOIA Response Drafter

Drafts a FOIA response letter with exemption analysis citing the DOJ guide
and agency SOP. Uses **raw OpenAI** with inline MCP helpers.

## Run

```bash
# 1. Seed the FOIA corpus
cd ks-backend
uv run --env-file .env.e2e python seed/seed_government_foia_corpus.py

# 2. From the cookbook
cd knowledgestack-cookbook
make demo-foia-response REQUEST="All records related to contract awards for IT services in FY2025"
```

Output: `foia-response.md` with cover letter, exemption analysis, and redaction notes.
