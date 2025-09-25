from .models import CompanyId, Manifest
from .net import HttpClient


def fetch_pipeline(
    http: HttpClient,
    company: CompanyId,
    forms: list[str],
    limit: int,
    data_root: str,
    include_amendments: bool = False,
) -> list[Manifest]:
    """
    Steps:
        1) GET submissions JSON
        2) Parse FilingKey rows
        3) Filter forms (& exclude amendments unless flag)
        4) Take limit
        5) For each filing:
            a) build_download_plan()
            b) for each spec:
                - skip if already downloaded
                - GET, hash, write
            c) write manifest.json with provenance
        6) Return list of manifests
    """
    raise NotImplementedError
