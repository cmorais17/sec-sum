from collections.abc import Mapping


class HttpClient:
    def __init__(self, user_agent: str, cache_name: str, rps_limit: float = 5.0):
        """
        Configure requests Session:
            - default headers with UA + Accept-Encoding
            - requests-cache with sane TTLs
            - tenacity retry for 5xx/429
            - simple token-bucket rate limiter targeting rps_limit
        """
        raise NotImplementedError

    def get(
        self, url: str, *, params: Mapping[str, str] | None = None, timeout_s: float = 15.0
    ) -> tuple[int, bytes, Mapping[str, str]]:
        """Return (status_code, content_bytes, headers)."""
        raise NotImplementedError
