"""Well-log summarizer CLI."""


import argparse
import asyncio
import os
import sys
from pathlib import Path

from well_log_summarizer.agent import summarize_well
from well_log_summarizer.schema import WellSummary


def _render_markdown(s: WellSummary) -> str:
    lines: list[str] = [
        f"# Well Log Summary — {s.well_id}",
        "",
        f"**Operator:** {s.operator}",
        f"**Location:** {s.location}",
        f"**HSE risk rating:** {s.hse_risk_rating}",
        "",
        "## Depth",
        s.depth_summary,
        "",
        "## Formation notes",
        s.formation_notes,
        "",
        "## Events",
    ]
    for ev in s.events:
        lines.append(f"### [{ev.event_type.upper()}] severity: {ev.severity}")
        lines.append(ev.description)
        lines.append("")
        lines.append("**Evidence:**")
        for c in ev.citations:
            snippet = (c.snippet or "").replace("\n", " ").strip()[:240]
            lines.append(f"- *{c.document_name}* (chunk:{c.chunk_id}): \u201c{snippet}\u201d")
        lines.append("")

    lines.append("## Recommended actions")
    for a in s.recommended_actions:
        lines.append(f"- {a}")
    return "\n".join(lines)


def main() -> None:
    p = argparse.ArgumentParser(description="Summarize a well's drilling reports and logs.")
    p.add_argument("--well-id", required=True, help="API well number or operator well name.")
    p.add_argument(
        "--corpus-folder",
        default=os.environ.get(
            "ENERGY_CORPUS_FOLDER_ID", "ab926019-ac7a-579f-bfda-6c52a13c5f41",
        ),
        help="Folder.id of the energy corpus in your KS tenant.",
    )
    p.add_argument("--model", default=os.environ.get("MODEL", "gpt-4o"))
    p.add_argument("--out", type=Path, default=Path("well-summary.md"))
    args = p.parse_args()

    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY in .env.")

    summary = asyncio.run(summarize_well(
        well_id=args.well_id, corpus_folder_id=args.corpus_folder, model=args.model,
    ))
    args.out.write_text(_render_markdown(summary))
    n_cites = sum(len(e.citations) for e in summary.events)
    print(
        f"Wrote {args.out} — well={summary.well_id} "
        f"hse_risk={summary.hse_risk_rating} events={len(summary.events)} citations={n_cites}"
    )


if __name__ == "__main__":
    main()
