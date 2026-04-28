"""Tool schemas and the OpenAI function-calling tool list."""

from typing import Any

TOOLS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "list_contents",
            "description": (
                "List the immediate children of a folder in the Knowledge Stack "
                "tenant. Returns each child's path_part_id (UUID), name, and "
                "part_type."
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
                "Read the contents of any path-part (folder, document, section, "
                "or chunk). For documents, returns the full outline with inline "
                "[chunk:<uuid>] markers you can cite. Copy the UUIDs verbatim."
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


ABSTRACT_TEMPLATE = """\
# Lease Abstract — {property_name}

- **Tenant:** <name> [chunk:<uuid>]
- **Landlord:** <name> [chunk:<uuid>]
- **Premises:** <suite, RSF, address> [chunk:<uuid>]
- **Lease Date:** <date> [chunk:<uuid>]
- **Commencement / Expiration:** <dates> [chunk:<uuid>]
- **Initial Term:** <years> [chunk:<uuid>]

## Rent Schedule
<table or bullets; cite each step> [chunk:<uuid>]

## Renewal Options
<count, length, notice window, rent mechanism> [chunk:<uuid>]

## Operating Expenses / CAM
<pro-rata share, inclusions, exclusions, reconciliation, audit rights> [chunk:<uuid>]

## Key Covenants
- **Exclusive Use:** ... [chunk:<uuid>]
- **Radius Restriction:** ... [chunk:<uuid>]
- **Assignment / Subletting:** ... [chunk:<uuid>]

## Default and Remedies
<cure periods, remedies summary> [chunk:<uuid>]

## Special Items
<TI allowance, parking, signage, ROFR/ROFO> [chunk:<uuid>]
"""
