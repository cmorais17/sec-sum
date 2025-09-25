from collections.abc import Iterable

from .models import FilingKey


def filter_forms(rows: Iterable[FilingKey], forms: list[str]) -> list[FilingKey]:
    """Keep only requested forms (case-insensitive)."""
    raise NotImplementedError


def exclude_amendments(rows: Iterable[FilingKey]) -> list[FilingKey]:
    """Drop forms ending in '/A' e.g. '10-K/A'."""
    raise NotImplementedError


def take_limit(rows: Iterable[FilingKey], n: int) -> list[FilingKey]:
    """First n rows in original order."""
    raise NotImplementedError
