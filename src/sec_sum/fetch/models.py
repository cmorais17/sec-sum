from dataclasses import dataclass


@dataclass(frozen=True)
class CompanyId:
    ticker: str | None
    cik10: str


@dataclass(frozen=True)
class FilingKey:
    cik10: str
    accession: str
    accession_nodash: str
    form: str
    filing_date: str
    report_period: str | None
    primary_document: str


@dataclass(frozen=True)
class DownloadSpec:
    url: str
    kind: str
    dest_relpath: str


@dataclass(frozen=True)
class DownloadResult:
    spec: DownloadSpec
    status_code: int
    bytes: int
    sha256: str
    downloaded_at: str


@dataclass
class Manifest:
    company: CompanyId
    filing: FilingKey
    source_urls: list[str]
    files: list[DownloadResult]
    user_agent: str
    notes: dict[str, str]
