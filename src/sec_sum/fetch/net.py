from collections.abc import Mapping
import time
from typing import Final, cast

import requests


class HttpError(RuntimeError):
    """Raised when HTTP request return a 4xx/5xx status"""

    def __init__(self, url: str, status_code: int, body_preview: str):
        super().__init__(f"HTTP {status_code} for {url}: {body_preview}")
        self.url = url
        self.status_code = status_code
        self.body_preview = body_preview


class HttpClient:
    def __init__(
        self, user_agent: str, cache_name: str, rps_limit: float = 5.0, timeout_s: float = 10.0
    ):
        """
        Configure requests Session:
            - default headers with UA + Accept-Encoding
            - simple rate limiter targeting rps_limit
        """
        self._session = requests.Session()
        self._session.headers.update(
            {
                "User-Agent": user_agent,
                "Accept-Encoding": "gzip, deflate",
            }
        )
        self._timeout_s: Final = timeout_s

        self._min_interval: Final = 1.0 / rps_limit if rps_limit > 0 else 0.0
        self._last_request_ts: float | None = None

    @property
    def user_agent(self) -> str:
        ua = self._session.headers.get("User-Agent", "")
        if isinstance(ua, bytes):
            ua = ua.decode("utf-8", errors="ignore")
        return cast(str, ua)

    def _respect_rate_limit(self) -> None:
        if self._min_interval <= 0:
            return
        now = time.monotonic()
        if self._last_request_ts is None:
            self._last_request_ts = now
            return
        elapsed = now - self._last_request_ts
        if elapsed < self._min_interval:
            time.sleep(self._min_interval - elapsed)
        self._last_request_ts = time.monotonic()

    def get(
        self, url: str, *, params: Mapping[str, str] | None = None, timeout_s: float = 15.0
    ) -> tuple[int, bytes, Mapping[str, str]]:
        """Return (status_code, content_bytes, headers). Raise HttpError on 4xx/5xx"""
        self._respect_rate_limit()
        try:
            resp = self._session.get(
                url,
                params=params,
                timeout=timeout_s or self._timeout_s,
            )
        except requests.RequestException as exc:
            raise RuntimeError(f"Request to {url!r} failed: {exc}") from exc

        if resp.status_code >= 400:
            try:
                preview = resp.text[:200]
            except Exception:
                preview = "<non-text body>"
            raise HttpError(url, resp.status_code, preview)

        return resp.status_code, resp.content, resp.headers
