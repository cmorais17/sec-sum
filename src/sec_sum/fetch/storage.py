from collections.abc import Iterator
from dataclasses import asdict
import hashlib
import json
import pathlib
from typing import Any

from .models import CompanyId, DownloadResult, DownloadSpec, FilingKey, Manifest


def company_dir(root: pathlib.Path, cik10: str) -> pathlib.Path:
    return root / cik10


def filing_dir(root: pathlib.Path, f: FilingKey) -> pathlib.Path:
    return company_dir(root, f.cik10) / f.accession_nodash


def path_for(fdir: pathlib.Path, spec: DownloadSpec) -> pathlib.Path:
    return fdir / spec.dest_relpath


def compute_sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def exists_and_same(path: pathlib.Path, expected_sha256: str | None = None) -> bool:
    """Return True if already downloaded (size/hash match)."""
    if not path.exists():
        return False
    if expected_sha256 is None:
        return True
    actual = compute_sha256(path.read_bytes())
    return actual == expected_sha256


def write_file_atomic(path: pathlib.Path, content: bytes) -> None:
    """Write via temp file + rename."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_bytes(content)
    tmp.replace(path)


def write_manifest(path: pathlib.Path, manifest: Manifest) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = asdict(manifest)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
    tmp.replace(path)


def _manifest_from_dict(data: dict[str, Any]) -> Manifest:
    # Reconstruct dataclasses from dict
    company_raw = data["company"]
    filing_raw = data["filing"]
    files_raw = data["files"]

    company = CompanyId(
        ticker=company_raw.get("ticker"),
        cik10=company_raw["cik10"],
    )
    filing = FilingKey(
        cik10=filing_raw["cik10"],
        accession=filing_raw["accession"],
        accession_nodash=filing_raw["accession_nodash"],
        form=filing_raw["form"],
        filing_date=filing_raw["filing_date"],
        report_period=filing_raw.get("report_period"),
        primary_document=filing_raw["primary_document"],
    )

    files: list[DownloadResult] = []
    for item in files_raw:
        spec_raw = item["spec"]
        spec = DownloadSpec(
            url=spec_raw["url"],
            kind=spec_raw["kind"],
            dest_relpath=spec_raw["dest_relpath"],
        )
        files.append(
            DownloadResult(
                spec=spec,
                status_code=item["status_code"],
                bytes=item["bytes"],
                sha256=item["sha256"],
                downloaded_at=item["downloaded_at"],
            )
        )
    return Manifest(
        company=company,
        filing=filing,
        source_urls=list(data.get("source_urls", [])),
        files=files,
        user_agent=data.get("user_agent", ""),
        notes=dict(data.get("notes", {})),
    )


def read_manifest(path: pathlib.Path) -> Manifest:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"Manifest {path} is not a JSON object")
    return _manifest_from_dict(raw)


def enumerate_needed(specs: list[DownloadSpec], fdir: pathlib.Path) -> Iterator[DownloadSpec]:
    """Yield only those not there"""
    for spec in specs:
        dest = path_for(fdir, spec)
        if not dest.exists():
            yield spec
