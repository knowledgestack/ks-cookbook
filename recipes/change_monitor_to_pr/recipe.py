# pyright: reportMissingImports=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportUnknownParameterType=false, reportAny=false, reportAttributeAccessIssue=false, reportUnusedCallResult=false, reportCallIssue=false, reportGeneralTypeIssues=false, reportArgumentType=false, reportOptionalSubscript=false, reportReturnType=false, reportMissingTypeArgument=false, reportDeprecated=false, reportUnannotatedClassAttribute=false
"""Change monitor → PR body recipe.

Title: Watch a KS corpus for material changes and emit a PR-ready diff summary.
Tenant: any seeded tenant with a watched corpus.
Framework: raw MCP via _shared.mcp_client.
Pain point: engineers / compliance teams hand-roll scripts that watch
            regulatory filings, vendor API docs, or case law and file PRs
            when something changes (see HN 'What are you working on', 2026).

Keeps under 100 LOC. Stateless on the client side — uses KS chunk UUIDs as
the change-tracking key.
"""

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from _shared.mcp_client import call, ks_mcp_session  # noqa: E402


def _load_snapshot(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        return {}


def _save_snapshot(path: Path, snapshot: dict[str, str]) -> None:
    path.write_text(json.dumps(snapshot, indent=2, sort_keys=True))


async def run(folder_id: str, topic: str, snapshot_path: Path, out: Path) -> None:
    prior = _load_snapshot(snapshot_path)
    new_snapshot: dict[str, str] = {}
    changed: list[dict[str, str]] = []

    async with ks_mcp_session() as session:
        # No folder_id — search the whole tenant, KS finds the right doc.
        hits_json = await call(
            session,
            "search_knowledge",
            {
                "query": topic,
                "limit": 20,
            },
        )
        try:
            hits = json.loads(hits_json) if isinstance(hits_json, str) else hits_json
        except json.JSONDecodeError:
            hits = []
        if isinstance(hits, list):
            results = hits
        else:
            results = hits.get("results") or hits.get("hits") or []
        for hit in results:
            chunk_id = hit.get("chunk_id") or hit.get("id")
            document_name = hit.get("document_name") or hit.get("path", "")
            snippet = (hit.get("snippet") or hit.get("text") or "").strip()
            if not chunk_id:
                continue
            new_snapshot[chunk_id] = snippet[:200]
            if chunk_id not in prior:
                changed.append(
                    {
                        "type": "added",
                        "chunk_id": chunk_id,
                        "document": document_name,
                        "snippet": snippet[:300],
                    }
                )
            elif prior[chunk_id] != snippet[:200]:
                changed.append(
                    {
                        "type": "modified",
                        "chunk_id": chunk_id,
                        "document": document_name,
                        "snippet": snippet[:300],
                    }
                )

    for old_id in prior:
        if old_id not in new_snapshot:
            changed.append(
                {
                    "type": "removed",
                    "chunk_id": old_id,
                    "document": "",
                    "snippet": prior[old_id],
                }
            )

    _save_snapshot(snapshot_path, new_snapshot)

    lines = [f"# Change report — topic: {topic}", "", f"Changes detected: {len(changed)}", ""]
    for c in changed:
        lines += [
            f"## [{c['type'].upper()}] {c['document']}",
            f"- chunk: `[chunk:{c['chunk_id']}]`",
            f"- snippet: \u201c{c['snippet']}\u201d",
            "",
        ]
    out.write_text("\n".join(lines))
    summary = {
        "topic": topic,
        "tracked_chunks": len(new_snapshot),
        "changes": changed,
        "report_path": str(out),
    }
    print(json.dumps(summary, indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--folder-id",
        default=os.environ.get(
            "CORPUS_FOLDER_ID",
            "ab926019-ac7a-579f-bfda-6c52a13c5f41",
        ),
    )
    p.add_argument("--topic", required=True, help="Search query to watch, e.g. 'SOC 2 CC6.1'.")
    p.add_argument(
        "--snapshot", type=Path, default=Path("recipes/change_monitor_to_pr/.snapshot.json")
    )
    p.add_argument(
        "--out", type=Path, default=Path("recipes/change_monitor_to_pr/sample_output.md")
    )
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY"):
        sys.exit("KS_API_KEY is not set.")
    asyncio.run(run(args.folder_id, args.topic, args.snapshot, args.out))


if __name__ == "__main__":
    main()
