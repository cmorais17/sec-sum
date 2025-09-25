from .models import DownloadSpec, FilingKey


def build_primary_url(f: FilingKey) -> str:
    """
    /Archives/edgar/data/{cik_plain}/{acc_no_dash}/{primary_document}
    (cik_plain = int without leading zeros)
    """
    raise NotImplementedError


def build_index_url(f: FilingKey) -> str:
    """Return directory index URL (HTML or JSON if available)."""
    raise NotImplementedError


def build_download_plain(f: FilingKey) -> list[DownloadSpec]:
    """
    At minimum:
        - primary doc (kind='primary')
        - index page (kind='index')
    Optionally add:
        - xbrl instance(s) when easily identifiable later
    """
    raise NotImplementedError
