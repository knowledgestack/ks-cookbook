"""Seed a KS tenant with the on-disk public corpus under ``seed/``.

The corpus is **just a folder of real files** — see ``seed/README.md``. This
script walks ``seed/<vertical>/`` and uploads every file it finds into a
matching sub-folder of the parent folder you pass in. Whatever is on disk is
what ends up in the tenant; there are no inline fixtures.

Usage:
    uv run python scripts/seed_public_corpus.py \
        --folder-id <FOLDER_PATH_PART_ID> [--vertical healthcare|banking|...|all]

The folder-id must be an existing FOLDER path_part_id in your tenant. Each
vertical creates its own sub-folder (``cookbook-<vertical>``) under that
parent. Run once per tenant.

Output: prints the created folder IDs so you can wire them into ``.env``:

    POLICIES_FOLDER_ID=<generic policies pack>
    CLINICAL_FOLDER_ID=<healthcare pack>
    LEGAL_CORPUS_FOLDER_ID=<legal pack>
    ...

To extend the corpus, drop files into ``seed/<vertical>/`` — no code change.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from uuid import UUID

from ksapi import ApiClient, Configuration, DocumentsApi

SEED_ROOT = Path(__file__).resolve().parent.parent / "seed"

ENV_VAR_BY_VERTICAL: dict[str, str] = {
    "policies": "POLICIES_FOLDER_ID",
    "healthcare": "CLINICAL_FOLDER_ID",
    "legal": "LEGAL_CORPUS_FOLDER_ID",
    "banking": "REGULATORY_FOLDER_ID",
    "insurance": "INSURANCE_FOLDER_ID",
    "energy": "ENERGY_FOLDER_ID",
    "government": "GOV_FOLDER_ID",
    "hr": "HR_FOLDER_ID",
    "finance": "FINANCE_FOLDER_ID",
}


def _discover_verticals() -> list[str]:
    if not SEED_ROOT.is_dir():
        sys.exit(f"Seed root not found: {SEED_ROOT}")
    return sorted(
        p.name
        for p in SEED_ROOT.iterdir()
        if p.is_dir() and not p.name.startswith(".") and any(p.iterdir())
    )


def _client() -> ApiClient:
    cfg = Configuration(host=os.environ.get("KS_BASE_URL", "https://api.knowledgestack.ai"))
    cfg.api_key["HTTPBearer"] = os.environ["KS_API_KEY"]
    cfg.api_key_prefix["HTTPBearer"] = "Bearer"
    return ApiClient(cfg)


def seed_vertical(api: ApiClient, parent_folder: UUID, vertical: str) -> UUID:
    from ksapi import CreateFolderRequest, FoldersApi  # type: ignore

    vertical_dir = SEED_ROOT / vertical
    files = sorted(p for p in vertical_dir.iterdir() if p.is_file() and not p.name.startswith("."))
    if not files:
        sys.exit(f"No files under {vertical_dir} — add documents before seeding.")

    folders = FoldersApi(api)
    sub = folders.create_folder(
        CreateFolderRequest(name=f"cookbook-{vertical}", parent_path_part_id=parent_folder)
    )
    sub_id = UUID(str(sub.path_part_id))

    docs = DocumentsApi(api)
    for path in files:
        docs.ingest_document(
            file=(path.name, path.read_bytes()),
            path_part_id=sub_id,
            name=path.name,
        )
    return sub_id


def main() -> int:
    available = _discover_verticals()
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--folder-id",
        type=UUID,
        required=True,
        help="Parent folder path_part_id (must be a FOLDER).",
    )
    p.add_argument("--vertical", default="all", choices=["all", *available])
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY"):
        sys.exit("Set KS_API_KEY.")

    verticals = available if args.vertical == "all" else [args.vertical]
    with _client() as api:
        for v in verticals:
            sub_id = seed_vertical(api, args.folder_id, v)
            env_var = ENV_VAR_BY_VERTICAL.get(v, f"{v.upper()}_FOLDER_ID")
            print(f"{env_var}={sub_id}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
