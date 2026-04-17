"""Render a ``RevRecMemo`` to markdown."""


from pathlib import Path

from rev_rec_memo.schema import RevRecMemo


def write_memo(memo: RevRecMemo, out_path: Path) -> None:
    lines: list[str] = [
        f"# ASC 606 Revenue Recognition Memo — {memo.customer}",
        "",
        f"**Product:** {memo.product}  ",
        f"**Total contract value:** ${memo.total_contract_value_usd:,.2f}",
        "",
        "## Conclusion",
        "",
        memo.conclusion.strip(),
        "",
    ]
    for step in sorted(memo.steps, key=lambda s: s.number):
        lines.append(f"## Step {step.number} — {step.title}")
        lines.append("")
        lines.append(step.analysis.strip())
        lines.append("")
    lines.append("## Citations")
    lines.append("")
    if not memo.citations:
        lines.append("_No citations._")
    for c in memo.citations:
        snippet = (c.snippet or "").replace("\n", " ").strip()
        lines.append(
            f"- `[chunk:{c.chunk_id}]` — **{c.document_name}** — "
            f"\u201c{snippet}\u201d"
        )
    lines.append("")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines))
