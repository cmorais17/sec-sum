import json
from pathlib import Path
import re
from typing import Any
import warnings

from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning

from sec_sum.fetch.models import Manifest
from sec_sum.fetch.storage import read_manifest

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

_ITEM_KEYS: dict[str, str] = {
    "1": "item_1",
    "1A": "item_1a",
    "2": "item_2",
    "3": "item_3",
    "4": "item_4",
    "7": "item_7",
    "7A": "item_7a",
    "9A": "item_9a",
}

_ITEM_HEADING_RE = re.compile(r"ITEM\s+(\d+[A-Z]?)\.", flags=re.IGNORECASE)


def _normalize_paragraphs(content: str) -> str:
    content = content.replace("\r\n", "\n").replace("\r", "\n")
    content = re.sub(r"\n{3,}", "\n\n", content)
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in content.split("\n")]
    while lines and not lines[0]:
        lines.pop(0)
    while lines and not lines[-1]:
        lines.pop()
    return "\n".join(lines)


def _extract_sections_from_html_text(text: str) -> dict[str, str]:
    sections: dict[str, str] = {}
    upper = text.upper()
    matches = list(_ITEM_HEADING_RE.finditer(upper))
    if not matches:
        return sections

    all_items = []
    for m in matches:
        item_label = m.group(1).upper()
        all_items.append((item_label, m.start()))

    all_items_sorted = sorted(all_items, key=lambda kv: kv[1])

    ordered_boundaries: list[tuple[str, int, int]] = []
    for i, (label, start) in enumerate(all_items_sorted):
        end = all_items_sorted[i + 1][1] if i + 1 < len(all_items_sorted) else len(text)
        ordered_boundaries.append((label, start, end))

    for label, start, end in ordered_boundaries:
        if label not in _ITEM_KEYS:
            continue
        raw_section = text[start:end]
        heading_re = re.compile(rf"ITEM\s+{re.escape(label)}\.", flags=re.IGNORECASE)
        m_head = heading_re.search(raw_section)

        content = raw_section[m_head.end() :] if m_head else raw_section

        cleaned = _normalize_paragraphs(content)
        if cleaned:
            key = _ITEM_KEYS[label]
            sections[key] = cleaned

    return sections


def extract_sections_from_html_file(html_path: Path) -> dict[str, str]:
    html = html_path.read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(html, "lxml")
    text = soup.get_text("\n")
    return _extract_sections_from_html_text(text)


def _find_filing_by_accession(accession: str, data_root: Path) -> tuple[Manifest, Path]:
    acc_nodash = accession.replace("-", "")
    root = data_root

    for cik_dir in root.iterdir():
        if not cik_dir.is_dir():
            continue
        candidate = cik_dir / acc_nodash
        mpath = candidate / "manifest.json"
        if mpath.exists():
            manifest = read_manifest(mpath)
            primary = candidate / manifest.filing.primary_document
            if not primary.exists():
                raise FileNotFoundError(
                    f"Primary document {primary} from manifest not found on disk"
                )
            return manifest, primary
    raise FileNotFoundError(
        f"No filing directory found for accession {accession!r} under {data_root}"
    )


def parse_filing(
    *,
    accession: str | None,
    path: str | None,
    data_root: str = "data",
    out_dir: str = "out",
) -> Path:
    data_root_path = Path(data_root)
    out_root = Path(out_dir)
    out_root.mkdir(parents=True, exist_ok=True)

    manifest: Manifest | None = None
    html_path: Path

    if path:
        html_path = Path(path)
        if not html_path.exists():
            raise FileNotFoundError(f"HTML file {html_path!r} does not exist")
    elif accession:
        manifest, html_path = _find_filing_by_accession(accession, data_root_path)
    else:
        raise ValueError("Either accession or path must be provided")

    sections = extract_sections_from_html_file(html_path)

    meta: dict[str, Any] = {"source_path": str(html_path)}

    if manifest is not None:
        meta.update(
            {
                "accession": manifest.filing.accession,
                "accession_nodash": manifest.filing.accession_nodash,
                "cik10": manifest.filing.cik10,
                "form": manifest.filing.form,
                "filing_date": manifest.filing.filing_date,
                "report_period": manifest.filing.report_period,
            }
        )
        out_name = f"{manifest.filing.cik10}_{manifest.filing.accession_nodash}.json"
    else:
        out_name = html_path.stem + ".parsed.json"

    out_path = out_root / out_name
    payload = {"meta": meta, "sections": sections}

    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return out_path
