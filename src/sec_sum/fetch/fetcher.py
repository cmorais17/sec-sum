from datetime import UTC, datetime
from pathlib import Path

from .archive import build_download_plan
from .models import CompanyId, DownloadResult, Manifest
from .net import HttpClient
from .select import exclude_amendments, filter_forms, take_limit
from .storage import (
    compute_sha256,
    filing_dir,
    path_for,
    write_file_atomic,
    write_manifest,
)
from .submissions import fetch_submissions_json, parse_filing_rows, submissions_url


def _utc_now_iso() -> str:
    """Current UTC time in ISO8601 w/ Z suffix."""
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


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
    root = Path(data_root)

    # 1-2
    subs_json = fetch_submissions_json(http, company.cik10)
    rows = parse_filing_rows(company.cik10, subs_json)

    # 3
    filtered = filter_forms(rows, forms)
    if not include_amendments:
        filtered = exclude_amendments(filtered)

    # 4
    chosen = take_limit(filtered, limit)
    if not chosen:
        return []

    manifests: list[Manifest] = []
    subs_url = submissions_url(company.cik10)

    for filing in chosen:
        fdir = filing_dir(root, filing)
        specs = build_download_plan(filing)

        files: list[DownloadResult] = []
        source_urls: list[str] = [subs_url]

        for spec in specs:
            source_urls.append(spec.url)
            dest = path_for(fdir, spec)

            if dest.exists():
                content = dest.read_bytes()
                status_code = 200
            else:
                status_code, content, _headers = http.get(spec.url)
                write_file_atomic(dest, content)

            sha = compute_sha256(content)
            files.append(
                DownloadResult(
                    spec=spec,
                    status_code=status_code,
                    bytes=len(content),
                    sha256=sha,
                    downloaded_at=_utc_now_iso(),
                )
            )

        # Dedup source_urls
        seen: set[str] = set()
        deduped_urls: list[str] = []
        for u in source_urls:
            if u not in seen:
                seen.add(u)
                deduped_urls.append(u)

        manifest = Manifest(
            company=company,
            filing=filing,
            source_urls=deduped_urls,
            files=files,
            user_agent=http.user_agent,
            notes={"amendments_included": str(include_amendments).lower()},
        )

        write_manifest(fdir / "manifest.json", manifest)
        manifests.append(manifest)

    return manifests
