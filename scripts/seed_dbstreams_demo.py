"""Seed DB-Streams-branded demo corpora into the local KS tenant.

Produces real PDFs (via reportlab) and real XLSXs (via openpyxl) —
the same messy formats DB Streams' customers store. Claude alone can't cite
into these at the page + row level; Knowledge Stack can.

Usage (deps resolved inline via uv):

    KS_API_KEY=<...> KS_BASE_URL=http://localhost:28000 \\
        uv run --with reportlab --with openpyxl \\
            python scripts/seed_dbstreams_demo.py --parent <folder-uuid>

Creates three sub-folders under ``--parent``:
  - dbstreams-condostack  (for condo_board_decision_pack)
  - dbstreams-sertain     (for legal_matter_intake)
  - dbstreams-chirocrm    (for chiro_visit_autopilot)

Prints env-var lines at the end — paste into .env:

    CONDO_CORPUS_FOLDER_ID=...
    LEGAL_CORPUS_FOLDER_ID=...
    CHIRO_CORPUS_FOLDER_ID=...
"""

from __future__ import annotations

import argparse
import io
import os
import sys
from uuid import UUID

from ksapi import ApiClient, Configuration, CreateFolderRequest, DocumentsApi, FoldersApi
from ksapi.models.ingestion_mode import IngestionMode

# --- Lazy import: reportlab + openpyxl are resolved via `uv run --with ...`.
from openpyxl import Workbook
from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# ---------------------------------------------------------------------------
# PDF / XLSX helpers
# ---------------------------------------------------------------------------


