from .models import DownloadSpec, FilingKey


def _plain_cik(cik10: str) -> str:
    """Convert zero-padded CIK to no padding CIK string"""
    return str(int(cik10))


def build_primary_url(f: FilingKey) -> str:
    """
    /Archives/edgar/data/{cik_plain}/{acc_no_dash}/{primary_document}
    (cik_plain = int without leading zeros)
    """
    cik_plain = _plain_cik(f.cik10)
    return (
        f"https://www.sec.gov/Archives/edgar/data/"
        f"{cik_plain}/{f.accession_nodash}/{f.primary_document}"
    )


def build_index_url(f: FilingKey) -> str:
    """Return directory index URL (HTML)."""
    cik_plain = _plain_cik(f.cik10)
    return f"https://www.sec.gov/Archives/edgar/data/{cik_plain}/{f.accession_nodash}/index.html"


def build_download_plan(f: FilingKey) -> list[DownloadSpec]:
    """
    - primary doc (kind='primary')
    - index page (kind='index')
    """
    primary = DownloadSpec(
        url=build_primary_url(f),
        kind="primary",
        dest_relpath=f.primary_document,
    )
    index = DownloadSpec(
        url=build_primary_url(f),
        kind="index",
        dest_relpath="index.path",
    )
    return [primary, index]
