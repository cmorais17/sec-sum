from pathlib import Path

from sec_sum.fetch.fetcher import fetch_pipeline
from sec_sum.fetch.ids import resolve_company_id
from sec_sum.fetch.net import HttpClient
from sec_sum.parse_core import parse_filing
from sec_sum.summarizer import summarize_parsed_file


def run_pipeline(
    *,
    ticker_or_cik: str,
    forms: list[str],
    limit: int,
    data_root: str,
    out_dir: str,
    model: str,
    user_agent: str,
    cache_name: str = "sec-sum",
    rps_limit: float = 5.0,
    timeout_s: float = 10.0,
    include_amendments: bool = False,
) -> list[Path]:
    http = HttpClient(
        user_agent=user_agent,
        cache_name=cache_name,
        rps_limit=rps_limit,
        timeout_s=timeout_s,
    )

    company = resolve_company_id(ticker_or_cik)
    manifests = fetch_pipeline(
        http=http,
        company=company,
        forms=forms,
        limit=limit,
        data_root=data_root,
        include_amendments=include_amendments,
    )

    out_paths: list[Path] = []
    for m in manifests:
        parsed_path = parse_filing(
            accession=m.filing.accession,
            path=None,
            data_root=data_root,
            out_dir=out_dir,
        )
        summary_path = summarize_parsed_file(
            input_path=parsed_path,
            out_dir=Path(out_dir),
            model=model,
        )
        out_paths.append(summary_path)

    return out_paths