def _pdf(title: str, blocks: list[str | list[list[str]]]) -> bytes:
    """Render a multi-section PDF. Strings → paragraphs; list-of-lists → tables."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=LETTER, title=title)
    styles = getSampleStyleSheet()
    flow: list = [Paragraph(title, styles["Title"]), Spacer(1, 14)]
    for block in blocks:
        if isinstance(block, str):
            for para in block.split("\n\n"):
                flow.append(Paragraph(para.replace("\n", "<br/>"), styles["BodyText"]))
                flow.append(Spacer(1, 8))
        else:
            t = Table(block, hAlign="LEFT")
            t.setStyle(
                TableStyle(
                    [
                        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ]
                )
            )
            flow.append(t)
            flow.append(Spacer(1, 10))
    doc.build(flow)
    return buf.getvalue()


def _xlsx(sheets: dict[str, list[list]]) -> bytes:
    wb = Workbook()
    wb.remove(wb.active)
    for name, rows in sheets.items():
        ws = wb.create_sheet(name)
        for row in rows:
            ws.append(row)
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


# ---------------------------------------------------------------------------
# CondoStack corpus — Bayview Terrace Condominium Corp.
# ---------------------------------------------------------------------------


def condostack_docs() -> dict[str, bytes]:
    declaration = _pdf(
        "Declaration of Condominium — Bayview Terrace CC #1142",
        [
            "<b>Article III — Unit Boundaries.</b> Each Unit is bounded by the "
            "unfinished inner surfaces of the perimeter walls, floors and ceilings. "
            "The roof, exterior walls, balconies, common hallways, and the elevator "
            "shafts are Common Elements.",
            "<b>Article V — Restrictions on Alterations.</b> No Owner shall make any "
            "alteration, addition or improvement to the Common Elements without the "
            "prior written consent of the Board. Installation of equipment affecting "
            "the structural integrity of the building — including but not limited to "
            "solar arrays, satellite dishes, awnings, or HVAC condensers on balconies "
            "— requires a two-thirds (66.7%) vote of Owners, not merely Board approval.",
            "<b>Article VII — Reserve Fund.</b> The Corporation shall maintain a "
            "reserve fund in accordance with the Condominium Act. All work affecting "
            "Common Elements shall be assessed for reserve-fund impact prior to "
            "approval. The current reserve-fund study is incorporated herein by "
            "reference.",
            "<b>Article IX — Short-Term Occupancy.</b> No Unit may be occupied for a "
            "term of less than thirty (30) consecutive days. Listing a Unit on any "
            "short-term rental platform (including but not limited to Airbnb, VRBO) "
            "is expressly prohibited.",
        ],
    )

    bylaws = _pdf(
        "Bylaws — Bayview Terrace CC #1142",
        [
            "<b>Bylaw 12 — Architectural Control Committee.</b> The Board shall "
            "appoint an Architectural Control Committee (ACC) of three Owners to "
            "review alteration requests. The ACC shall render a recommendation to "
            "the Board within 30 days of receiving a complete application.",
            "<b>Bylaw 14 — Board Decisions.</b> Routine alterations within a Unit "
            "may be approved by simple majority of the Board. Alterations affecting "
            "Common Elements require the vote threshold set in the Declaration.",
            "<b>Bylaw 19 — Owner Cost Responsibility.</b> Where the Board approves "
            "an alteration, the requesting Owner bears ALL costs including "
            "permitting, engineering review, installation, ongoing maintenance, "
            "and eventual removal/restoration.",
        ],
    )

    rules = _pdf(
        "Rules & Regulations — Bayview Terrace CC #1142 (adopted 2024-03)",
        [
            "Rule 4.1 — Balcony railings shall remain in the original white "
            "powder-coat finish as specified in the building plans. No alteration to "
            "railing colour, materials, or height is permitted without ACC approval.",
            "Rule 4.2 — Balcony plantings, furniture and decor must not be visible "
            "above the top of the railing from the street.",
            "Rule 7.3 — Storage of combustible materials (including lithium-ion "
            "battery backup units > 1 kWh) in locker rooms is prohibited per Ontario "
            "Fire Code §5.5.",
        ],
    )

    acc_guidelines = _pdf(
        "Architectural Control Committee Guidelines (rev. 2025)",
        [
            "<b>1. Scope.</b> The ACC reviews all requests for modifications that "
            "are visible from the exterior of the building, affect Common Elements, "
            "or involve Unit systems that tie into Common Elements (electrical, "
            "plumbing, HVAC).",
            "<b>2. Application Requirements.</b> A complete application must "
            "include: (a) dimensioned drawings sealed by a licensed engineer; "
            "(b) product specifications; (c) contractor COI naming the Corporation "
            "as additional insured; (d) reserve-fund impact letter from the "
            "Corporation's engineer.",
            "<b>3. Solar Installations.</b> Rooftop solar is prohibited on the "
            "Bayview Terrace building due to the 2019 roof-membrane warranty, which "
            "is voided by penetrations. Any solar request must first demonstrate a "
            "waiver from the roofing vendor (Sika Sarnafil); without it, the ACC "
            "shall recommend denial.",
            "<b>4. Short-Term Rentals.</b> The ACC does NOT hear short-term rental "
            "requests; these are categorically prohibited by Declaration Article IX.",
        ],
    )

    minutes = _pdf(
        "Board Meeting Minutes — 2024 and 2025 (excerpts)",
        [
            "<b>Minute 2024-05-14.</b> Unit 3A requested permission to install a "
            "satellite dish on the balcony. ACC recommended DENIAL citing Rule 4.2 "
            "(visibility above railing) and Declaration Article V (Common Element "
            "alteration). Motion to deny: carried 5-0.",
            "<b>Minute 2024-09-10.</b> Unit 2F requested repainting balcony railings "
            "matte black. ACC recommended DENIAL citing Rule 4.1. Owner offered to "
            "bear all costs. Motion to deny: carried 4-1 with dissent noting that "
            "Rule 4.1 may be revisited at the 2025 AGM.",
            "<b>Minute 2025-01-21.</b> Unit 8D requested solar panels on private "
            "roof-terrace (Unit-owned, not Common Element). ACC recommended "
            "APPROVE_WITH_CONDITIONS: (i) owner provides Sika Sarnafil waiver; "
            "(ii) licensed PE-sealed drawings; (iii) owner indemnifies for any "
            "damage to the common-element roof membrane. Motion: carried 5-0.",
            "<b>Minute 2025-06-17.</b> Unit 7A inquired about listing the Unit on "
            "Airbnb. The Board noted Declaration Article IX prohibits STRs and no "
            "motion was entertained. Owner advised in writing.",
        ],
    )

    reserve_fund = _xlsx(
        {
            "Reserve Fund Summary": [
                [
                    "Component",
                    "Install Year",
                    "Expected Life (yr)",
                    "Replacement Cost (CAD)",
                    "Year of Next Major Work",
                ],
                ["Roof membrane (Sika Sarnafil)", 2019, 25, 480000, 2044],
                ["Elevators (2 cabs)", 2015, 30, 260000, 2045],
                ["Window assemblies", 2015, 35, 910000, 2050],
                ["Boiler + HW system", 2018, 22, 180000, 2040],
                ["Common hallway finishes", 2022, 15, 140000, 2037],
            ],
            "Contributions": [
                ["Year", "Opening Balance", "Contribution", "Expenditures", "Closing Balance"],
                [2023, 820000, 210000, 15000, 1015000],
                [2024, 1015000, 215000, 22000, 1208000],
                [2025, 1208000, 220000, 48000, 1380000],
            ],
        }
    )

    return {
        "bayview_declaration.pdf": declaration,
        "bayview_bylaws.pdf": bylaws,
        "bayview_rules.pdf": rules,
        "bayview_acc_guidelines.pdf": acc_guidelines,
        "bayview_board_minutes.pdf": minutes,
        "bayview_reserve_fund.xlsx": reserve_fund,
    }


# ---------------------------------------------------------------------------
# Sertain corpus — Harbour & Finch LLP
# ---------------------------------------------------------------------------


def sertain_docs() -> dict[str, bytes]:
    engagement = _pdf(
        "Engagement Letter Template — Harbour & Finch LLP",
        [
            "<b>Scope.</b> Our engagement is limited to the matter described in "
            "Schedule A. Any additional work requires a written amendment.",
            "<b>Fees and Retainer.</b> Fees are billed monthly at the rates on "
            "Schedule B. A retainer equal to the first month's estimate is required "
            "before commencement of work.",
            "<b>Conflicts.</b> The Firm has conducted a conflicts check against its "
            "database prior to this engagement. The Client acknowledges any waivers "
            "identified in Schedule C.",
            "<b>Termination.</b> Either party may terminate on 10 days' written "
            "notice; fees incurred to the date of termination remain payable.",
        ],
    )

    playbook = _pdf(
        "Practice-Area Risk Playbook — Internal (rev. 2026-01)",
        [
            "<b>Section 1 — M&A and Financings.</b> Series A/B/C financings: "
            "engage only if the lead investor is one the Firm has acted adverse "
            "to within 5 years, subject to conflict waiver. Require a 20% retainer "
            "uplift for rounds >$25M where a Delaware sub is being formed. Assign "
            "at minimum one senior associate with 3+ years M&A experience.",
            "<b>Section 2 — Life Sciences and IP In-Licensing.</b> Where the "
            "counterparty is a university tech-transfer office (including MIT TLO, "
            "Stanford OTL, UofT Innovations), the Firm MUST assign a patent agent. "
            "Risk of fields-of-use drafting disputes is HIGH.",
            "<b>Section 3 — Employment Litigation.</b> Constructive dismissal "
            "defence: MEDIUM risk. Decline if the plaintiff was a C-suite officer "
            "of a current Firm client within 3 years. Always require a conflicts "
            "check against the plaintiff AND their spouse.",
            "<b>Section 4 — Commercial Real Estate.</b> For acquisitions over "
            "CAD $10M in Toronto, retain local title counsel at Gowling WLG. "
            "Estimate fees at 0.35% of deal value plus disbursements.",
            "<b>Section 5 — Scope Creep Defence.</b> All engagements must include a "
            "written scope in Schedule A. Partners should review scope at 50% of "
            "estimate and renegotiate before exceeding 100%.",
        ],
    )

    lso_rules = _pdf(
        "LSO Rules of Professional Conduct — Excerpts",
        [
            "<b>Rule 3.4-1 — Duty to Avoid Conflicts.</b> A lawyer shall not act "
            "for a client where there is a conflict of interest unless there is "
            "express or implied consent from all clients.",
            "<b>Rule 3.4-10 — Former Client.</b> Unless the former client "
            "consents, a lawyer shall not act against a former client in the same "
            "or a related matter.",
            "<b>Rule 3.6-1 — Fees and Disbursements.</b> A lawyer shall not charge "
            "or accept any fee or disbursement unless it is fair and reasonable "
            "and has been disclosed in a timely fashion.",
            "<b>Rule 7.2-6 — Undertakings.</b> A lawyer shall fulfil every "
            "undertaking given and shall not give an undertaking that cannot be "
            "fulfilled.",
        ],
    )

    conflicts = _xlsx(
        {
            "Conflicts": [
                ["Year", "Client", "Matter Type", "Adverse Party", "Status", "Notes"],
                [
                    2022,
                    "Meridian Capital Partners",
                    "Series B Financing",
                    "Northstar Biotech Ltd.",
                    "Closed",
                    "Acted for investor; Northstar was the issuer.",
                ],
                [
                    2023,
                    "Mercer Industrial Services",
                    "Employment — hiring",
                    "n/a",
                    "Closed",
                    "Drafted CEO employment contract; Mr. Chen.",
                ],
                [
                    2023,
                    "City of Toronto",
                    "Real estate — expropriation",
                    "Harbourfront Holdings Inc.",
                    "Closed",
                    "Acted for City; small parcel at Queen's Quay.",
                ],
                [
                    2024,
                    "Quantum Therapeutics",
                    "IP licensing",
                    "MIT TLO",
                    "Active",
                    "Currently negotiating field-of-use with MIT TLO.",
                ],
                [
                    2024,
                    "BayBridge Capital",
                    "Series A Financing",
                    "Northstar Biotech Ltd.",
                    "Closed",
                    "Acted for investor on $8M seed extension.",
                ],
                [
                    2025,
                    "Sierra Healthcare REIT",
                    "M&A",
                    "n/a",
                    "Active",
                    "Ongoing; firm cannot act adverse to Sierra.",
                ],
            ],
            "Key Relationships": [
                ["Firm Contact", "Counterparty", "Nature"],
                ["Partner Finch", "MIT TLO", "Ongoing adversarial — Quantum matter"],
                ["Partner Cheng", "BayBridge Capital", "Lead counsel relationship"],
                ["Partner Finch", "City of Toronto", "Past adversarial"],
            ],
        }
    )

    fees = _xlsx(
        {
            "Hourly Rates (CAD)": [
                ["Practice Area", "Seniority", "Hourly Rate"],
                ["M&A and Financings", "Partner", 950],
                ["M&A and Financings", "Senior Associate", 625],
                ["M&A and Financings", "Junior Associate", 425],
                ["M&A and Financings", "Paralegal", 235],
                ["Life Sciences / IP", "Partner", 1050],
                ["Life Sciences / IP", "Patent Agent", 550],
                ["Life Sciences / IP", "Senior Associate", 675],
                ["Employment Litigation", "Partner", 875],
                ["Employment Litigation", "Senior Associate", 540],
                ["Commercial Real Estate", "Partner", 825],
                ["Commercial Real Estate", "Senior Associate", 495],
            ],
            "Benchmarks": [
                ["Deal Type", "Typical Fees Low (CAD)", "Typical Fees High (CAD)"],
                ["Series B financing", 180000, 325000],
                ["IP in-licensing (university)", 85000, 160000],
                ["Constructive dismissal defence", 55000, 110000],
                ["Toronto commercial acquisition $18M", 110000, 195000],
            ],
        }
    )

    return {
        "engagement_letter_template.pdf": engagement,
        "practice_risk_playbook.pdf": playbook,
        "lso_rules_excerpt.pdf": lso_rules,
        "conflicts_database.xlsx": conflicts,
        "fee_schedule.xlsx": fees,
    }


# ---------------------------------------------------------------------------
# ChiroCRM corpus — Northside Chiropractic
# ---------------------------------------------------------------------------


def chirocrm_docs() -> dict[str, bytes]:
    soap_note = _pdf(
        "SOAP Note — PT-4401 — 2026-04-18",
        [
            "<b>Subjective.</b> Patient is a 47 y/o office worker with a 4-week "
            "history of low-back pain radiating into the posterior L thigh, worse "
            "with prolonged sitting. Rates 7/10. Prior conservative therapy with "
            "NSAIDs and home exercises (4 weeks documented) without meaningful "
            "relief. No bowel/bladder symptoms, no red flags.",
            "<b>Objective.</b> Positive straight-leg raise at 45° on the left. "
            "Decreased sensation over L5 dermatome. Reflexes 2+ symmetric. Motor "
            "5/5 throughout. Range of motion limited in lumbar flexion (40°, "
            "normal 60°).",
            "<b>Assessment.</b> Lumbar radiculopathy, L5 distribution (ICD-10 "
            "M54.16). Chronic low back pain (M54.50). Patient is an appropriate "
            "candidate for chiropractic manipulative therapy (CMT) with adjunctive "
            "therapeutic exercise.",
            "<b>Plan.</b> Initiate care plan per clinic protocol for lumbar "
            "radiculopathy: 3 visits/week for 2 weeks, then reassess. CMT 3-4 "
            "regions; therapeutic exercise; mechanical traction. Re-evaluation at "
            "6 visits. Submit prior authorization to Sun Life per their medical "
            "policy.",
        ],
    )

    sun_life_policy = _pdf(
        "Sun Life Chiropractic Medical Policy (CMT-2026-03)",
        [
            "<b>Section A — Covered Services.</b> Spinal manipulation (CPT 98940, "
            "98941, 98942) is covered for acute and chronic conditions where "
            "medical necessity is documented.",
            "<b>Section B — Prior Authorization.</b> Prior authorization is "
            "REQUIRED for: (a) any course of care exceeding 12 visits in a rolling "
            "12-month period; (b) any care plan that includes mechanical traction "
            "(CPT 97012); (c) treatment of lumbar radiculopathy.",
            "<b>Section C — Medical Necessity Criteria.</b> Prior authorization "
            "requires documentation of ALL of the following: (1) specific "
            "diagnosis with ICD-10 code; (2) documented conservative therapy of at "
            "least 2 weeks with inadequate relief; (3) objective findings on "
            "examination; (4) a written care plan with functional goals and a "
            "reassessment interval of no more than 6 visits.",
            "<b>Section D — Non-Covered.</b> Wellness / maintenance care (no acute "
            "diagnosis) is NOT covered. Patient is responsible for full fee.",
        ],
    )

    protocols = _pdf(
        "Northside Clinic Treatment Protocols",
        [
            "<b>Protocol 4 — Lumbar Radiculopathy.</b> Phase 1 (weeks 1-2): reduce "
            "acute pain and inflammation. 3 visits/week. Interventions: CMT 3-4 "
            "regions, mechanical traction 15 min, ice 10 min. Home program: "
            "McKenzie extension exercises 3x daily.",
            "Phase 2 (weeks 3-4): restore mobility. 2 visits/week. Add active "
            "therapeutic exercise (neural mobilization, lumbar stabilization). "
            "Reassess at visit 6.",
            "Phase 3 (weeks 5-6): return to activity. 1 visit/week. Advance "
            "exercise; ergonomic counselling for office workers.",
            "<b>Protocol 7 — Whiplash (Grade I-II).</b> Phase 1 (weeks 1-2): "
            "3 visits/week. CMT cervical + thoracic, soft-tissue therapy, "
            "isometric exercises. Phase 2 (weeks 3-4): 2 visits/week; add "
            "proprioceptive and range-of-motion work.",
            "<b>Protocol 12 — Wellness Maintenance.</b> Monthly CMT. NOT a covered "
            "service under typical Canadian payer policies; counsel patient on "
            "self-pay fee. No prior authorization.",
        ],
    )

    fee_schedule = _xlsx(
        {
            "Fees": [
                ["Code", "Type", "Description", "Units Rule", "Fee CAD"],
                ["98940", "CPT", "CMT — 1-2 regions", "per visit", 65.00],
                ["98941", "CPT", "CMT — 3-4 regions", "per visit", 82.00],
                ["98942", "CPT", "CMT — 5 regions", "per visit", 99.00],
                ["97012", "CPT", "Mechanical traction", "per 15 min", 38.00],
                ["97110", "CPT", "Therapeutic exercise", "per 15 min", 42.00],
                ["97140", "CPT", "Manual therapy", "per 15 min", 48.00],
                ["99202", "CPT", "New pt evaluation, low", "per visit", 120.00],
                ["99203", "CPT", "New pt evaluation, moderate", "per visit", 165.00],
                ["97750", "CPT", "Physical performance test", "per 15 min", 52.00],
            ],
            "Memberships": [
                ["Membership", "Monthly Fee CAD", "Included Visits"],
                ["Wellness Basic", 149, 2],
                ["Wellness Plus", 249, 4],
            ],
        }
    )

    cpt_icd_ref = _xlsx(
        {
            "ICD-10": [
                ["Code", "Description"],
                ["M54.16", "Radiculopathy, lumbar region"],
                ["M54.50", "Low back pain, unspecified"],
                ["M54.2", "Cervicalgia"],
                ["S13.4XXA", "Sprain of ligaments of cervical spine, initial"],
                ["M99.01", "Segmental and somatic dysfunction of cervical region"],
                ["M99.03", "Segmental and somatic dysfunction of lumbar region"],
            ],
            "Common Modifiers": [
                ["Modifier", "Description"],
                ["25", "Significant, separately identifiable E/M service"],
                ["59", "Distinct procedural service"],
                ["GA", "Waiver of liability on file (ABN)"],
                ["GY", "Statutorily excluded service"],
            ],
        }
    )

    history = _pdf(
        "Prior Visit History — PT-4401",
        [
            "<b>2026-03-15.</b> Initial evaluation. CC: low back pain x 1 wk. "
            "ROM limited in flexion. No radiculopathy. Plan: home NSAIDs + "
            "McKenzie exercises; reassess in 2 weeks.",
            "<b>2026-03-29.</b> Follow-up. Pain worsening, now radiating into L "
            "posterior thigh. Continues NSAIDs. Home exercises compliance good. "
            "Developing L5 dermatomal findings. Discussed PA submission.",
            "<b>2026-04-05.</b> Phone check-in. Patient reports 8/10 pain. "
            "Scheduled full re-eval and PA submission for next visit.",
        ],
    )

    return {
        "soap_note_PT-4401_2026-04-18.pdf": soap_note,
        "sun_life_chiropractic_policy.pdf": sun_life_policy,
        "northside_treatment_protocols.pdf": protocols,
        "northside_fee_schedule.xlsx": fee_schedule,
        "cpt_icd_reference.xlsx": cpt_icd_ref,
        "prior_visit_history_PT-4401.pdf": history,
    }


# ---------------------------------------------------------------------------
# Upload orchestration
# ---------------------------------------------------------------------------

CORPORA: dict[str, tuple[str, dict[str, bytes]]] = {
    "condostack": ("dbstreams-condostack-bayview", {}),
    "sertain": ("dbstreams-sertain-harbour-finch", {}),
    "chirocrm": ("dbstreams-chirocrm-northside", {}),
}


def _client() -> ApiClient:
    cfg = Configuration(host=os.environ.get("KS_BASE_URL", "http://localhost:8000"))
    api = ApiClient(cfg)
    api.default_headers["Authorization"] = f"Bearer {os.environ['KS_API_KEY']}"
    return api


def _seed(api: ApiClient, parent: UUID, folder_name: str, files: dict[str, bytes]) -> UUID:
    folders = FoldersApi(api)
    sub = folders.create_folder(CreateFolderRequest(name=folder_name, parent_path_part_id=parent))
    sub_id = UUID(str(sub.path_part_id))
    docs = DocumentsApi(api)
    for filename, content in files.items():
        docs.ingest_document(
            file=(filename, content),
            path_part_id=sub_id,
            name=filename,
            ingestion_mode=IngestionMode.STANDARD,
        )
        print(f"  uploaded {filename} ({len(content):,} bytes)")
    return sub_id


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--parent",
        type=UUID,
        required=True,
        help="Existing folder path_part_id to nest demo folders under.",
    )
    p.add_argument(
        "--only",
        choices=list(CORPORA.keys()),
        default=None,
        help="Seed only one corpus (default: all three).",
    )
    args = p.parse_args()

    if not os.environ.get("KS_API_KEY"):
        sys.exit("Set KS_API_KEY.")

    CORPORA["condostack"] = (CORPORA["condostack"][0], condostack_docs())
    CORPORA["sertain"] = (CORPORA["sertain"][0], sertain_docs())
    CORPORA["chirocrm"] = (CORPORA["chirocrm"][0], chirocrm_docs())

    targets = [args.only] if args.only else list(CORPORA.keys())
    env_lines: list[str] = []
    env_var = {
        "condostack": "CONDO_CORPUS_FOLDER_ID",
        "sertain": "LEGAL_CORPUS_FOLDER_ID",
        "chirocrm": "CHIRO_CORPUS_FOLDER_ID",
    }
    with _client() as api:
        for key in targets:
            folder_name, files = CORPORA[key]
            print(f"\nSeeding {folder_name} ({len(files)} files) …")
            sub_id = _seed(api, args.parent, folder_name, files)
            env_lines.append(f"{env_var[key]}={sub_id}")

    print("\n# Paste into .env:")
    for line in env_lines:
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
