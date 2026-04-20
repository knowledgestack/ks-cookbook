"""Seed three versions of an Access Control Policy with deliberate drift.

v1 (2024-Q1) — baseline.
v2 (2024-Q3) — tightened: MFA for all users, longer passwords, monthly reviews.
v3 (2025-Q1) — REGRESSION: MFA downgraded to "recommended", passwords shortened
               to 8 chars, access review cadence changed to annual, shared
               service accounts permitted with manager approval.

Run once, prints the ``document_id`` to feed into ``recipe.py --doc-id <id>``.

This is a fixture, not a recipe — LOC cap doesn't apply.
"""

import argparse
import os
import sys
from uuid import UUID

from ksapi import ApiClient, Configuration, DocumentsApi

V1 = b"""# Access Control Policy v1 (2024-Q1)

- MFA is required for all administrative accounts.
- Passwords must be at least 12 characters with mixed case and symbols.
- User access rights are reviewed every quarter.
- Least privilege is enforced for production write access.
- Shared service accounts are prohibited.
- Access terminations complete within 24 hours of HR notification.
"""

V2 = b"""# Access Control Policy v2 (2024-Q3)

- MFA is required for ALL users, including read-only roles.
- Passwords must be at least 14 characters; passphrases are encouraged.
- User access rights are reviewed every quarter; on-call exceptions are
  re-reviewed monthly.
- Least privilege is enforced for all production systems (read and write).
- Shared service accounts are prohibited without exception.
- Access terminations complete within 8 hours of HR notification.
- Break-glass accounts require dual approval and are logged to the SIEM.
"""

V3 = b"""# Access Control Policy v3 (2025-Q1)

- MFA is recommended for administrative accounts.
- Passwords must be at least 8 characters.
- User access rights are reviewed annually.
- Least privilege applies to production write access where feasible.
- Shared service accounts are allowed with manager approval.
- Access terminations complete within 72 hours of HR notification.
- Break-glass accounts require a single approver.
"""


def _client() -> ApiClient:
    api_key = os.environ["KS_API_KEY"]
    base = os.environ.get("KS_BASE_URL", "https://api.knowledgestack.ai")
    cfg = Configuration(host=base)
    cfg.api_key["HTTPBearer"] = api_key
    cfg.api_key_prefix["HTTPBearer"] = "Bearer"
    return ApiClient(cfg)


def seed(folder_id: UUID, name: str) -> UUID:
    with _client() as api:
        docs = DocumentsApi(api)
        ingest = docs.ingest_document(
            file=(f"{name}.md", V1),
            path_part_id=folder_id,
            name=f"{name} v1",
        )
        doc_id = ingest.document.id
        docs.ingest_document_version(document_id=doc_id, file=(f"{name}.md", V2))
        docs.ingest_document_version(document_id=doc_id, file=(f"{name}.md", V3))
        return doc_id


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--folder-id",
        type=UUID,
        default=UUID(os.environ.get(
            "POLICIES_FOLDER_ID", "ab926019-ac7a-579f-bfda-6c52a13c5f41"
        )),
        help="Parent folder path_part_id (must be a FOLDER).",
    )
    p.add_argument("--name", default="Access Control Policy")
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY"):
        sys.exit("KS_API_KEY is not set.")
    doc_id = seed(args.folder_id, args.name)
    print(doc_id)


if __name__ == "__main__":
    main()
