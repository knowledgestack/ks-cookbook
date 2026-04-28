"""KYC onboarding review CLI."""

import argparse
import asyncio
import os
import sys
from pathlib import Path

from kyc_onboarding_review.agent import review_kyc
from kyc_onboarding_review.schema import KYCReview


def _render_markdown(review: KYCReview) -> str:
    lines: list[str] = [
        f"# KYC Onboarding Review — {review.customer_name}",
        "",
        f"**Entity type:** {review.entity_type}",
        f"**Risk tier:** {review.risk_tier.value}",
        f"**EDD required:** {'Yes' if review.edd_required else 'No'}",
        f"**Recommendation:** {review.recommendation}",
        "",
        "## Risk Tier Rationale",
        review.risk_tier_rationale,
        "",
        "## CDD Checklist",
        "",
    ]

    for i, item in enumerate(review.checklist, 1):
        icon = {
            "PRESENT": "PASS",
            "MISSING": "FAIL",
            "INCOMPLETE": "WARN",
        }.get(item.status.value, "?")
        lines.append(f"### {i}. [{icon}] {item.requirement}")
        lines.append(f"**Status:** {item.status.value}")
        lines.append(f"**Evidence:** {item.evidence_note}")
        lines.append("")
        lines.append("**Policy basis:**")
        for c in item.citations:
            q = (c.quote or "").replace("\n", " ").strip()[:300]
            lines.append(f"- *{c.document_name}* (chunk:{c.chunk_id}): \u201c{q}\u201d")
        lines.append("")

    lines.append("## Risk Factors")
    for rf in review.risk_factors:
        lines.append(f"- **{rf.factor}**: {rf.impact}")
        for c in rf.citations:
            lines.append(f"  - *{c.document_name}* (chunk:{c.chunk_id})")
    lines.append("")

    if review.pending_items:
        lines.append("## Pending Items (must resolve before account opening)")
        for item in review.pending_items:
            lines.append(f"- {item}")
        lines.append("")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Review a KYC onboarding application against bank CDD policy with citations.",
    )
    parser.add_argument(
        "--corpus-folder",
        default=os.environ.get("KYC_CORPUS_FOLDER_ID", ""),
        help="Folder.id of the KYC corpus in your KS tenant.",
    )
    parser.add_argument(
        "--model",
        default=os.environ.get("MODEL", "gpt-4o"),
        help="OpenAI model (default: gpt-4o).",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("kyc-review.md"),
        help="Output markdown file (default: kyc-review.md).",
    )
    args = parser.parse_args()

    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY in .env.")
    review = asyncio.run(
        review_kyc(
            corpus_folder_id=args.corpus_folder or None,
            model=args.model,
        )
    )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(_render_markdown(review), encoding="utf-8")
    total_cites = sum(len(item.citations) for item in review.checklist) + sum(
        len(rf.citations) for rf in review.risk_factors
    )
    print(
        f"Wrote {args.out} — {review.customer_name}, "
        f"risk_tier={review.risk_tier.value}, "
        f"{len(review.checklist)} checklist items, "
        f"{total_cites} citations, "
        f"recommendation={review.recommendation}"
    )


if __name__ == "__main__":
    main()
