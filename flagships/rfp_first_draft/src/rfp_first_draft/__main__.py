"""CLI entry for the RFP first-draft flagship."""


import argparse
import asyncio
import os
import sys
from pathlib import Path

from rfp_first_draft.agent import draft_rfp
from rfp_first_draft.schema import RFPDraft


def _render_markdown(draft: RFPDraft) -> str:
    lines = [
        f"# RFP Draft — {draft.rfp_title}",
        "",
    ]
    for i, r in enumerate(draft.responses, 1):
        lines += [
            f"## {i}. {r.question}",
            f"*Confidence: {r.confidence.value}*",
            "",
            r.answer,
            "",
            "**Sources:**",
        ]
        for c in r.citations:
            q = (c.quote or "").replace("\n", " ").strip()[:300]
            lines.append(
                f"- {c.source_document} [chunk:{c.chunk_id}]: \u201c{q}\u201d"
            )
        lines.append("")

    if draft.overall_notes:
        lines += ["## Notes & Gaps", draft.overall_notes]
    return "\n".join(lines)


def main() -> None:
    p = argparse.ArgumentParser(
        description="Draft RFP responses grounded in past proposals."
    )
    p.add_argument(
        "--question", required=True,
        help="The RFP question(s) to answer (free text).",
    )
    p.add_argument(
        "--corpus-folder",
        default=os.environ.get("CORPUS_FOLDER_ID",
                               "baf79cab-7ab9-5949-bfda-93cb87b662c0"),
    )
    p.add_argument("--model", default=os.environ.get("MODEL", "gpt-4o"))
    p.add_argument("--out", type=Path, default=Path("rfp-draft.md"))
    args = p.parse_args()

    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY in .env.")

    draft = asyncio.run(draft_rfp(
        question=args.question,
        corpus_folder_id=args.corpus_folder,
        model=args.model,
    ))
    args.out.write_text(_render_markdown(draft))
    total_cites = sum(len(r.citations) for r in draft.responses)
    print(
        f"Wrote {args.out} — {len(draft.responses)} responses, "
        f"{total_cites} citations."
    )


if __name__ == "__main__":
    main()
