# Default filing

The seed script `ks-backend/seed/seed_10k_corpus.py` pulls a real 10-K from
EDGAR, chunks it, and inserts it into Knowledge Stack. The flagship then
reads from the resulting folder.

No business-input file is required — the agent operates on whatever 10-K is
in the seeded folder. To analyze a different filing, re-run the seed script
pointed at another EDGAR accession number.
