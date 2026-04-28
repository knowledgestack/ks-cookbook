"""Tool schemas and review template for subrogation opportunity review."""

from typing import Any

TOOLS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "list_contents",
            "description": (
                "List the immediate children of a folder in the Knowledge "
                "Stack tenant. Returns each child's path_part_id (UUID), "
                "name, and part_type."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "folder_id": {
                        "type": "string",
                        "description": "path_part_id of the folder to list.",
                    },
                },
                "required": ["folder_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read",
            "description": (
                "Read the contents of any path-part (folder, document, "
                "section, or chunk). For documents, returns the full outline "
                "with inline [chunk:<uuid>] markers you can cite."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path_part_id": {
                        "type": "string",
                        "description": "UUID of the path-part to read.",
                    },
                    "max_chars": {
                        "type": "integer",
                        "description": "Truncate to this many characters.",
                        "default": 8000,
                    },
                },
                "required": ["path_part_id"],
            },
        },
    },
]


REVIEW_TEMPLATE = """\
# Subrogation Recovery Opportunity Review

**Claim ID:** {claim_id}
**Date of Loss:** {date_of_loss}
**Insured:** {insured}
**Analyst:** Automated Draft (Acme Subrogation Unit — SOP SUB-2026-R1)

## 1. Loss Summary
<one paragraph synthesizing the claim narrative>

## 2. Recovery Potential Classification
<HIGH / MEDIUM / LOW / NONE with rationale> [chunk:<uuid>]

## 3. Liable Party Identification
<name, relationship, contact info if available> [chunk:<uuid>]

## 4. Basis of Liability
<negligence / strict liability / contractual / statutory> [chunk:<uuid>]

## 5. Anti-Subrogation / Waiver Analysis
<check for waivers, co-insured status, anti-subrogation rule> [chunk:<uuid>]

## 6. Made-Whole Doctrine
<applicable jurisdiction and impact on timing> [chunk:<uuid>]

## 7. Estimated Recovery
<dollar amount, calculation basis> [chunk:<uuid>]

## 8. Deductible Recovery
<insured's deductible amount and pro-rata formula> [chunk:<uuid>]

## 9. Recommended Next Steps
<demand letter timeline, arbitration vs litigation, escalation> [chunk:<uuid>]

## Citations
<numbered list; each: document_name — [chunk:<uuid>] "quote">
"""
