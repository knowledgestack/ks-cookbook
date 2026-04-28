"""Construction RFI agent CLI."""

import argparse
import asyncio
import os
import sys
from pathlib import Path

from construction_rfi_agent.agent import draft_rfi
from construction_rfi_agent.schema import RFIDraft


def _render_markdown(r: RFIDraft) -> str:
    lines: list[str] = [
        f"# RFI #{r.rfi_number} — {r.subject}",
        "",
        f"**Needs architect-of-record response:** {r.needs_architect_response}",
        f"**Schedule impact:** {r.schedule_impact_days} day(s)",
        f"**Cost impact:** {r.cost_impact}",
        f"**Confidence:** {r.confidence}",
        "",
        "## Question (restated)",
        r.question_restatement,
        "",
        "## Draft response",
        r.draft_response,
        "",
        "## Spec references",
    ]
    for s in r.spec_references:
        c = s.citation
        snippet = (c.snippet or "").replace("\n", " ").strip()[:240]
        lines.append(
            f"- **CSI {s.csi_division}** — {s.section_title} "
            f"(*{c.document_name}*, chunk:{c.chunk_id}): \u201c{snippet}\u201d"
        )

    if r.drawing_references:
        lines.append("")
        lines.append("## Drawing references")
        for d in r.drawing_references:
            lines.append(f"- {d}")

    lines.append("")
    lines.append("## Evidence")
    for c in r.citations:
        snippet = (c.snippet or "").replace("\n", " ").strip()[:240]
        lines.append(f"- *{c.document_name}* (chunk:{c.chunk_id}): \u201c{snippet}\u201d")
    return "\n".join(lines)


def main() -> None:
    p = argparse.ArgumentParser(
        description="Draft a construction RFI response from KS-seeded specs."
    )
    p.add_argument("--rfi-number", required=True)
    p.add_argument("--question", required=True, help="The RFI question body.")
    p.add_argument(
        "--corpus-folder",
        default=os.environ.get(
            "CONSTRUCTION_CORPUS_FOLDER_ID",
            "ab926019-ac7a-579f-bfda-6c52a13c5f41",
        ),
        help="Folder.id of the construction project corpus in your KS tenant.",
    )
    p.add_argument("--model", default=os.environ.get("MODEL", "gpt-4o"))
    p.add_argument("--out", type=Path, default=Path("rfi-response.md"))
    args = p.parse_args()

    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY in .env.")

    draft = asyncio.run(
        draft_rfi(
            rfi_number=args.rfi_number,
            question=args.question,
            corpus_folder_id=args.corpus_folder,
            model=args.model,
        )
    )
    args.out.write_text(_render_markdown(draft))
    print(
        f"Wrote {args.out} — rfi={draft.rfi_number} "
        f"needs_aor={draft.needs_architect_response} citations={len(draft.citations)}"
    )


if __name__ == "__main__":
    main()
