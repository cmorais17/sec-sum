from __future__ import annotations

import argparse
from collections.abc import Callable
import os
from pathlib import Path
from typing import cast

from sec_sum.fetch.fetcher import fetch_pipeline
from sec_sum.fetch.ids import resolve_company_id
from sec_sum.fetch.net import HttpClient
from sec_sum.parse_core import parse_filing
from sec_sum.summarizer import summarize_parsed_file


def _load_local_env() -> None:
    env_path = Path(__file__).resolve().parents[2] / ".env.local"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :].strip()
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


_load_local_env()

Command = Callable[[argparse.Namespace], int]


def _cmd_fetch(args: argparse.Namespace) -> int:
    forms = [s.strip().upper() for s in args.forms.split(",") if s.strip()]
    if not forms:
        raise SystemExit("At least one form must be specified (e.g. 10-K, 10-Q)")

    http = HttpClient(
        user_agent="sec-sum/0.1 (carlos8cadu@gmail.com)",
        cache_name="sec-sum",
        rps_limit=5.0,
        timeout_s=10.0,
    )

    company = resolve_company_id(args.ticker)

    manifests = fetch_pipeline(
        http=http,
        company=company,
        forms=forms,
        limit=args.limit,
        data_root="data",
        include_amendments=False,
    )

    label = company.ticker or company.cik10
    print(f"Fetched {len(manifests)} filings for {label}")
    for m in manifests:
        f = m.filing
        print(f"- {f.form} {f.filing_date} {f.accession}")
    return 0


def _cmd_parse(args: argparse.Namespace) -> int:
    # Parse accession or path
    accession = args.accession
    path = args.path

    if not accession and not path:
        raise SystemExit("You must provide either --accession or --path to parse")

    out_path = parse_filing(
        accession=accession,
        path=path,
        data_root="data",
        out_dir="out",
    )
    print(f"Parsed filing written to {out_path}")
    return 0


def _cmd_summarize(args: argparse.Namespace) -> int:
    # Summarization + MD output
    input_path = Path(args.input)
    out_dir = Path(args.outdir)

    if not input_path.exists():
        raise SystemExit(f"Input file {input_path!r} does not exist")

    out_path = summarize_parsed_file(input_path=input_path, out_dir=out_dir)
    print(f"Summary written to {out_path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="sec-sum", description="SEC filing summarizer")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_fetch = sub.add_parser("fetch", help="Fetch recent filings for a ticker/CIK")
    p_fetch.add_argument("--ticker", type=str, required=True)
    p_fetch.add_argument("--forms", type=str, default="10-K,10-Q")
    p_fetch.add_argument("--limit", type=int, default=4)
    p_fetch.set_defaults(func=_cmd_fetch)

    p_parse = sub.add_parser("parse", help="Parse a downloaded filing")
    p_parse.add_argument("--accession", type=str)
    p_parse.add_argument("--path", type=str)
    p_parse.set_defaults(func=_cmd_parse)

    p_sum = sub.add_parser("summarize", help="Summarize parsed data")
    p_sum.add_argument("--input", type=str, required=True)
    p_sum.add_argument("--outdir", type=str, default="out")
    p_sum.set_defaults(func=_cmd_summarize)

    args = p.parse_args(argv)

    handler = cast(Command, args.func)
    return handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
