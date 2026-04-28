"""Password / auth config audit — compare a config snapshot to policy.

Pain point: Security wants to confirm that a system's password / MFA / session
config actually matches the written policy. Today this means a human reads the
policy, reads the config, and writes a memo. This recipe does it deterministically.

Framework: MCP-only (no LLM). Pulls the password/auth policy and prints a
side-by-side audit table with citations.
Tools used: search_keyword, read.
Output: file (auth-audit.md).
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
DEFAULT_CONFIG = {
    "min_password_length": 10,
    "require_mfa": False,
    "session_timeout_minutes": 480,
    "password_rotation_days": 365,
    "lockout_after_failed_attempts": 10,
}


async def run(config: dict, out_path: Path) -> None:
    lines: list[str] = [
        "# Password / Auth Config Audit\n",
        "## Observed configuration\n",
        "```json",
        json.dumps(config, indent=2),
        "```\n",
        "## Relevant policy excerpts\n",
    ]
    async with ks_mcp_session() as session:
        seen: set[str] = set()
        for kw in ("password", "mfa", "session", "lockout", "authentication"):
            hits = await call_list(
                session,
                "search_keyword",
                {"query": kw, "folder_id": POLICIES_FOLDER, "limit": 2},
            )
            for hit in hits:
                if not isinstance(hit, dict):
                    continue
                ppid = hit.get("path_part_id") or hit.get("chunk_id")
                if not ppid or ppid in seen:
                    continue
                seen.add(ppid)
                doc = hit.get("document_name") or hit.get("name") or "(document)"
                excerpt = await call(
                    session,
                    "read",
                    {"path_part_id": ppid, "max_chars": 800},
                )
                lines.append(f"### {doc} — keyword `{kw}`\n\n{excerpt}\n")
    lines.append("\n## Reviewer task\n")
    lines.append(
        "Compare each config field above against the cited excerpts. Flag any "
        "field where the observed value is weaker than the policy minimum.\n"
    )
    out_path.write_text("\n".join(lines))
    print(json.dumps({"status": "ok", "wrote": f"{out_path} ({len(seen)} excerpts)"}, indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--config-file", help="JSON file with observed auth config. Default: built-in sample."
    )
    p.add_argument("--out", default="auth-audit.md")
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY"):
        sys.exit("Set KS_API_KEY.")
    config = json.loads(Path(args.config_file).read_text()) if args.config_file else DEFAULT_CONFIG
    asyncio.run(run(config, Path(args.out)))


if __name__ == "__main__":
    main()
