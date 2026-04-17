"""Prompt template and output schema for zoning compliance check."""


COMPLIANCE_TEMPLATE = """\
# Zoning Compliance Report

**Address:** {address}
**Zone District:** {zone_district}
**Proposed Use:** {proposed_use}
**Analyst:** Automated Draft (Austin LDC Chapter 25-2)

## 1. Zone District Summary
<describe the district, its purpose, max height, FAR, and general character>
[chunk:<uuid>]

## 2. Permitted Use Determination
<YES / CONDITIONAL / NO / VARIANCE_REQUIRED>
<cite the specific use table entry showing whether the proposed use is P, C,
or not listed for this district> [chunk:<uuid>]

## 3. Applicable Zoning Sections
<list each relevant LDC section, its title, and the relevant text>
[chunk:<uuid>]

## 4. Conditions (if Conditional Use)
<CUP requirements: application, public hearing, compatibility standards>
[chunk:<uuid>]

## 5. Compatibility Standards
<if adjacent to residential: height step-downs, setbacks, screening,
lighting, noise limits> [chunk:<uuid>]

## 6. Development Standards
<max height, FAR, setbacks, lot coverage applicable to this district>
[chunk:<uuid>]

## 7. Next Steps
<what the applicant needs to do: apply by right, file CUP, seek variance,
rezone, etc.> [chunk:<uuid>]

## Citations
<numbered list; each: document_name — [chunk:<uuid>] "quote">
"""
