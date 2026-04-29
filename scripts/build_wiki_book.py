#!/usr/bin/env python3
"""Assemble a 'book' under docs/wiki/book/ from every flagship and recipe README.

Each flagship README and each recipe README is included verbatim (with heading
levels shifted down) so the wiki contains every example end-to-end. Re-run
whenever a README changes:

    uv run python scripts/build_wiki_book.py
"""

from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FLAGSHIPS = ROOT / "flagships"
RECIPES = ROOT / "recipes"
BOOK = ROOT / "docs" / "wiki" / "book"

FLAGSHIP_VERTICALS: dict[str, str] = {
    "credit_memo_drafter": "banking",
    "loan_covenant_monitor": "banking",
    "kyc_onboarding_review": "banking",
    "earnings_risk_analyzer": "banking",
    "aml_sar_narrative": "banking",
    "contract_obligation_extractor": "legal",
    "msa_redline_vs_playbook": "legal",
    "privacy_impact_assessment": "legal",
    "contract_redline_with_provenance": "legal",
    "legal_matter_intake": "legal",
    "rev_rec_memo": "accounting",
    "audit_workpaper_drafter": "accounting",
    "tax_position_memo": "accounting",
    "audit_defensible_hcc_coder": "accounting",
    "prior_auth_letter": "healthcare",
    "clinical_trial_eligibility": "healthcare",
    "chiro_visit_autopilot": "healthcare",
    "claim_adjudication_memo": "insurance",
    "subrogation_opportunity_review": "insurance",
    "insurance_policy_comparison": "insurance",
    "claims_denial_rebuttal_drafter": "insurance",
    "lease_abstract": "real-estate",
    "zoning_compliance_check": "real-estate",
    "condo_board_decision_pack": "real-estate",
    "csv_enrichment": "sales",
    "research_brief": "sales",
    "rfp_first_draft": "sales",
    "sales_battlecard": "sales",
    "compliance_questionnaire": "sales",
    "conversational_sdr_bot": "sales",
    "realtime_voice_sdr": "sales",
    "smb_invoice_followup_agent": "sales",
    "employee_handbook_qa": "hr",
    "job_description_generator": "hr",
    "incident_runbook_lookup": "engineering",
    "api_doc_generator": "engineering",
    "release_notes_generator": "engineering",
    "sow_scope_validator": "engineering",
    "construction_rfi_agent": "engineering",
    "grant_compliance_checker": "government",
    "foia_response_drafter": "government",
    "adverse_event_narrative": "government",
    "nerc_compliance_evidence": "government",
}

VERTICAL_ORDER = [
    ("banking", "Banking & financial services"),
    ("legal", "Legal"),
    ("accounting", "Accounting & tax"),
    ("healthcare", "Healthcare"),
    ("insurance", "Insurance"),
    ("real-estate", "Real estate"),
    ("sales", "Sales & revenue"),
    ("hr", "HR"),
    ("engineering", "Engineering, product & SRE"),
    ("government", "Government, pharma & energy"),
    ("other", "Other"),
]

HEADING_RE = re.compile(r"^(#{1,6})\s", re.MULTILINE)


def shift_headings(md: str, by: int = 1) -> str:
    """Demote every Markdown heading by `by` levels (capped at h6)."""

    def repl(m: re.Match[str]) -> str:
        hashes = "#" * min(len(m.group(1)) + by, 6)
        return f"{hashes} "

    return HEADING_RE.sub(repl, md)


def read_readme(pkg_dir: Path) -> str | None:
    f = pkg_dir / "README.md"
    return f.read_text() if f.exists() else None


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def render_chapter(title: str, source_path: Path, body: str | None) -> str:
    rel = source_path.relative_to(ROOT)
    if not body:
        return f"## {title}\n\n_README missing: [`{rel}`](../../../{rel})._\n\n"
    return (
        f"## {title}\n\n"
        f"> Source: [`{rel}`](../../../{rel})\n\n"
        f"{shift_headings(body, by=2).strip()}\n\n"
        f"---\n\n"
    )


