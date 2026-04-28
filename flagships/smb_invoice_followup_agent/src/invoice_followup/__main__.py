"""SMB invoice follow-up CLI."""

import argparse
import asyncio
import os
import sys
from pathlib import Path

from invoice_followup.agent import draft_followup
from invoice_followup.schema import FollowUpDraft


def _render_markdown(draft: FollowUpDraft) -> str:
    lines: list[str] = [
        f"# Follow-up draft — {draft.client} / {draft.invoice_number}",
        "",
        f"**Days overdue:** {draft.days_overdue}",
        f"**Suggested send hour (local):** {draft.suggested_send_hour_local}:00",
        "",
        "## Tone observations (grounded)",
    ]
    for t in draft.tone_analysis:
        lines.append(f"- {t.observation}")
        c = t.citation
        snippet = (c.snippet or "").replace("\n", " ").strip()[:200]
        lines.append(f"  - *{c.document_name}* (chunk:{c.chunk_id}): \u201c{snippet}\u201d")
    lines += [
        "",
        "## Draft",
        f"**Subject:** {draft.subject}",
        "",
        draft.body,
    ]
    if draft.evidence:
        lines += ["", "## Supporting evidence"]
        for c in draft.evidence:
            lines.append(f"- *{c.document_name}* (chunk:{c.chunk_id})")
    return "\n".join(lines)


def main() -> None:
    p = argparse.ArgumentParser(description="Draft a tone-matched invoice follow-up.")
    p.add_argument("--client", required=True)
    p.add_argument("--invoice-number", required=True)
    p.add_argument("--days-overdue", type=int, default=14)
    p.add_argument(
        "--corpus-folder",
        default=os.environ.get(
            "INVOICE_CORPUS_FOLDER_ID",
            "ab926019-ac7a-579f-bfda-6c52a13c5f41",
        ),
    )
    p.add_argument("--model", default=os.environ.get("MODEL", "gpt-4o"))
    p.add_argument("--out", type=Path, default=Path("invoice-followup.md"))
    args = p.parse_args()

    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY in .env.")

    draft = asyncio.run(
        draft_followup(
            client=args.client,
            invoice_number=args.invoice_number,
            days_overdue=args.days_overdue,
            corpus_folder_id=args.corpus_folder,
            model=args.model,
        )
    )
    args.out.write_text(_render_markdown(draft))
    print(
        f"Wrote {args.out} — client={draft.client} invoice={draft.invoice_number} "
        f"tone_samples={len(draft.tone_analysis)}"
    )


if __name__ == "__main__":
    main()
