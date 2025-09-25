from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AppConfig:
    app_name: str = "sec-sum"
    version: str = "0.1.0"

    data_dir: str = "data"  # root
    raw_dir: str = "data/raw"  # downloaded filing here
    meta_dir: str = "data/meta"  # ticker maps, small caches, etc.
    out_dir: str = "out"  # final JSON/CSV/MD

    user_agent: str = "sec-sum/0.1 (+cmoliv17@mit.edu)"
    rps_limit: float = 5.0
    http_timeout_s: float = 15.0
    retry_max_attempts: int = 5  # for 5xx/429 errors
    retry_backoff_base_s: float = 0.5  # exponential backoff base

    sec_submissions_base: str = "https://data.sec.gov/submissions"
    sec_archives_base: str = "https://www.sec.gov/Archives/edgar/data"

    default_forms: tuple[str, ...] = ("10-K", "10-Q")
    include_amendments_default: bool = False  # exclude 10-K/A, 10-Q/A by default

    submissions_ttl_s: int = 24 * 60 * 60  # 1 day
    docs_ttl_s: int = 30 * 24 * 60 * 60  # 30 days

    log_level: str = "INFO"


CONFIG = AppConfig()
