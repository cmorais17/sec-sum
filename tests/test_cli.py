from sec_sum.cli import main


def test_fetch_stub_returns_zero() -> None:
    assert main(["fetch", "--ticker", "AAPL"]) == 0
