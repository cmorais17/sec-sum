from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AppConfig:
    app_name: str = "sec-sum"
    data_dir: str = "data"
    out_dir: str = "out"
    user_agent: str = "sec-sum/0.1 (+cmoliv17@mit.edu)"


CONFIG = AppConfig()
