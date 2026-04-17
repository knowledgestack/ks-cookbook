"""pydantic-ai agent that checks patient eligibility against a clinical trial."""


import os

from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio

from clinical_trial_eligibility.schema import EligibilityAssessment

SYSTEM = """\
You are a clinical research coordinator screening a patient for trial
eligibility. You have access to the PROGRESS trial protocol (NCT03855137,
atogepant for chronic migraine), AHS clinical guidance on CGRP inhibitors,
and CMS NCD coverage criteria.

MANDATORY workflow:
1. __DISCOVERY_STEP__
2. ``read(path_part_id=<UUID>, max_chars=6000)`` — read each document.
   Each passage ends with an inline ``[chunk:<uuid>]`` marker.
3. Produce an ``EligibilityAssessment`` with every inclusion and exclusion
   criterion evaluated against the patient profile.

IMPORTANT: Prefer ``find``/``list_contents`` plus ``read``. Do not rely on
guessed folder ids or document names as UUIDs.

For each criterion:
- Copy the criterion text from the trial protocol
- Determine ELIGIBLE, INELIGIBLE, or UNCERTAIN based on the patient info
- Provide clinical rationale
- Include >=1 citation with the ``chunk_id`` copied VERBATIM from a
  ``[chunk:...]`` marker in the read output

If information about the patient is missing for a criterion, mark it UNCERTAIN
and recommend what additional data is needed.

Set overall_eligibility to INELIGIBLE if any exclusion is triggered or any
mandatory inclusion criterion is unmet. UNCERTAIN if there are gaps. ELIGIBLE
only if all criteria are definitively met.

Use the UUID path_part_id values from list_contents — NOT document names.
"""


async def assess_eligibility(
    *,
    patient_profile: str,
    corpus_folder_id: str | None,
    model: str,
) -> EligibilityAssessment:
    server_cmd = os.environ.get("KS_MCP_COMMAND", "uvx")
    server_args = (
        os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or ""
    ).split()
    mcp = MCPServerStdio(
        command=server_cmd,
        args=server_args,
        env={
            "KS_API_KEY": os.environ.get("KS_API_KEY", ""),
            "KS_BASE_URL": os.environ.get("KS_BASE_URL", ""),
        },
    )
    if corpus_folder_id:
        discovery_step = (
            f'Call ``list_contents(folder_id="{corpus_folder_id}")`` to '
            "enumerate the corpus."
        )
    else:
        discovery_step = (
            "Do NOT call ``list_contents``. Use ``find`` to locate the trial "
            "protocol and supporting guidance by title keywords such as "
            "``PROGRESS``, ``migraine``, ``atogepant``, ``AHS``, and ``CMS``."
        )
    agent = Agent(
        model=f"openai:{model}",
        mcp_servers=[mcp],
        system_prompt=SYSTEM.replace(
            "__DISCOVERY_STEP__", discovery_step
        ),
        output_type=EligibilityAssessment,
    )
    assessment: EligibilityAssessment | None = None
    try:
        async with agent.run_mcp_servers():
            result = await agent.run(
                f"Evaluate this patient for trial eligibility:\n\n"
                f"{patient_profile}"
            )
            assessment = (
                getattr(result, "output", None)
                or getattr(result, "data", None)
                or result  # type: ignore[assignment]
            )
    except BaseExceptionGroup:
        # pydantic-ai's MCPServerStdio raises BrokenResourceError during
        # cleanup after the result is already produced. Safe to swallow.
        pass
    if assessment is None:
        raise RuntimeError(
            "Agent did not produce a result before the MCP session closed."
        )
    return assessment
