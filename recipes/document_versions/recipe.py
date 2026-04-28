"""Document versions probe — list + diff version metadata for a corpus document.

Pain point: Policies change quarterly. Auditors ask "what changed in v3 of the
access-control policy, and which chunk says so?". Reviewers need a deterministic
way to see version metadata and newest-version chunks without trusting an LLM.

Framework: MCP-only (no LLM). Deterministic.
Tools used: find, get_info, list_contents, read.
Output: file (document-versions.md).

NOTE ON VERSIONING SURFACE. The KS MCP server v1 is read-only. Version *metadata*
is exposed via ``get_info`` / ``list_contents`` (whatever fields the server
returns — this recipe prints them verbatim so you can see the shape). Mutating
version tools (create_version, promote, rollback) are on the roadmap in the
write-back MCP. This recipe is the honest v1 check: it probes what's there and
surfaces citations from the current version's chunks.
"""

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _shared.mcp_client import call, call_list, ks_mcp_session  # noqa: E402

CORPUS_FOLDER = os.environ.get("POLICIES_FOLDER_ID", "")
def _dump(obj) -> str:
    return json.dumps(obj, indent=2, default=str)


async def run(query: str, out_path: Path) -> None:
    async with ks_mcp_session() as session:
        hits = await call_list(session, "find", {"query": query, "limit": 5})
        if not hits:
            sys.exit(f"No documents found matching '{query}'.")
        first = hits[0] if not isinstance(hits[0], list) else hits[0][0]
        path_part_id = (
            (first.get("path_part_id") or first.get("id") or first.get("pathPartId"))
            if isinstance(first, dict)
            else None
        )
        if not path_part_id:
            sys.exit(f"Could not locate path_part_id in find result: {first!r}")

        info = await call_list(session, "get_info", {"path_part_id": path_part_id})
        body = await call(session, "read", {"path_part_id": path_part_id})

        lines: list[str] = [
            f"# Version probe — query `{query}`",
            "",
            f"Resolved path_part_id: `{path_part_id}`",
            "",
            "## get_info payload",
            "",
            "```json",
            _dump(info),
            "```",
            "",
            "## Chunks in current version",
            "",
            "These `[chunk:<uuid>]` tags come from `read` output — cite them verbatim.",
            "",
            "```",
            body[:4000] + ("\n…(truncated)" if len(body) > 4000 else ""),
            "```",
            "",
            "## Mutating version tools",
            "",
            "The v1 MCP surface is read-only. `create_version`, `promote_version`,",
            "and `rollback_version` are tracked in the write-back MCP roadmap.",
        ]
        out_path.write_text("\n".join(lines))
        print(f"Wrote {out_path}")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--query",
        default="access control policy",
        help="Natural-language query to resolve a document via `find`.",
    )
    p.add_argument("--out", type=Path, default=Path("document-versions.md"))
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY"):
        sys.exit("Set KS_API_KEY.")
    asyncio.run(run(args.query, args.out))


if __name__ == "__main__":
    main()
