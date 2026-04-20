"""Version drift review — summarize changes across document versions and flag
regressions (controls weakened vs. a prior version) with chunk citations.

Pain point: A policy was tightened in v2, then quietly loosened in v3. Nobody
noticed until an audit. This recipe lists every version of a document, pulls
each version's chunks (with real chunk IDs), and asks an LLM to produce a cited
changelog plus a list of *regressions* — changes that weaken a control.

Framework: pydantic-ai + ksapi SDK (the MCP v1 `read` tool only returns the
current version, so historical versions are fetched via the SDK; citations are
still real chunk UUIDs from the backend).
Tools used: SDK list_document_versions, SDK get_document_version_contents.
Output: file (version-drift.md).

Companion: ``seed.py`` creates a demo Access Control Policy with three versions
whose drift is deliberately engineered (v2 tightens, v3 regresses).
"""

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path
from uuid import UUID

from ksapi import ApiClient, Configuration, DocumentVersionsApi
from pydantic import BaseModel, Field
from pydantic_ai import Agent


class Citation(BaseModel):
    chunk_id: str
    version_label: str
    snippet: str = Field(..., max_length=240)


class Regression(BaseModel):
    control: str = Field(..., max_length=120)
    from_version: str
    to_version: str
    prior_text: str = Field(..., max_length=300)
    new_text: str = Field(..., max_length=300)
    why_weakened: str = Field(..., max_length=300)
    citations: list[Citation] = Field(..., min_length=1, max_length=4)


class DriftReport(BaseModel):
    summary: str = Field(..., max_length=800)
    changes: list[str] = Field(default_factory=list, max_length=20)
    regressions: list[Regression] = Field(default_factory=list, max_length=10)


PROMPT = (
    "You review policy drift across document versions. Input is a JSON list of "
    "versions (oldest first), each with a version_label and chunks (id + text). "
    "Produce (a) a high-level summary, (b) a bullet changelog, and (c) a "
    "'regressions' list for any control that was WEAKENED vs an earlier version "
    "(e.g. 'required' → 'recommended', stricter threshold → looser, prohibition "
    "→ allowed with approval). Every regression MUST cite real chunk_ids from "
    "the input — never fabricate UUIDs."
)


def _client() -> ApiClient:
    cfg = Configuration(host=os.environ.get("KS_BASE_URL", "https://api.knowledgestack.ai"))
    cfg.api_key["HTTPBearer"] = os.environ["KS_API_KEY"]
    cfg.api_key_prefix["HTTPBearer"] = "Bearer"
    return ApiClient(cfg)


def collect_versions(doc_id: UUID) -> list[dict]:
    with _client() as api:
        versions_api = DocumentVersionsApi(api)
        versions = versions_api.list_document_versions(document_id=doc_id, limit=100).items
        versions = sorted(versions, key=lambda v: v.version)
        out: list[dict] = []
        for v in versions:
            contents = versions_api.get_document_version_contents(
                version_id=v.id, content_type="CHUNK", limit=100
            ).items
            chunks = [
                {"chunk_id": str(c.path_part_id), "text": (c.content or "")[:800]}
                for c in contents if getattr(c, "part_type", None) == "CHUNK"
            ]
            out.append({"version_label": f"v{v.version}", "chunks": chunks})
        return out


async def review(doc_id: UUID, out_path: Path) -> None:
    versions = collect_versions(doc_id)
    if len(versions) < 2:
        sys.exit(f"Document {doc_id} has <2 versions; nothing to compare.")
    agent = Agent(
        model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
        system_prompt=PROMPT, result_type=DriftReport,
    )
    result = await agent.run(json.dumps(versions))
    report = result.data
    lines = [f"# Version drift — document `{doc_id}`", "", "## Summary", "",
             report.summary, "", "## Changelog", ""]
    lines += [f"- {c}" for c in report.changes] or ["- (no changes detected)"]
    lines += ["", "## Regressions (controls weakened)", ""]
    if not report.regressions:
        lines.append("_No regressions detected._")
    for r in report.regressions:
        cites = ", ".join(f"[chunk:{c.chunk_id}]" for c in r.citations)
        lines += [f"### {r.control} ({r.from_version} → {r.to_version})",
                  f"- **Before:** {r.prior_text}", f"- **After:** {r.new_text}",
                  f"- **Why weakened:** {r.why_weakened}", f"- **Citations:** {cites}", ""]
    out_path.write_text("\n".join(lines))
    print(f"Wrote {out_path}")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--doc-id", type=UUID, required=True,
                   help="Document ID (run seed.py to create a demo).")
    p.add_argument("--out", type=Path, default=Path("version-drift.md"))
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(review(args.doc_id, args.out))


if __name__ == "__main__":
    main()
