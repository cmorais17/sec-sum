import json
from typing import Any

from .models import FilingKey
from .net import HttpClient


def submissions_url(cik10: str) -> str:
    """Return official submissions JSON URL for given CIK(10)."""
    return f"https://data.sec.gov/submissions/CIK{cik10}.json"


def fetch_submissions_json(http: "HttpClient", cik10: str) -> dict[str, Any] | Any:
    """GET submissions JSON; Returns the JSON as a dict"""
    url = submissions_url(cik10)
    status, content, headers = http.get(url)
    try:
        return json.loads(content)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Unable to decode JSON from {url}") from exc


def parse_filing_rows(cik10: str, submissions_json: dict[str, Any]) -> list[FilingKey]:
    """
    Extract rows into FilingKey list.
    Must:
        - Include accession with and without dashes
        - Include primaryDocument, form, dates
        - Keep source ordering (most recent first)
    """
    filings = submissions_json.get("filings", {})
    recent = filings.get("recent", {})

    accession_numbers = recent.get("accessionNumber", [])
    forms = recent.get("form", [])
    filing_dates = recent.get("filingDate", [])
    report_periods = recent.get("reportDate", [])
    primary_documents = recent.get("primaryDocument", [])

    rows: list[FilingKey] = []

    for acc, form, fdate, rdate, primary in zip(
        accession_numbers, forms, filing_dates, report_periods, primary_documents, strict=False
    ):
        acc = str(acc)
        accession_nodash = acc.replace("-", "")
        rows.append(
            FilingKey(
                cik10=cik10,
                accession=acc,
                accession_nodash=accession_nodash,
                form=str(form),
                filing_date=str(fdate),
                report_period=str(rdate) if rdate else None,
                primary_document=str(primary),
            )
        )
    return rows
