from typing import Any

from .models import CompanyId, FilingKey
from .net import HttpClient


def submissions_url(cik10: str) -> str:
    """Return official submissions JSON URL for given CIK(10)."""
    raise NotImplementedError


def fetch_submissions_json(http: "HttpClient", company: CompanyId) -> dict[str, Any]:
    """GET submissions JSON; caller handles caching via http client."""
    raise NotImplementedError


def parse_filing_rows(submissions_json: dict[str, Any]) -> list[FilingKey]:
    """
    Extract rows into FilingKey list.
    Must:
        - Include accession with and without dashes
        - Include primaryDocument, form, dates
        - Keep source ordering (most recent first)
    """
    raise NotImplementedError
