"""Markdown template for FOIA response output."""


RESPONSE_TEMPLATE = """\
# FOIA Response — {request_summary}

**Request Date:** {date}
**Response Type:** {response_type}
**FOIA Officer:** Automated Draft

## Cover Letter

{cover_letter}

## Records Search Summary

{search_summary}

## Exemptions Applied

{exemptions_applied}

## Redaction Notes

{redaction_notes}

## Fee Assessment

{fee_assessment}

## Appeal Rights

The requester has the right to appeal this determination within 90 days
of the date of this response. Appeals should be directed to the agency's
FOIA Appeals Officer.

## Citations

{citations}
"""
