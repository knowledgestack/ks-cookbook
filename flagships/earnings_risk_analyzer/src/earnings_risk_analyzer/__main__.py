"""10-K risk-flag analyst memo CLI."""

import argparse
import asyncio
import os
import sys
from pathlib import Path

from earnings_risk_analyzer.agent import analyze_10k
from earnings_risk_analyzer.schema import EarningsRiskMemo


def _render_markdown(memo: EarningsRiskMemo) -> str:
    lines = [
        f"# Risk-Flag Memo — {memo.company} ({memo.ticker})",
        f"**Filing:** {memo.filing_period}",
        f"**Overall posture:** {memo.overall_risk_posture}",
        "",
    ]

    for i, f in enumerate(memo.flags, 1):
        lines += [
            f"## {i}. [{f.severity.value}] {f.title}",
            f"*Category: {f.category.value}*",
            "",
            f.analysis,
            "",
            f"**Mitigation:** {f.mitigation}",
            "",
            "**Evidence:**",
        ]
        for c in f.citations:
            q = (c.quote or "").replace("\n", " ").strip()[:300]
            lines.append(f"- *{c.section}* (chunk:{c.chunk_id}): \u201c{q}\u201d")
        lines.append("")

    if memo.new_risks_vs_prior_year:
        lines += ["## New / materially changed risks"]
        lines += [f"- {r}" for r in memo.new_risks_vs_prior_year]
        lines.append("")

    lines += ["## Investment implications", memo.investment_implications]
    return "\n".join(lines)


def main() -> None:
    p = argparse.ArgumentParser(description="10-K risk-flag analyst memo from a real SEC filing.")
    p.add_argument(
        "--corpus-folder",
        default=os.environ.get("CORPUS_FOLDER_ID", "a5c81290-b181-54d4-a949-bbb2cb91739a"),
    )
    p.add_argument("--model", default=os.environ.get("MODEL", "gpt-4o"))
    p.add_argument("--out", type=Path, default=Path("risk-flag-memo.md"))
    args = p.parse_args()

    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY in .env.")

    memo = asyncio.run(
        analyze_10k(
            corpus_folder_id=args.corpus_folder,
            model=args.model,
        )
    )
    args.out.write_text(_render_markdown(memo))
    total_cites = sum(len(f.citations) for f in memo.flags)
    print(
        f"Wrote {args.out} — {memo.company} ({memo.ticker}), "
        f"{len(memo.flags)} flags, {total_cites} citations, "
        f"posture: {memo.overall_risk_posture[:80]}"
    )


if __name__ == "__main__":
    main()
