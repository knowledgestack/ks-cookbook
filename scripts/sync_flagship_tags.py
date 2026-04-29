#!/usr/bin/env python3
"""Make tags first-class metadata on every flagship.

Tags live in PEP 621 ``[project.keywords]`` of each flagship's ``pyproject.toml``
— that's the source of truth. The wiki book and the tag index are generated
from it. To tag a new flagship, set ``keywords = [...]`` in its pyproject.

Run idempotently:

    uv run python scripts/sync_flagship_tags.py            # write/update keywords
    uv run python scripts/sync_flagship_tags.py --check    # CI: fail if any flagship is untagged
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    import tomllib  # 3.11+
except ImportError:  # pragma: no cover
    import tomli as tomllib  # type: ignore[no-redef]

ROOT = Path(__file__).resolve().parent.parent
FLAGSHIPS = ROOT / "flagships"

# Source of truth for every flagship's tags. First tag is the primary vertical.
TAGS: dict[str, list[str]] = {
    "adverse_event_narrative":       ["pharma", "pharmacovigilance", "cioms", "safety"],
    "aml_sar_narrative":             ["banking", "aml", "sar", "compliance"],
    "api_doc_generator":             ["engineering", "api", "documentation", "devex"],
    "audit_defensible_hcc_coder":    ["healthcare", "hcc", "risk-adjustment", "coding"],
    "audit_workpaper_drafter":       ["accounting", "audit", "pcaob", "workpapers"],
    "chiro_visit_autopilot":         ["healthcare", "ehr", "soap-notes", "chiropractic"],
    "claim_adjudication_memo":       ["insurance", "claims", "coverage-analysis", "p-and-c"],
    "claims_denial_rebuttal_drafter":["insurance", "claims", "appeals", "rebuttal"],
    "clinical_trial_eligibility":    ["healthcare", "clinical-trials", "eligibility", "ctms"],
    "compliance_questionnaire":      ["security", "compliance", "caiq", "sig", "questionnaires"],
    "condo_board_decision_pack":     ["real-estate", "condo", "hoa", "governance"],
    "construction_rfi_agent":        ["engineering", "construction", "rfi", "field-ops"],
    "contract_obligation_extractor": ["legal", "contracts", "msa", "obligations"],
    "contract_redline_with_provenance":["legal", "contracts", "redline", "provenance"],
    "conversational_sdr_bot":        ["sales", "sdr", "outbound", "chat"],
    "credit_memo_drafter":           ["banking", "credit-risk", "underwriting", "commercial-lending"],
    "csv_enrichment":                ["sales", "data-enrichment", "batch", "operations"],
    "earnings_risk_analyzer":        ["finance", "sec-filings", "10-k", "investment-research"],
    "employee_handbook_qa":          ["hr", "handbook", "q-and-a"],
    "foia_response_drafter":         ["government", "foia", "public-records"],
    "grant_compliance_checker":      ["government", "grants", "compliance", "cfr"],
    "incident_runbook_lookup":       ["engineering", "sre", "runbooks", "incident-response"],
    "insurance_policy_comparison":   ["insurance", "policy-comparison", "coverage"],
    "job_description_generator":     ["hr", "recruiting", "job-descriptions"],
    "kyc_onboarding_review":         ["banking", "kyc", "aml", "compliance"],
    "lease_abstract":                ["real-estate", "leases", "commercial"],
    "legal_matter_intake":           ["legal", "matter-intake", "triage", "ops"],
    "loan_covenant_monitor":         ["banking", "covenant-monitoring", "credit-risk"],
    "msa_redline_vs_playbook":       ["legal", "contracts", "redline", "negotiations"],
    "nerc_compliance_evidence":      ["energy", "nerc-cip", "compliance", "utilities"],
    "prior_auth_letter":             ["healthcare", "prior-auth", "payer", "clinical"],
    "privacy_impact_assessment":     ["legal", "privacy", "gdpr", "security"],
    "realtime_voice_sdr":            ["sales", "voice", "sdr", "realtime"],
    "release_notes_generator":       ["product", "engineering", "release-notes"],
    "research_brief":                ["research", "reports", "analyst"],
    "rev_rec_memo":                  ["accounting", "asc-606", "revenue-recognition", "memos"],
    "rfp_first_draft":               ["sales", "rfp", "proposals", "go-to-market"],
    "sales_battlecard":              ["sales", "competitive", "enablement"],
    "smb_invoice_followup_agent":    ["sales", "ar", "collections", "smb"],
    "sow_scope_validator":           ["proserv", "sow", "scope-management"],
    "subrogation_opportunity_review":["insurance", "subrogation", "claims"],
    "tax_position_memo":             ["tax", "irc", "research", "memos"],
    "well_log_summarizer":           ["energy", "oil-and-gas", "well-logs", "geology"],
    "zoning_compliance_check":       ["real-estate", "zoning", "compliance", "municipal"],
}


def render_keywords(tags: list[str]) -> str:
    quoted = ", ".join(f'"{t}"' for t in tags)
    return f"keywords = [{quoted}]"


def upsert_keywords(pyproject: Path, tags: list[str]) -> bool:
    """Write keywords = [...] into [project] table. Returns True if changed."""
    text = pyproject.read_text()
    new_line = render_keywords(tags)

    lines = text.splitlines()
    in_project = False
    keywords_idx: int | None = None
    insert_after_idx: int | None = None

    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            in_project = (stripped == "[project]")
            continue
        if not in_project:
            continue
        if stripped.startswith("keywords"):
            keywords_idx = i
            break
        if stripped.startswith("readme"):
            insert_after_idx = i

    if keywords_idx is not None:
        if lines[keywords_idx] == new_line:
            return False
        lines[keywords_idx] = new_line
    elif insert_after_idx is not None:
        lines.insert(insert_after_idx + 1, new_line)
    else:
        # Fallback: append at end of [project] block (after the table header).
        for i, line in enumerate(lines):
            if line.strip() == "[project]":
                lines.insert(i + 1, new_line)
                break
        else:
            return False  # No [project] table; skip.

    pyproject.write_text("\n".join(lines) + ("\n" if not text.endswith("\n") or True else ""))
    return True


def read_keywords(pyproject: Path) -> list[str]:
    data = tomllib.loads(pyproject.read_text())
    return list(data.get("project", {}).get("keywords", []))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true",
                        help="Exit non-zero if any flagship is missing tags")
    args = parser.parse_args()

    flagship_dirs = sorted(d for d in FLAGSHIPS.iterdir()
                           if d.is_dir() and not d.name.startswith("_"))

    missing: list[str] = []
    untagged: list[str] = []
    changed: list[str] = []

    for d in flagship_dirs:
        py = d / "pyproject.toml"
        if not py.exists():
            missing.append(d.name)
            continue
        tags = TAGS.get(d.name)
        if not tags:
            untagged.append(d.name)
            continue
        if args.check:
            if read_keywords(py) != tags:
                untagged.append(d.name)
        else:
            if upsert_keywords(py, tags):
                changed.append(d.name)

    if missing:
        print("missing pyproject.toml:", ", ".join(missing), file=sys.stderr)
    if args.check:
        if untagged:
            print("flagships with stale or missing tags:",
                  ", ".join(untagged), file=sys.stderr)
            return 1
        print(f"all {len(flagship_dirs)} flagships tagged ✓")
        return 0

    print(f"updated {len(changed)} pyproject(s); "
          f"{len(flagship_dirs) - len(changed) - len(untagged)} already current; "
          f"{len(untagged)} untagged")
    if untagged:
        print("untagged:", ", ".join(untagged), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
