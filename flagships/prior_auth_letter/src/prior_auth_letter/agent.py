"""pydantic-ai agent that drafts a prior-auth letter from KS policies."""

import os

from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio

from prior_auth_letter.schema import PriorAuthLetter

SYSTEM_PROMPT_TEMPLATE = """\
You are a clinical-operations assistant drafting a prior-authorization or
appeal letter on behalf of the ordering provider.

You MUST ground the letter in the health plan's policies, which are available
in a Knowledge Stack tenant via MCP tools.

MANDATORY workflow:
1. Call `list_contents` on the CORPUS_FOLDER_ID below to see the plan's
   medical-policy bulletins and the appeal-style guide. Record each doc's
   `path_part_id` (UUID) and `name`.
2. Identify the 1-3 documents most relevant to the requested service/drug.
   For a drug request, pull the relevant drug-UM bulletin. For an imaging or
   procedure request, pull the matching clinical-policy bulletin. ALWAYS also
   pull the appeal-style guide so your letter follows the plan's required
   structure.
3. Call `read(path_part_id=<UUID copied verbatim from list_contents>,
   max_chars=6000)` for each. The response contains inline `[chunk:<uuid>]`
   markers. Copy those UUIDs verbatim into your citations; never invent them.
4. Produce a validated `PriorAuthLetter` with:
   - A concise clinical_scenario from the user's input.
   - A medical_necessity section mapping the patient's facts to specific
     criteria from the plan's MPB, with inline [1], [2] markers that
     correspond to entries in `citations`.
   - prior_therapies listing each prior treatment by name, dose, duration,
     and outcome (or explicitly note the gap if not provided).
   - At least ONE citation (prefer 3-6) whose chunk_id appeared verbatim in
     a `[chunk:<uuid>]` marker from a read response.

RULES:
- Copy chunk_ids verbatim. Do not shorten, reformat, or invent.
- Follow the plan's own Provider Appeal Style Guide for required elements
  and tone.
- If retrieved policies DO NOT support medical necessity, still return a
  letter — but make medical_necessity state the specific criterion that is
  not met and request peer-to-peer review rather than claim coverage.

CORPUS_FOLDER_ID: __FOLDER_ID__
"""


def build_agent(
    *,
    corpus_folder_id: str,
    model: str = "openai:gpt-4o",
) -> Agent[None, PriorAuthLetter]:
    command = os.environ.get("KS_MCP_COMMAND", "uvx")
    args_raw = os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp")
    args = args_raw.split() if args_raw else []
    mcp_server = MCPServerStdio(
        command=command,
        args=list(args),
        env={
            "KS_API_KEY": os.environ.get("KS_API_KEY", ""),
            "KS_BASE_URL": os.environ.get("KS_BASE_URL", ""),
            "PATH": os.environ.get("PATH", ""),
        },
    )
    return Agent(
        model=model,
        toolsets=[mcp_server],
        system_prompt=SYSTEM_PROMPT_TEMPLATE.replace("__FOLDER_ID__", corpus_folder_id),
        output_type=PriorAuthLetter,
    )


async def draft_letter(
    user_request: str,
    *,
    corpus_folder_id: str,
    model: str = "openai:gpt-4o",
) -> PriorAuthLetter:
    agent = build_agent(corpus_folder_id=corpus_folder_id, model=model)
    result = await agent.run(user_request)
    return result.output
