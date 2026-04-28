"""CLI entry for the MSA redline-vs-playbook flagship."""

import argparse
import asyncio
import os
import sys
from pathlib import Path

from msa_redline_vs_playbook.agent import compare_msa, model_id_default
from msa_redline_vs_playbook.schema import DeviationSeverity, RedlineMemo

_SEVERITY_EMOJI = {
    DeviationSeverity.NONE: "OK",
    DeviationSeverity.MINOR: "MINOR",
    DeviationSeverity.MAJOR: "**MAJOR**",
    DeviationSeverity.MISSING: "**MISSING**",
}


def _render_markdown(memo: RedlineMemo) -> str:
    majors = sum(
        1
        for c in memo.clauses
        if c.deviation_severity in (DeviationSeverity.MAJOR, DeviationSeverity.MISSING)
    )
    lines: list[str] = [
        f"# Redline Memo — {memo.inbound_contract_name}",
        f"**Playbook:** {memo.playbook_name}",
        "",
        f"**Executive summary:** {memo.executive_summary}",
        "",
        f"**Clauses reviewed:** {len(memo.clauses)}  "
        f"**Major / Missing deviations:** {majors}",
        "",
    ]
    for i, c in enumerate(memo.clauses, 1):
        sev = _SEVERITY_EMOJI.get(c.deviation_severity, c.deviation_severity.value)
        lines.append(f"## {i}. {c.clause_topic} [{sev}]")
        lines.append("")
        lines.append(f"**Playbook position:** {c.playbook_position}")
        lines.append("")
        lines.append(f"**Inbound position:** {c.inbound_position}")
        lines.append("")
        lines.append(f"**Recommended change:** {c.recommended_change}")
        lines.append("")
        cite_parts = [f"playbook chunk:{c.playbook_citation}"]
        if c.inbound_citation:
            cite_parts.append(f"inbound chunk:{c.inbound_citation}")
        lines.append(f"*Citations: {'; '.join(cite_parts)}*")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compare an inbound MSA against a company playbook and produce a redline memo."
    )
    parser.add_argument(
        "--corpus-folder",
        default=os.environ.get(
            "CORPUS_FOLDER_ID",
            "a4bdb206-d45a-50fa-9b62-071966226eb8",
        ),
        help="folder_id of the legal-redline corpus in your KS tenant.",
    )
    parser.add_argument(
        "--playbook-name",
        default="bonterms_playbook",
        help="Substring to match the playbook document name (default: bonterms_playbook).",
    )
    parser.add_argument(
        "--inbound-name",
        default="commonpaper_inbound",
        help="Substring to match the inbound MSA document name (default: commonpaper_inbound).",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("msa-redline-memo.md"),
        help="Output markdown path (default: msa-redline-memo.md).",
    )
    parser.add_argument(
        "--model",
        default=model_id_default(),
        help=f"OpenAI model (default: {model_id_default()}).",
    )
    args = parser.parse_args()

    if not os.environ.get("KS_API_KEY"):
        sys.exit("KS_API_KEY is not set.")
    if not os.environ.get("OPENAI_API_KEY"):
        sys.exit("OPENAI_API_KEY is not set.")

    memo = asyncio.run(
        compare_msa(
            corpus_folder_id=args.corpus_folder,
            playbook_name=args.playbook_name,
            inbound_name=args.inbound_name,
            model=args.model,
        )
    )
    md = _render_markdown(memo)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(md)
    majors = sum(
        1
        for c in memo.clauses
        if c.deviation_severity in (DeviationSeverity.MAJOR, DeviationSeverity.MISSING)
    )
    print(
        f"Compared {len(memo.clauses)} clauses between "
        f"{memo.playbook_name!r} and {memo.inbound_contract_name!r}. "
        f"{majors} major/missing deviations. Wrote: {args.out}"
    )


if __name__ == "__main__":
    main()
