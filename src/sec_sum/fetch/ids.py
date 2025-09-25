from .models import CompanyId


def normalize_ticker(t: str) -> str:
    """Return uppercase, strip spaces; error if invalid chars."""
    raise NotImplementedError


def normalize_cik_to_10(cik: str) -> str:
    """Digits-only; left-pad with zeros to length 10; validate length."""
    raise NotImplementedError


def load_ticker_map(cache_path: str) -> dict[str, str]:
    """Return {TICKER -> CIK(plain)}, cached locally; raise if missing"""
    raise NotImplementedError


def resolve_company_id(user_input: str) -> CompanyId:
    """If looks like ticker -> map to CIK; else treat as cik; return CompanyId."""
    raise NotImplementedError
