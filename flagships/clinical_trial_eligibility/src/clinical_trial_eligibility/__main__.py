"""Clinical trial eligibility assessment CLI."""


import argparse
import asyncio
import os
import sys
from pathlib import Path

from clinical_trial_eligibility.agent import assess_eligibility
from clinical_trial_eligibility.schema import EligibilityAssessment


def _render_markdown(assess: EligibilityAssessment) -> str:
    lines = [
        f"# Eligibility Assessment — {assess.trial_title}",
        f"**Trial:** {assess.trial_id}",
        f"**Patient:** {assess.patient_summary}",
        f"**Overall Eligibility:** {assess.overall_eligibility.value}",
        "",
    ]

    for i, c in enumerate(assess.criteria, 1):
        status_icon = {
            "ELIGIBLE": "PASS",
            "INELIGIBLE": "FAIL",
            "UNCERTAIN": "????",
        }.get(c.match_status.value, "??")
        lines += [
            f"## {i}. [{status_icon}] {c.criterion_type.upper()}: "
            f"{c.criterion_text[:80]}",
            f"*Status: {c.match_status.value}*",
            "",
            c.rationale,
            "",
            "**Evidence:**",
        ]
        for cit in c.citations:
            q = (cit.quote or "").replace("\n", " ").strip()[:300]
            lines.append(
                f"- *{cit.source_document}* "
                f"(chunk:{cit.chunk_id}): \u201c{q}\u201d"
            )
        lines.append("")

    lines += [
        "## Recommended Next Steps",
        assess.recommended_next_steps,
    ]
    return "\n".join(lines)


def _load_patient(in_path: Path | None) -> str:
    if in_path is not None:
        return in_path.read_text(encoding="utf-8")
    default = (
        Path(__file__).resolve().parents[2] / "sample_inputs" / "patient.txt"
    )
    return default.read_text(encoding="utf-8")


def main() -> None:
    p = argparse.ArgumentParser(
        description="Assess patient eligibility for a clinical trial."
    )
    p.add_argument(
        "--in",
        dest="in_path",
        type=Path,
        default=None,
        help="Patient profile file (default: sample_inputs/patient.txt).",
    )
    p.add_argument(
        "--corpus-folder",
        default=os.environ.get("CORPUS_FOLDER_ID", ""),
    )
    p.add_argument(
        "--model",
        default=os.environ.get("MODEL", "gpt-4o"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("trial-eligibility.md"),
    )
    args = p.parse_args()

    if not os.environ.get("KS_API_KEY") or not os.environ.get(
        "OPENAI_API_KEY"
    ):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY in .env.")
    patient = _load_patient(args.in_path)
    assessment = asyncio.run(
        assess_eligibility(
            patient_profile=patient,
            corpus_folder_id=args.corpus_folder or None,
            model=args.model,
        )
    )
    args.out.write_text(_render_markdown(assessment))
    total_cites = sum(len(c.citations) for c in assessment.criteria)
    print(
        f"Wrote {args.out} -- {assessment.trial_id}, "
        f"{len(assessment.criteria)} criteria, {total_cites} citations, "
        f"eligibility: {assessment.overall_eligibility.value}"
    )


if __name__ == "__main__":
    main()
