# Knowledge Stack with CrewAI

CrewAI fits when you want **multiple role-played agents** sharing the same KS retrieval surface — e.g. a researcher gathering source material, a drafter producing the memo, a reviewer checking citations.

## Install

```bash
uv add crewai crewai-tools
```

## Pattern: KS as a shared tool across the crew

Spawn `knowledgestack-mcp` once via `MCPServerAdapter` and hand its `tools` to every crew member. Each agent inherits the same KS permission scope from `KS_API_KEY` — use **distinct keys per agent** if you want the researcher to see broadly and the drafter to see only approved templates.

## Worked example — credit memo (CrewAI port)

```python
import os
from crewai import Agent, Crew, Process, Task
from crewai_tools import MCPServerAdapter

ks = MCPServerAdapter({
    "command": "uvx",
    "args": ["knowledgestack-mcp"],
    "env": {
        "KS_API_KEY": os.environ["KS_API_KEY"],
        "KS_BASE_URL": os.environ.get("KS_BASE_URL", ""),
    },
})

researcher = Agent(
    role="Credit policy researcher",
    goal="Surface every relevant credit-policy and borrower passage with [chunk:<uuid>] markers preserved.",
    backstory="A senior risk analyst who never trusts a number that isn't cited.",
    tools=ks.tools,  # search_knowledge, read, list_contents, ...
    allow_delegation=False,
    verbose=True,
)

drafter = Agent(
    role="Credit memo drafter",
    goal="Produce a CreditMemo JSON with a risk_rating 1-9 and chunk_id citations copied verbatim.",
    backstory="A commercial credit underwriter at Riverway Bank.",
    tools=ks.tools,
    allow_delegation=False,
    verbose=True,
)

reviewer = Agent(
    role="Citation reviewer",
    goal="Reject any citation whose chunk_id was not produced by a read() call.",
    backstory="A compliance officer who treats fabricated citations as a fireable offense.",
    tools=ks.tools,
    allow_delegation=False,
    verbose=True,
)

research_task = Task(
    description=(
        "Borrower: {borrower}. Loan: ${loan_amount}. "
        "Use search_knowledge then read() to assemble a corpus of policy + financial passages. "
        "Output: a markdown bundle of passages, each tagged with its [chunk:<uuid>] marker."
    ),
    expected_output="Markdown corpus of cited passages.",
    agent=researcher,
)

draft_task = Task(
    description="Using only the bundle from research, draft a CreditMemo JSON matching the schema.",
    expected_output="Valid JSON that parses to CreditMemo.",
    agent=drafter,
    context=[research_task],
)

review_task = Task(
    description="Verify every Citation.chunk_id appeared in the research bundle. Reject otherwise.",
    expected_output="Final approved CreditMemo JSON.",
    agent=reviewer,
    context=[research_task, draft_task],
)

crew = Crew(
    agents=[researcher, drafter, reviewer],
    tasks=[research_task, draft_task, review_task],
    process=Process.sequential,
    verbose=True,
)

result = crew.kickoff(inputs={"borrower": "ACME Corp", "loan_amount": "5,000,000"})
print(result)
```

## Why a 3-agent crew over 1 agent

- **Researcher** can iterate on `search_knowledge` queries without polluting the drafting context.
- **Drafter** sees a curated bundle, not the raw 200-tool-call trace — JSON output gets cleaner.
- **Reviewer** is the citation gate. CI doesn't trust LLM citations; neither should you.

You can collapse this to a single agent for cheap demos, but the multi-agent shape is what makes CrewAI worth the overhead.

## Per-role permission scoping

```python
researcher = Agent(..., tools=MCPServerAdapter({..., "env": {"KS_API_KEY": RESEARCHER_KEY}}).tools)
drafter    = Agent(..., tools=MCPServerAdapter({..., "env": {"KS_API_KEY": DRAFTER_KEY}}).tools)
```

Different keys → different folders visible. The drafter literally cannot read documents the researcher had access to. This is how you implement need-to-know across a crew.

## Gotchas

- **`MCPServerAdapter` spawns a subprocess.** Reuse `ks.tools` across the crew rather than creating one per agent unless you actually need separate permission scopes.
- **CrewAI's default `verbose=True` is loud.** Set to `False` in production.
- **`expected_output` strings matter.** CrewAI uses them to coerce the result; if your final task says "JSON", make sure the agent emits raw JSON, not Markdown-fenced JSON.
- **Citations field is your friend.** Have the reviewer agent literally reject any `chunk_id` not in the research bundle — that's the only reliable hallucination guard in a multi-agent setup.
