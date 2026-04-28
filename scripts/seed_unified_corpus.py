"""Seed a Knowledge Stack tenant with the unified cookbook corpus.

Walks ``seed/ingest/<vertical>/`` and uploads every real document into one
shared parent folder (``cookbook-corpus`` by default), one sub-folder per
vertical. Prints the resulting per-vertical FOLDER_ID env-var lines so they
can be pasted straight into ``.env``.

This is the single ingest the cookbook expects. Every one of the 150+
recipes / flagships reads against one of these vertical sub-folders — there
are no per-recipe corpora to seed.

Usage:
    KS_API_KEY=... KS_BASE_URL=https://api.knowledgestack.ai \\
        uv run python scripts/seed_unified_corpus.py \\
            --parent-folder-id <PARENT_FOLDER_PATH_PART_ID>

The parent folder must exist in your tenant. Create it once via the UI (or
via curl); the script creates ``cookbook-corpus/<vertical>/`` underneath.

Why curl-driven instead of the SDK: the generated SDK is missing auth wiring
on several folder/document endpoints; direct HTTP with a bearer header is
the reliable path until ksapi is regenerated.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any
from uuid import UUID

SEED_ROOT = Path(__file__).resolve().parent.parent / "seed"

ENV_VARS_BY_VERTICAL: dict[str, list[str]] = {
    # Each vertical sub-folder of cookbook-corpus advertises every FOLDER_ID
    # env var that any recipe/flagship in that domain reads. The mapping
    # exists because some env vars don't have a perfect 1:1 vertical (e.g.
    # SALES_NOTES_FOLDER_ID maps to the finance vertical because the only
    # public-domain "sales note" content is SEC earnings transcripts).
    "healthcare": ["CLINICAL_FOLDER_ID", "MEDICARE_FOLDER_ID"],
    "pharma": ["PHARMA_PV_FOLDER_ID", "CLINICAL_TRIALS_FOLDER_ID"],
    "legal": ["LEGAL_CORPUS_FOLDER_ID", "DOCKET_FOLDER_ID", "PATENTS_FOLDER_ID"],
    "finance": [
        "FINANCE_FOLDER_ID",
        "BOARD_FOLDER_ID",
        "VC_DATAROOM_FOLDER_ID",
        "PROCUREMENT_FOLDER_ID",
        "SALES_NOTES_FOLDER_ID",
        "ACCOUNT_NOTES_FOLDER_ID",
        "ICP_FOLDER_ID",
        "COMPETE_FOLDER_ID",
        "MEETINGS_FOLDER_ID",
    ],
    "banking": [
        "LENDING_FOLDER_ID",
        "AML_FOLDER_ID",
        "KYC_CORPUS_FOLDER_ID",
        "REGULATORY_FOLDER_ID",
    ],
    "insurance": ["INSURANCE_FOLDER_ID"],
    "energy": ["ENERGY_FOLDER_ID"],
    "government": ["GOV_FOLDER_ID", "GOV_RFP_FOLDER_ID", "RFP_FOLDER_ID"],
    "hr": ["HR_FOLDER_ID"],
    "policies": ["POLICIES_FOLDER_ID", "SEC_POLICY_FOLDER_ID", "PRIVACY_FOLDER_ID", "KB_FOLDER_ID"],
    "eng": ["ENG_DOCS_FOLDER_ID", "ENG_FOLDER_ID", "FINOPS_FOLDER_ID"],
    "marketing": ["MARKETING_FOLDER_ID", "CS_NOTES_FOLDER_ID"],
    "realestate": ["REAL_ESTATE_FOLDER_ID", "CONSTRUCTION_FOLDER_ID"],
}


def _request(
    method: str,
    url: str,
    token: str,
    body: dict | None = None,
    multipart: tuple[Path, UUID] | None = None,
) -> dict[str, Any]:
    req = urllib.request.Request(url, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    data: bytes
    if multipart is not None:
        path, parent_id = multipart
        boundary = "----cookbook" + str(int(time.time() * 1000))
        body_bytes = path.read_bytes()
        parts: list[bytes] = []
        parts.append(f"--{boundary}\r\n".encode())
        parts.append(
            f'Content-Disposition: form-data; name="file"; filename="{path.name}"\r\n'
            f"Content-Type: application/pdf\r\n\r\n".encode()
        )
        parts.append(body_bytes)
        parts.append(b"\r\n")
        for k, v in (("path_part_id", str(parent_id)), ("name", path.name)):
            parts.append(f"--{boundary}\r\n".encode())
            parts.append(f'Content-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode())
        parts.append(f"--{boundary}--\r\n".encode())
        data = b"".join(parts)
        req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
    elif body is not None:
        data = json.dumps(body).encode()
        req.add_header("Content-Type", "application/json")
    else:
        data = b""
    try:
        with urllib.request.urlopen(req, data=data or None, timeout=120) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        sys.exit(f"HTTP {e.code} on {method} {url}: {e.read().decode()[:300]}")


def create_folder(base: str, token: str, name: str, parent: UUID) -> UUID:
    """Create folder; if it already exists under this parent, return its id."""
    try:
        res = _request(
            "POST",
            f"{base}/v1/folders",
            token,
            body={"name": name, "parent_path_part_id": str(parent)},
        )
        return UUID(str(res["path_part_id"]))
    except SystemExit as e:
        if "already exists" not in str(e):
            raise
        # Look it up under the parent
        listing = _request("GET", f"{base}/v1/folders?parent_path_part_id={parent}", token)
        for item in listing.get("items", []):
            if item.get("name") == name:
                return UUID(str(item["path_part_id"]))
        raise


def ingest_file(base: str, token: str, path: Path, parent: UUID) -> str | None:
    """Upload file; return workflow_id, or None if already ingested."""
    try:
        res = _request("POST", f"{base}/v1/documents/ingest", token, multipart=(path, parent))
        return str(res["workflow_id"])
    except SystemExit as e:
        if "already exists" in str(e):
            return None
        raise


def wait_workflow(base: str, token: str, workflow_id: str, *, timeout_s: int = 900) -> str:
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        res = _request("GET", f"{base}/v1/workflows/{workflow_id}", token)
        status = res.get("temporal_status", "UNKNOWN")
        if status != "RUNNING":
            return status
        time.sleep(8)
    return "TIMEOUT"


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--parent-folder-id",
        type=UUID,
        required=True,
        help="Existing parent folder path_part_id under which to create cookbook-corpus.",
    )
    p.add_argument("--corpus-name", default="cookbook-corpus")
    p.add_argument("--vertical", default="all")
    p.add_argument("--no-wait", action="store_true", help="Don't poll workflows to completion.")
    args = p.parse_args()

    token = os.environ.get("KS_API_KEY")
    base = os.environ.get("KS_BASE_URL", "https://api.knowledgestack.ai").rstrip("/")
    if not token:
        sys.exit("Set KS_API_KEY.")
    if not SEED_ROOT.is_dir():
        sys.exit(f"Missing seed root: {SEED_ROOT}")

    verticals = sorted(p.name for p in SEED_ROOT.iterdir() if p.is_dir() and any(p.iterdir()))
    if args.vertical != "all":
        verticals = [args.vertical]

    print(f"# Creating {args.corpus_name}/ under parent {args.parent_folder_id}", file=sys.stderr)
    corpus_id = create_folder(base, token, args.corpus_name, args.parent_folder_id)
    print(f"# corpus_id={corpus_id}", file=sys.stderr)

    workflows: list[tuple[str, str]] = []  # (vertical, workflow_id)
    folder_ids: dict[str, UUID] = {}

    for v in verticals:
        files = sorted(p for p in (SEED_ROOT / v).iterdir() if p.is_file())
        if not files:
            print(f"# skipping empty vertical: {v}", file=sys.stderr)
            continue
        sub_id = create_folder(base, token, v, corpus_id)
        folder_ids[v] = sub_id
        print(f"# {v}/ → {sub_id}", file=sys.stderr)
        for f in files:
            wf = ingest_file(base, token, f, sub_id)
            if wf is None:
                print(f"#   skipped {f.name} (already ingested)", file=sys.stderr)
                continue
            workflows.append((f"{v}/{f.name}", wf))
            print(f"#   uploaded {f.name} → workflow {wf}", file=sys.stderr)

    if not args.no_wait:
        print(f"# waiting for {len(workflows)} ingestion workflows ...", file=sys.stderr)
        for label, wf in workflows:
            status = wait_workflow(base, token, wf)
            print(f"# {label}: {status}", file=sys.stderr)

    print("# ----- paste into .env -----")
    print(f"COOKBOOK_CORPUS_FOLDER_ID={corpus_id}")
    for v, sub_id in folder_ids.items():
        for var in ENV_VARS_BY_VERTICAL.get(v, [f"{v.upper()}_FOLDER_ID"]):
            print(f"{var}={sub_id}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
