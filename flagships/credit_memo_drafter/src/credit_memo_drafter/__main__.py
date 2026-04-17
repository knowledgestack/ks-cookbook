"""Credit memo drafter CLI."""


import argparse
import asyncio
import os
import sys
from pathlib import Path

from credit_memo_drafter.agent import draft_memo
from credit_memo_drafter.schema import CreditMemo


def _render_markdown(memo: CreditMemo, loan_amount: int) -> str:
    lines: list[str] = [
        f"# Credit Memo — {memo.borrower}",
        "",
        f"**Facility requested:** ${loan_amount:,}",
        f"**Recommendation:** {memo.recommendation}",
        f"**Risk rating:** {memo.risk_rating} (1-9 scale)",
        "",
        "## Facility summary",
        memo.facility_summary,
        "",
        "## Key financials",
        memo.key_financials,
        "",
        "## Risk factors",
    ]
    for rf in memo.risks:
        lines.append(f"### {rf.title}  —  severity: {rf.severity}")
        lines.append(rf.narrative)
        lines.append("")
        lines.append("**Evidence:**")
        for c in rf.citations:
            snippet = (c.snippet or "").replace("\n", " ").strip()[:250]
            lines.append(f"- *{c.document_name}* (chunk:{c.chunk_id}): \u201c{snippet}\u201d")
        lines.append("")

    lines.append("## Recommended covenants")
    for cov in memo.covenants:
        lines.append(f"- **{cov.covenant}** — {cov.rationale}")
        for c in cov.citations:
            lines.append(f"  - source: *{c.document_name}* (chunk:{c.chunk_id})")
    lines.append("")

    if memo.policy_exceptions:
        lines.append("## Policy exceptions")
        for e in memo.policy_exceptions:
            lines.append(f"- {e}")

    return "\n".join(lines)


def main() -> None:
    p = argparse.ArgumentParser(description="Draft a credit memo from KS-seeded lending docs.")
    p.add_argument("--borrower", required=True)
    p.add_argument("--loan-amount", type=int, required=True)
    p.add_argument(
        "--corpus-folder",
        default=os.environ.get(
            "CORPUS_FOLDER_ID", "18001b47-295b-503f-a7ff-321100853a42",
        ),
        help="Folder.id (not path_part_id) of the lending corpus in your KS tenant.",
    )
    p.add_argument("--model", default=os.environ.get("MODEL", "gpt-4o"))
    p.add_argument("--out", type=Path, default=Path("credit-memo.md"))
    args = p.parse_args()

    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY in .env.")

    memo = asyncio.run(draft_memo(
        borrower=args.borrower, loan_amount=args.loan_amount,
        corpus_folder_id=args.corpus_folder, model=args.model,
    ))
    args.out.write_text(_render_markdown(memo, args.loan_amount))
    n_citations = sum(len(r.citations) for r in memo.risks) + sum(len(c.citations) for c in memo.covenants)
    print(f"Wrote {args.out} — recommendation={memo.recommendation} risk_rating={memo.risk_rating} citations={n_citations}")


if __name__ == "__main__":
    main()
