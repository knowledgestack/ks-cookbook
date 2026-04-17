"""Prompt template describing the memo shape the agent must return."""


MEMO_TEMPLATE = """\
# Coverage Analysis Memorandum

**Claim Number:** {claim_number}
**Date of Loss:** {date_of_loss}
**Insured:** {insured}
**Adjudicator:** Automated Draft (Acme Claims SOP CLM-2026-R2)

## 1. Loss Summary
<one paragraph synthesizing the FNOL narrative>

## 2. Applicable Policy Form
<name of the policy form the adjuster should rely on, cited to the SOP>

## 3. Covered Peril Analysis
<is the cause of loss a covered peril? cite the specific insuring agreement>

## 4. Exclusion Analysis
<walk each potentially-triggered exclusion; cite policy wording; note any
ensuing-loss carve-back>

## 5. Duties After Loss
<which duties has the insured satisfied, which are pending>

## 6. Reserve Recommendation
<tier per SOP (minor/moderate/severe/complex) and rationale>

## 7. Escalation
<whether the claim triggers any mandatory-escalation threshold>

## Citations
<numbered list; each entry: document_name — [chunk:<uuid>] "quote">
"""
