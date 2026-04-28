"""Structured output and prompt template for the audit workpaper drafter."""

WORKPAPER_TEMPLATE = """\
# Audit Workpaper — {account_name}

**Client:** {client_name}
**Period:** {period}
**Prepared by:** Automated Draft (PCAOB AS 1215 / AU-C 500)

## 1. Account Summary

| Item | Amount |
|------|--------|
| Balance per GL (trial balance) | {balance_per_gl} |
| Balance per audit | {balance_per_audit} |
| Variance | {variance} |

## 2. Objective
<state the audit objective for this account per the applicable standard>

## 3. Procedures Performed
<for each procedure: description, result, and conclusion>

### Procedure 1: {procedure_1_name}
**Description:** ...
**Result:** ...
**Conclusion:** ...

(repeat for each procedure)

## 4. Conclusion
<overall conclusion on whether the balance is fairly stated>

## 5. Issues / Exceptions
<any exceptions, adjustments, or items requiring follow-up>

## Citations
<numbered list; each entry: document_name — [chunk:<uuid>] "quote">
"""
