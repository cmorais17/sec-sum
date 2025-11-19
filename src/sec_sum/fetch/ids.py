import json
from pathlib import Path

import requests

from .models import CompanyId

SEC_TICKER_URL = "https://www.sec.gov/files/company_tickers.json"
TICKER_CACHE_PATH = Path("data/meta/ticker_map.json")


def normalize_ticker(t: str) -> str:
    """Return uppercase, strip spaces; error if invalid chars."""
    ticker = t.strip().upper()
    if not ticker:
        raise ValueError("Ticker must be non-empty")

    for ch in ticker:
        if not (ch.isalnum() or ch in {".", "-"}):
            raise ValueError(f"Invalid character {ch!r} in ticker {t!r}")

    return ticker


def normalize_cik_to_10(cik: str) -> str:
    """Digits-only; left-pad with zeros to length 10; validate length."""
    digits = "".join(ch for ch in cik if ch.isdigit())
    if not digits:
        raise ValueError(f"Invalid CIK: {cik!r}")
    if len(digits) > 10:
        raise ValueError(f"CIK too long {digits!r}")
    return digits.zfill(10)


def load_ticker_map(cache_path: str | Path = TICKER_CACHE_PATH) -> dict[str, str]:
    """Return {TICKER -> CIK(plain)}, cached locally; If missing, download, process, and write it"""
    path = Path(cache_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            return {str(k).upper(): str(v) for k, v in data.items()}
        raise RuntimeError(f"Unexpected format in ticker cache {path}")

    # Missing
    resp = requests.get(
        SEC_TICKER_URL,
        headers={
            "User-Agent": "sec-sum/0.1 (carlos8cadu@gmail.com)",
            "Accept-Encoding": "gzip, deflate",
        },
        timeout=15,
    )
    resp.raise_for_status()
    raw = resp.json()

    mapping: dict[str, str] = {}
    for entry in raw.values():
        ticker = str(entry["ticker"]).upper()
        cik_str = str(entry["cik_str"])
        mapping[ticker] = cik_str

    path.write_text(json.dumps(mapping, indent=2), encoding="utf-8")
    return mapping


def resolve_company_id(user_input: str) -> CompanyId:
    """If looks like ticker -> map to CIK; else treat as cik; return CompanyId."""
    s = user_input.strip()
    if not s:
        raise ValueError("Identifier must be non-empty")

    # Just digits -> CIK
    if s.isdigit():
        cik10 = normalize_cik_to_10(s)
        return CompanyId(ticker=None, cik10=cik10)

    # ticker -> get CIK
    ticker = normalize_ticker(s)
    mapping = load_ticker_map()
    if ticker not in mapping:
        raise ValueError(f"Ticker {ticker!r} not found in SEC ticker map")

    cik_plain = mapping[ticker]
    cik10 = normalize_cik_to_10(cik_plain)
    return CompanyId(ticker=ticker, cik10=cik10)
