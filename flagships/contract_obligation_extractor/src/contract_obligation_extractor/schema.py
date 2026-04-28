"""Structured output for the obligation extractor."""

from enum import Enum

from pydantic import BaseModel, Field


class Holder(str, Enum):
    PROVIDER = "Provider"
    CUSTOMER = "Customer"
    MUTUAL = "Mutual"
    # Contract-type-specific roles the LLM may use depending on the agreement
    # (NDAs use "Receiving Party" / "Disclosing Party", DPAs use
    # "Processor"/"Controller", etc.). We allow them to keep the extraction
    # readable rather than forcing everything into Provider/Customer.
    RECEIVING_PARTY = "Receiving Party"
    DISCLOSING_PARTY = "Disclosing Party"
    PROCESSOR = "Processor"
    CONTROLLER = "Controller"
    OTHER = "Other"


class Obligation(BaseModel):
    holder: Holder = Field(
        ...,
        description=(
            "Who is obligated — Provider, Customer, Mutual, or a role "
            "specific to the contract type (Receiving Party / Disclosing "
            "Party for NDAs; Processor / Controller for DPAs). Use 'Other' "
            "only if none fit."
        ),
    )
    verb: str = Field(
        ..., description="The modal verb used (shall | must | will).", max_length=20
    )
    summary: str = Field(
        ...,
        max_length=500,
        description="Plain-English one-sentence summary of the obligation.",
    )
    quote: str = Field(
        ...,
        max_length=800,
        description="Verbatim (or near-verbatim) clause quote, <=800 chars.",
    )
    chunk_id: str = Field(
        ...,
        description="UUID copied from a [chunk:<uuid>] marker in the retrieved text.",
    )
    section: str = Field(
        default="",
        max_length=120,
        description="Section heading the obligation appears under (e.g., 'Payment').",
    )


class ObligationReport(BaseModel):
    document_name: str = Field(..., max_length=200)
    obligations: list[Obligation] = Field(
        default_factory=list,
        description=(
            "All shall/must/will obligations found. Each must carry a real chunk_id "
            "copied verbatim from a [chunk:...] marker."
        ),
    )
