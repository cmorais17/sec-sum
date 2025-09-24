from __future__ import annotations

import argparse
from collections.abc import Callable
from typing import cast

Command = Callable[[argparse.Namespace], int]


def _cmd_fetch(args: argparse.Namespace) -> int:
    # Implement ticker -> CIK -> filings lookup + caching
    print(f"[fetch] ticker={args.ticker} forms={args.forms} limit={args.limit}")
    return 0


def _cmd_parse(args: argparse.Namespace) -> int:
    # Parse HTML/iXBRL into structured data
    print(f"[parse] accession={args.accession} path={args.path}")
    return 0


def _cmd_summarize(args: argparse.Namespace) -> int:
    # Summarization + JSON/CSV/MD outputs
    print(f"[summarize] input={args.input} outdir={args.outdir}")
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
