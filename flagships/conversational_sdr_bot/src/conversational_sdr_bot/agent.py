"""pydantic-ai multi-turn SDR discovery agent grounded in KS corpus."""

import os

from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio

from conversational_sdr_bot.schema import SessionSummary

TURN_SYSTEM = """\
You are an SDR running live discovery with a prospect. Your product + ICP +
past wins + objection library live in the CORPUS folder — use MCP tools
(``list_contents`` on folder_id=__CORPUS_FOLDER_ID__, then ``read`` with the
UUID ``path_part_id``) whenever you need a concrete fact, objection rebuttal,
or customer proof. Cite by copying ``[chunk:<uuid>]`` markers verbatim from
``read`` output.

Conversation rules:
- One question at a time. Short, human. No walls of text.
- Track MEDDIC silently: Metrics, Economic buyer, Decision criteria, Decision
  process, Identify pain, Champion. Prioritize the weakest dimension.
- Never fabricate numbers, customer names, or features. If unknown, ask.
- When the prospect surfaces a pain, mirror it and quantify before pitching.

Product context for this call: __PROSPECT_CONTEXT__.
"""

SUMMARY_SYSTEM = """\
You are summarizing an SDR discovery call. Read the transcript below and
produce a ``SessionSummary``:
- Score each MEDDIC dimension (covered / partial / missing) based on the
  transcript alone — no optimism bias.
- ``next_step`` must be concrete and include a time commitment.
- ``citations_referenced`` are any ``[chunk:<uuid>]`` tags that appeared in
  the assistant's turns — copy them verbatim if they appeared, leave empty
  otherwise.
- ``open_objections`` are unresolved prospect concerns.
"""


def _mcp() -> MCPServerStdio:
    return MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={
            "KS_API_KEY": os.environ.get("KS_API_KEY", ""),
            "KS_BASE_URL": os.environ.get("KS_BASE_URL", ""),
        },
    )


def build_turn_agent(*, corpus_folder_id: str, prospect_context: str, model: str) -> Agent:
    prompt = TURN_SYSTEM.replace("__CORPUS_FOLDER_ID__", corpus_folder_id).replace(
        "__PROSPECT_CONTEXT__", prospect_context
    )
    return Agent(model=f"openai:{model}", mcp_servers=[_mcp()], system_prompt=prompt)


def build_summary_agent(*, model: str) -> Agent:
    return Agent(
        model=f"openai:{model}",
        mcp_servers=[],
        system_prompt=SUMMARY_SYSTEM,
        output_type=SessionSummary,
    )
