"""Graph state for the CSV enrichment flow."""

from typing import TypedDict


class Row(TypedDict):
    index: int
    data: dict[str, str]
    query: str


class EnrichmentState(TypedDict, total=False):
    rows: list[Row]
    column: str
    results: dict[int, str]
    fail_fast: bool
    concurrency: int
