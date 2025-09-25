from collections.abc import Iterator
import pathlib

from .models import DownloadSpec, FilingKey, Manifest


def company_dir(root: pathlib.Path, cik10: str) -> pathlib.Path:
    raise NotImplementedError


def filing_dir(root: pathlib.Path, f: FilingKey) -> pathlib.Path:
    raise NotImplementedError


def path_for(f: FilingKey, spec: DownloadSpec) -> pathlib.Path:
    raise NotImplementedError


def exists_and_same(path: pathlib.Path, expected_sha256: str | None = None) -> bool:
    """Return True if already downloaded (size/hash match when given)."""
    raise NotImplementedError


def write_file_atomic(path: pathlib.Path, content: bytes) -> None:
    """Write via temp file + rename."""
    raise NotImplementedError


def compute_sha256(content: bytes) -> str:
    raise NotImplementedError


def write_manifest(path: pathlib.Path, manifest: Manifest) -> None:
    raise NotImplementedError


def read_manifest(path: pathlib.Path) -> Manifest:
    raise NotImplementedError


def enumerate_needed(specs: list[DownloadSpec], fdir: pathlib.Path) -> Iterator[DownloadSpec]:
    """Yield only those not present or mismatched (for idempotency)."""
    raise NotImplementedError
