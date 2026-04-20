"""Seed a KS tenant with one representative public-corpus document per vertical.

This is the minimum seed that makes the vertical recipes runnable end-to-end.
It does NOT replace a full production corpus — it ships one canonical document
per vertical pack so each recipe has something to cite against.

Usage:
    uv run python scripts/seed_public_corpus.py \
        --folder-id <FOLDER_PATH_PART_ID> [--vertical healthcare|banking|...|all]

The folder-id must be an existing FOLDER path_part_id in your tenant. Each
vertical creates its own sub-folder under that parent. Run once per tenant.

Output: prints the created folder IDs so you can wire them into .env, e.g.

    POLICIES_FOLDER_ID=<generic policies pack>
    CLINICAL_FOLDER_ID=<healthcare pack>
    LEGAL_CORPUS_FOLDER_ID=<legal pack>
    ENERGY_FOLDER_ID=<energy pack>
    ...

Fixture content is intentionally short — the point is to prove the plumbing,
not to be a real domain corpus. Swap in real public-corpus downloads (SEC
EDGAR, CMS, SAM.gov, USPTO, CUAD, state RRCs, IRS.gov, DailyMed) for real
evaluation runs.
"""

from __future__ import annotations

import argparse
import os
import sys
from uuid import UUID

from ksapi import ApiClient, Configuration, DocumentsApi

VERTICALS: dict[str, dict[str, bytes]] = {
    "policies": {
        "access_control_policy.md": b"""# Access Control Policy

- MFA is required for all administrative accounts.
- Passwords must be at least 12 characters with mixed case.
- User access rights are reviewed quarterly.
- Least privilege enforced for production write access.
- Shared service accounts are prohibited.
- Access terminations within 24 hours of HR notification.
""",
        "data_retention_policy.md": b"""# Data Retention Policy

- Customer personal data: retained for 7 years after contract termination.
- Application logs: 90 days hot, 1 year cold.
- Backup retention: 35 days for point-in-time recovery.
- Deletion requests honored within 30 days (GDPR) or 45 days (CCPA).
""",
    },
    "healthcare": {
        "icd10_reference_excerpt.md": b"""# ICD-10-CM Excerpt (Public - CMS)

- I21.4: Non-ST elevation myocardial infarction (NSTEMI)
- E11.9: Type 2 diabetes mellitus without complications
- J45.909: Unspecified asthma, uncomplicated
- J18.9: Pneumonia, unspecified organism
- R07.9: Chest pain, unspecified
""",
        "triage_protocol.md": b"""# Symptom Triage Protocol (fixture)

- Chest pain + diaphoresis + radiation to arm: ED (possible ACS).
- Fever + rigid abdomen: ED.
- Isolated headache, no red flags: telehealth.
- Cough <7 days, no fever, no SOB: self-care.
""",
    },
    "legal": {
        "msa_playbook_excerpt.md": b"""# MSA Playbook Excerpt

- Limitation of liability cap: 12 months of fees paid.
- Indemnification: mutual, carved out for IP, data breach, gross negligence.
- Auto-renewal: opt-out notice 60 days before term end.
- Force majeure: listed events + 'acts of God'; cure window 30 days.
- Governing law: Delaware; venue: SDNY.
""",
    },
    "banking": {
        "basel_iii_weights_excerpt.md": b"""# Basel III Risk Weights (fixture)

- Cash: 0%
- Sovereign (AAA-AA): 0%
- Bank exposure (A-rated): 20%
- Corporate (BBB-rated): 100%
- Corporate (BB-rated): 150%
- Residential mortgage (LTV <=80%): 35%
""",
    },
    "insurance": {
        "policy_handbook_excerpt.md": b"""# Auto Policy Handbook (fixture)

- Collision: first-party damage from impact. Deductible applies.
- Comprehensive: non-collision loss (theft, fire, hail). Deductible applies.
- Uninsured motorist: BI only unless UMPD endorsement added.
- Rental reimbursement: only if Coverage R is elected.
""",
    },
    "energy": {
        "drilling_report_sample.md": b"""# Daily Drilling Report - Well 42-123-45678

- Depth MD: 8,412 ft; TVD: 8,390 ft.
- Formation: Eagle Ford shale.
- HSE: 1 first-aid, pinched finger replacing tong die. No LTI.
- Equipment: top drive motor intermittent fault; replaced sensor.
- Forward: continue drilling to TD 10,200 ft.
""",
    },
    "government": {
        "sam_gov_notice_sample.md": b"""# SAM.gov Notice (fixture)

- Notice ID: 36C24524Q0123
- Agency: Department of Veterans Affairs
- Title: AI-assisted document retrieval with citations
- NAICS: 541512
- Response by: 2026-05-15
- Set-aside: Small Business
""",
    },
    "hr": {
        "spd_excerpt.md": b"""# Benefits Summary Plan Description (fixture)

- HDHP + HSA: employer contributes $1,200/yr (single), $2,400/yr (family).
- PPO: $25 PCP copay, $50 specialist, 20% coinsurance after deductible.
- Dependent coverage: children to age 26.
- HSA: employees with spouse on an FSA are NOT eligible to contribute.
""",
    },
    "finance": {
        "te_policy_excerpt.md": b"""# T&E Policy (fixture)

- Meals: $75/day domestic, $125/day international.
- Client dinner: $150/person cap; receipt required above $25.
- Airfare: economy; premium-economy allowed for flights >6 hours.
- Ground: rideshare preferred; rental car requires manager pre-approval.
""",
    },
}


def _client() -> ApiClient:
    cfg = Configuration(host=os.environ.get("KS_BASE_URL", "https://api.knowledgestack.ai"))
    cfg.api_key["HTTPBearer"] = os.environ["KS_API_KEY"]
    cfg.api_key_prefix["HTTPBearer"] = "Bearer"
    return ApiClient(cfg)


def seed_vertical(api: ApiClient, parent_folder: UUID, vertical: str) -> UUID:
    from ksapi import CreateFolderRequest, FoldersApi  # type: ignore
    folders = FoldersApi(api)
    sub = folders.create_folder(
        CreateFolderRequest(name=f"cookbook-{vertical}", parent_path_part_id=parent_folder)
    )
    docs = DocumentsApi(api)
    sub_id = UUID(str(sub.path_part_id))
    for filename, content in VERTICALS[vertical].items():
        docs.ingest_document(file=(filename, content), path_part_id=sub_id, name=filename)
    return sub_id


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--folder-id", type=UUID, required=True,
                   help="Parent folder path_part_id (must be a FOLDER).")
    p.add_argument("--vertical", default="all",
                   choices=["all", *VERTICALS.keys()])
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY"):
        sys.exit("Set KS_API_KEY.")

    verticals = list(VERTICALS.keys()) if args.vertical == "all" else [args.vertical]
    with _client() as api:
        for v in verticals:
            sub_id = seed_vertical(api, args.folder_id, v)
            env_var = {
                "policies":   "POLICIES_FOLDER_ID",
                "healthcare": "CLINICAL_FOLDER_ID",
                "legal":      "LEGAL_CORPUS_FOLDER_ID",
                "banking":    "REGULATORY_FOLDER_ID",
                "insurance":  "INSURANCE_FOLDER_ID",
                "energy":     "ENERGY_FOLDER_ID",
                "government": "GOV_FOLDER_ID",
                "hr":         "HR_FOLDER_ID",
                "finance":    "FINANCE_FOLDER_ID",
            }[v]
            print(f"{env_var}={sub_id}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
