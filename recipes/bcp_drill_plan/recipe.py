"""Business continuity drill plan grounded in BCP/DR policies.

Pain point: Annual BCP/DR tabletops need a custom scenario, success criteria,
and references to your real recovery objectives — but they get copy-pasted
from last year and slowly drift from policy.

Framework: raw Anthropic Messages API + MCP stdio.
Tools used: list_contents, read.
Output: file (drill-plan.md).
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
    "You design business continuity / disaster recovery tabletop drills. Use "
    "the MCP tools to read the BCP, disaster-recovery, and incident-response "
    "policies from the policies folder. Produce a markdown drill plan with "
    "sections: Scenario, Participants, Inject Timeline (5-8 injects), Success "
    "Criteria (tied to RTO/RPO from policy), Policy References. Each Success "
    "Criterion must end with a [chunk:<uuid>] tag copied from the read output."
)


async def run(scenario: str, out_path: Path) -> None:
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
                f"Drill scenario: {scenario}\n"
                f"Policies folder path_part_id: {POLICIES_FOLDER}\n"
                "Produce the drill plan markdown."
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
        sys.exit("Reached MCP turn limit without final drill plan.")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--scenario",
                   default="Primary region outage: us-east-1 unavailable for 4 hours.",
                   help="One-line description of the BCP/DR scenario.")
    p.add_argument("--out", default="drill-plan.md")
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("Set KS_API_KEY and ANTHROPIC_API_KEY.")
    asyncio.run(run(args.scenario, Path(args.out)))


if __name__ == "__main__":
    main()
