import json
import os
from pathlib import Path
from typing import Any

from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

SECTION_LABELS = {
    "item_1": "Item 1",
    "item_1a": "Item 1A",
    "item_2": "Item 2",
    "item_3": "Item 3",
    "item_4": "Item 4",
    "item_7": "Item 7",
    "item_7a": "Item 7A",
    "item_9a": "Item 9A",
}


def build_messages(
    meta: dict[str, Any], sections: dict[str, str]
) -> list[ChatCompletionMessageParam]:
    header = (
        f"CIK: {meta.get('cik10', '')}, "
        f"Form: {meta.get('form', '')}, "
        f"Filing date: {meta.get('filing_date', '')}"
    ).strip(", ")

    combined = []

    combined.append(f"Metadata:\n{header}\n")
    combined.append(
        "Write a structured Markdown summary:\n"
        "1. Overall snapshot (2-3 paragraphs)\n"
        "2. Key risks (bullet list, based on Item 1A)\n"
        "3. Business overview (based on Item 1)\n"
        "4. MD&A highlights (based on Item 2 or 7)\n"
        "5. Market risk and controls (based on Items 3, 7A, 4, 9A)\n\n"
        "Do NOT ask for more content. All sections you need are already provided below.\n"
        "If something is missing, state that briefly.\n"
    )

    for key, label in SECTION_LABELS.items():
        if key not in sections:
            continue
        text = sections[key]
        combined.append(f"\n\n### {label}\n{text}")

    full_text = "\n".join(combined)

    return [
        {
            "role": "system",
            "content": (
                "You are a senior equity analyst. "
                "Write precise, concise, investor-grade summaries of SEC filings."
            ),
        },
        {
            "role": "user",
            "content": full_text,
        },
    ]


def summarize_parsed_file(
    input_path: Path,
    out_dir: Path,
    model: str = "gpt-5-mini",
) -> Path:
    raw = json.loads(input_path.read_text(encoding="utf-8"))
    meta = raw.get("meta", {})
    sections = raw.get("sections", {})

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY environment variable is not set")

    client = OpenAI(api_key=api_key)

    messages = build_messages(meta, sections)

    resp = client.chat.completions.create(
        model=model,
        messages=messages,
    )

    content = resp.choices[0].message.content or ""
    out_dir.mkdir(parents=True, exist_ok=True)

    base = meta.get("accession_nodash") or input_path.stem
    out_path = out_dir / f"{base}.summary.md"
    out_path.write_text(content, encoding="utf-8")

    return out_path
