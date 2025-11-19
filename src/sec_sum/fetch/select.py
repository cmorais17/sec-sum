from collections.abc import Iterable

from .models import FilingKey


def filter_forms(rows: Iterable[FilingKey], forms: list[str]) -> list[FilingKey]:
    """Keep only requested forms (case-insensitive)."""
    wanted = {f.strip().upper() for f in forms if f.strip()}
    if not wanted:
        return list(rows)

    kept: list[FilingKey] = []
    for r in rows:
        f_upper = r.form.upper()
        base = f_upper[:-2] if f_upper.endswith("/A") else f_upper
        if f_upper in wanted or base in wanted:
            kept.append(r)
    return kept


def exclude_amendments(rows: Iterable[FilingKey]) -> list[FilingKey]:
    """Drop forms ending in '/A' e.g. '10-K/A'."""
    return [r for r in rows if not r.form.upper().endswith("/A")]


def take_limit(rows: Iterable[FilingKey], n: int) -> list[FilingKey]:
    """First n rows in original order."""
    if n <= 0:
        return []

    out: list[FilingKey] = []
    for r in rows:
        out.append(r)
        if len(out) >= n:
            break
    return out