def build_flagships_book() -> None:
    by_vertical: dict[str, list[Path]] = defaultdict(list)
    for d in sorted(FLAGSHIPS.iterdir()):
        if not d.is_dir() or d.name.startswith("_"):
            continue
        by_vertical[FLAGSHIP_VERTICALS.get(d.name, "other")].append(d)

    BOOK.mkdir(parents=True, exist_ok=True)
    flagships_dir = BOOK / "flagships"
    flagships_dir.mkdir(exist_ok=True)

    toc_lines = ["# Flagships book\n"]
    toc_lines.append(
        "Every flagship README, grouped by vertical, in one navigable book. "
        "Every chapter is generated from `flagships/<name>/README.md` — edit the "
        "source README, then re-run `scripts/build_wiki_book.py`.\n"
    )
    toc_lines.append("## Chapters\n")

    for key, label in VERTICAL_ORDER:
        if not by_vertical.get(key):
            continue
        chapter_path = flagships_dir / f"{key}.md"
        chunks = [f"# {label}\n\n_Generated. Do not edit by hand._\n\n"]
        chunks.append("[← Back to flagships book](../flagships.md)\n\n")
        for d in sorted(by_vertical[key]):
            body = read_readme(d)
            chunks.append(render_chapter(d.name, d, body))
        chapter_path.write_text("".join(chunks))
        toc_lines.append(
            f"- [{label}](flagships/{key}.md) — {len(by_vertical[key])} flagships"
        )

    (BOOK / "flagships.md").write_text("\n".join(toc_lines) + "\n")


def build_recipes_book() -> None:
    recipes_dir = BOOK / "recipes"
    recipes_dir.mkdir(parents=True, exist_ok=True)

    pkgs = sorted(
        d for d in RECIPES.iterdir()
        if d.is_dir() and not d.name.startswith("_")
    )

    # Bucket alphabetically: a-d, e-h, i-l, m-p, q-t, u-z
    buckets: dict[str, list[Path]] = defaultdict(list)
    for d in pkgs:
        first = d.name[0].lower()
        if first <= "d":
            key = "a-d"
        elif first <= "h":
            key = "e-h"
        elif first <= "l":
            key = "i-l"
        elif first <= "p":
            key = "m-p"
        elif first <= "t":
            key = "q-t"
        else:
            key = "u-z"
        buckets[key].append(d)

    bucket_order = ["a-d", "e-h", "i-l", "m-p", "q-t", "u-z"]
    toc = ["# Recipes book\n"]
    toc.append(
        "Every recipe README, alphabetized into chapters, in one navigable book. "
        "Every chapter is generated from `recipes/<name>/README.md` — edit the "
        "source README, then re-run `scripts/build_wiki_book.py`.\n"
    )
    toc.append("## Chapters\n")

    for key in bucket_order:
        if not buckets.get(key):
            continue
        chapter = recipes_dir / f"{key}.md"
        chunks = [f"# Recipes {key.upper()}\n\n_Generated. Do not edit by hand._\n\n"]
        chunks.append("[← Back to recipes book](../recipes.md)\n\n")
        for d in sorted(buckets[key]):
            body = read_readme(d)
            chunks.append(render_chapter(d.name, d, body))
        chapter.write_text("".join(chunks))
        toc.append(f"- [Recipes {key.upper()}](recipes/{key}.md) — {len(buckets[key])} recipes")

    (BOOK / "recipes.md").write_text("\n".join(toc) + "\n")


def build_book_root() -> None:
    BOOK.mkdir(parents=True, exist_ok=True)
    (BOOK / "README.md").write_text(
        "# Cookbook book\n\n"
        "Everything in `flagships/` and `recipes/` assembled into a single "
        "readable book — so you can browse every example end-to-end without "
        "leaving the wiki.\n\n"
        "## Sections\n\n"
        "- [Flagships](flagships.md) — 44 production-style agents, grouped by vertical.\n"
        "- [Recipes](recipes.md) — 100+ ≤100-LOC single-file patterns, alphabetized.\n\n"
        "## How this book is built\n\n"
        "Generated by [`scripts/build_wiki_book.py`](../../../scripts/build_wiki_book.py) "
        "from every `flagships/*/README.md` and `recipes/*/README.md`. The source "
        "READMEs remain authoritative — edit them, then re-run:\n\n"
        "```bash\n"
        "uv run python scripts/build_wiki_book.py\n"
        "```\n\n"
        "Each chapter shows the source path so you can jump back to the package "
        "to run it.\n"
    )


def main() -> None:
    build_book_root()
    build_flagships_book()
    build_recipes_book()
    print(f"Wrote book under {BOOK.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
