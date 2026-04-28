# pyright: reportMissingImports=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportUnknownParameterType=false, reportAny=false, reportAttributeAccessIssue=false, reportUnusedCallResult=false, reportCallIssue=false, reportGeneralTypeIssues=false, reportArgumentType=false, reportOptionalSubscript=false, reportReturnType=false, reportMissingTypeArgument=false, reportDeprecated=false, reportUnannotatedClassAttribute=false
"""DPA gap check — flag missing/weak GDPR clauses vs your data-protection policy.

Pain point: Counterparty Data Processing Addenda often omit standard GDPR
Article 28 obligations. Privacy/legal redoes the same gap analysis each time.
This recipe: DPA text in → list of missing or weak clauses out, each cited
to the company's data-protection policy.

Framework: raw OpenAI chat completions + MCP stdio.
Tools used: list_contents, read.
Output: stdout (markdown).
"""

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

from openai import AsyncOpenAI

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _shared.mcp_client import call, ks_mcp_session  # noqa: E402

POLICIES_FOLDER = os.environ.get("POLICIES_FOLDER_ID", "")
SYSTEM = (
    "You are a privacy counsel assistant. Compare the counterparty's DPA text "
    "against the company's data-protection policy. Output markdown with one "
    "row per missing or weak clause: '- **<topic>** — <gap>. Source: "
    "[chunk:<uuid>]' where chunk_id is copied verbatim from the policy text. "
    "Do not invent chunk_ids. If the DPA is fully compliant, say so explicitly."
)

SAMPLE_DPA = (
    "Processor will process Personal Data only to provide the Services.\n"
    "Processor may engage sub-processors at its discretion.\n"
    "Processor will notify Controller of breaches within 30 days.\n"
)


async def pick_policy(session, hint: str) -> dict:
    """Search the whole tenant for a relevant DPA / data-processing policy."""
    raw = await call(session, "search_knowledge", {"query": f"data processing addendum {hint}", "limit": 6})
    try:
        hits = json.loads(raw) if isinstance(raw, str) else raw
    except json.JSONDecodeError:
        hits = []
    items = hits if isinstance(hits, list) else (hits.get("hits") or hits.get("results") or [])
    docs = []
    for h in items:
        ppid = h.get("path_part_id") or h.get("chunk_id")
        if not ppid:
            continue
        name = (h.get("document_name") or "").split("/")[-1] or f"chunk-{str(ppid)[:8]}"
        docs.append({"name": name, "path_part_id": ppid, "part_type": "DOCUMENT"})
    if not docs:
        sys.exit("No policies found in the tenant.")
    match = next((d for d in docs if hint in d.get("name", "").lower()), None)
    return match or docs[0]


async def run(dpa_text: str) -> None:
    client = AsyncOpenAI()
    async with ks_mcp_session() as session:
        policy = await pick_policy(session, "data")
        policy_text = await call(
            session,
            "read",
            {"path_part_id": policy["path_part_id"], "max_chars": 6000},
        )
        resp = await client.chat.completions.create(
            model=os.environ.get("MODEL", "gpt-4o"),
            messages=[
                {"role": "system", "content": SYSTEM},
                {
                    "role": "user",
                    "content": (
                        f"Company policy '{policy['name']}':\n{policy_text}\n\n"
                        f"Counterparty DPA:\n{dpa_text}"
                    ),
                },
            ],
        )
        print(json.dumps({"gap_analysis_markdown": resp.choices[0].message.content}, indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--dpa-file", help="Path to counterparty DPA text. Default: built-in sample.")
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    text = Path(args.dpa_file).read_text() if args.dpa_file else SAMPLE_DPA
    asyncio.run(run(text))


if __name__ == "__main__":
    main()
