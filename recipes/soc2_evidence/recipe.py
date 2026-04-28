# pyright: reportMissingImports=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportUnknownParameterType=false, reportAny=false, reportAttributeAccessIssue=false, reportUnusedCallResult=false, reportCallIssue=false, reportGeneralTypeIssues=false, reportArgumentType=false, reportOptionalSubscript=false, reportReturnType=false, reportMissingTypeArgument=false, reportDeprecated=false, reportUnannotatedClassAttribute=false
"""SOC 2 evidence puller — given a control ID, dump cited policy excerpts.

Pain point: Audit prep means hunting through policy PDFs for the paragraphs
that satisfy each Trust Services Criteria control (CC6.1, CC7.2, etc.).
This recipe: control ID → markdown evidence pack with [chunk:<uuid>] tags.

Framework: MCP-only (no LLM). Pure keyword search + read, deterministic.
Tools used: search_keyword, read.
Output: file (soc2-evidence.md).
"""

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _shared.mcp_client import call, call_list, ks_mcp_session  # noqa: E402

POLICIES_FOLDER = os.environ.get("POLICIES_FOLDER_ID", "")
# Map a few common SOC 2 controls to keyword sets that surface relevant policy text.
CONTROL_KEYWORDS: dict[str, list[str]] = {
    "CC6.1": ["access control", "least privilege", "authentication"],
    "CC6.2": ["user provisioning", "account management"],
    "CC6.3": ["password", "mfa", "multi-factor"],
    "CC7.2": ["incident response", "monitoring", "alert"],
    "CC8.1": ["change management", "deployment"],
    "A1.2": ["backup", "recovery", "business continuity"],
}


async def run(control: str, out_path: Path) -> None:
    keywords = CONTROL_KEYWORDS.get(control.upper())
    if not keywords:
        sys.exit(f"Unknown control '{control}'. Try one of: {list(CONTROL_KEYWORDS)}")

    lines: list[str] = [f"# SOC 2 Evidence — {control.upper()}\n"]
    seen_chunks: set[str] = set()
    async with ks_mcp_session() as session:
        for kw in keywords:
            lines.append(f"\n## Keyword: `{kw}`\n")
            hits = await call_list(
                session,
                "search_keyword",
                {"query": kw, "folder_id": POLICIES_FOLDER, "limit": 3},
            )
            if not hits:
                lines.append("_No hits._\n")
                continue
            for hit in hits:
                if not isinstance(hit, dict):
                    continue
                ppid = hit.get("path_part_id") or hit.get("chunk_id")
                doc_name = hit.get("document_name") or hit.get("name") or "(document)"
                if not ppid or ppid in seen_chunks:
                    continue
                seen_chunks.add(ppid)
                excerpt = (
                    await call(
                        session,
                        "read_around",
                        {"chunk_id": ppid, "before": 0, "after": 1},
                    )
                    if hit.get("chunk_id")
                    else await call(
                        session,
                        "read",
                        {"path_part_id": ppid, "max_chars": 1200},
                    )
                )
                lines.append(f"### {doc_name}\n\n{excerpt}\n")
    out_path.write_text("\n".join(lines))
    print(json.dumps({"status": "ok", "wrote": str(out_path), "excerpts": len(seen_chunks)}, indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--control", default="CC6.1", help=f"SOC 2 control ID. Known: {sorted(CONTROL_KEYWORDS)}"
    )
    p.add_argument("--out", default="soc2-evidence.md", help="Output markdown file.")
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY"):
        sys.exit("Set KS_API_KEY.")
    asyncio.run(run(args.control, Path(args.out)))


if __name__ == "__main__":
    main()
