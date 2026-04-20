"""Architecture Decision Record drafter grounded in security/eng policies.

Pain point: Engineers write ADRs from a blank page; constraint references
(data-classification, encryption, vendor-mgmt) are forgotten until review.
This recipe: decision title + context → ADR markdown with policy-cited
constraints in the "Consequences" section.

Framework: raw Anthropic Messages API + MCP stdio.
Tools used: list_contents, read.
Output: file (adr.md).
"""

import argparse
import asyncio
import os
import sys
from pathlib import Path

from anthropic import AsyncAnthropic

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _shared.mcp_client import ks_mcp_session  # noqa: E402

POLICIES_FOLDER = os.environ.get(
    "POLICIES_FOLDER_ID", "ab926019-ac7a-579f-bfda-6c52a13c5f41"
)

SYSTEM = (
    "You draft Architecture Decision Records (ADRs). Use the MCP tools to read "
    "relevant policies (encryption, data classification, vendor management, "
    "access control) from the policies folder. Produce markdown with sections: "
    "Title, Status (Proposed), Context, Decision, Consequences, Policy Constraints. "
    "Every item under 'Policy Constraints' must end with a [chunk:<uuid>] tag "
    "copied verbatim from the read output."
)


async def run(decision: str, context: str, out_path: Path) -> None:
    client = AsyncAnthropic()
    async with ks_mcp_session() as session:
        tools_resp = await session.list_tools()
        anth_tools = [
            {"name": t.name, "description": t.description or "",
             "input_schema": t.inputSchema or {"type": "object", "properties": {}}}
            for t in tools_resp.tools
        ]
        messages: list[dict] = [{
            "role": "user",
            "content": (
                f"Decision: {decision}\nContext: {context}\n"
                f"Policies folder path_part_id: {POLICIES_FOLDER}\n"
                "Draft the ADR now."
            ),
        }]
        for _ in range(8):
            resp = await client.messages.create(
                model=os.environ.get("MODEL", "claude-opus-4-6"),
                system=SYSTEM, tools=anth_tools, max_tokens=2500,
                messages=messages,
            )
            if resp.stop_reason == "end_turn":
                text = "\n".join(
                    b.text for b in resp.content if getattr(b, "type", None) == "text"
                )
                out_path.write_text(text)
                print(f"Wrote {out_path}")
                return
            assistant_blocks: list[dict] = []
            tool_results: list[dict] = []
            for block in resp.content:
                assistant_blocks.append(block.model_dump(exclude_none=True))
                if getattr(block, "type", None) == "tool_use":
                    args = dict(block.input) if block.input else {}
                    result = await session.call_tool(block.name, args)
                    body = result.content[0].text if result.content else ""
                    tool_results.append({
                        "type": "tool_result", "tool_use_id": block.id,
                        "content": body[:6000], "is_error": result.isError,
                    })
            messages.append({"role": "assistant", "content": assistant_blocks})
            messages.append({"role": "user", "content": tool_results})
        sys.exit("Reached MCP turn limit without final ADR.")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--decision", default="Adopt managed Postgres for the analytics service",
                   help="The proposed decision in one sentence.")
    p.add_argument("--context", default="Current self-hosted Postgres has frequent on-call pages.",
                   help="Background paragraph on why the decision is being considered.")
    p.add_argument("--out", default="adr.md", help="Output markdown file path.")
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("Set KS_API_KEY and ANTHROPIC_API_KEY.")
    asyncio.run(run(args.decision, args.context, Path(args.out)))


if __name__ == "__main__":
    main()
