# Zoning Compliance Check (Real Estate)

Proposed use at a commercial address checked against the City of Austin Land
Development Code (Chapter 25-2) zoning ordinance.

**Framework:** LangGraph ReAct agent with MCP

## Data Sources
- Austin TX Land Development Code, Chapter 25-2 (Zoning Districts)
- Austin TX LDC permitted uses table (Subchapter C, Article 2)
- Austin TX LDC conditional use permit process
- Source: https://library.municode.com/tx/austin/codes/land_development_code

## Quick Start

```bash
# 1. Seed the corpus (from ks-backend/)
uv run --env-file .env.e2e python seed/seed_realestate_zoning_corpus.py

# 2. Run the demo (from knowledgestack-cookbook/)
make demo-zoning-check CORPUS_FOLDER_ID=<id-from-step-1>

# Custom scenario:
make demo-zoning-check \
  CORPUS_FOLDER_ID=<id> \
  ADDRESS="500 E 6th St, Austin, TX" \
  ZONE_DISTRICT="CBD" \
  PROPOSED_USE="nightclub"
```

## Output
`zoning-compliance.md` with YES/CONDITIONAL/NO/VARIANCE_REQUIRED determination,
applicable LDC sections, compatibility standards, and next steps.
