from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

from .manager import ConfigManager

load_dotenv()


@dataclass(frozen=True)
class Settings:
    gemini_api_key: str
    gdelt_api_key: str | None
    gemini_model: str


def get_settings() -> Settings:
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not set. Please create a .env with GEMINI_API_KEY=<your_key>."
        )
    gdelt_api_key = os.getenv("GDELT_API_KEY") or None
    cfg = ConfigManager().config
    return Settings(
        gemini_api_key=gemini_api_key,
        gdelt_api_key=gdelt_api_key,
        gemini_model=cfg.gemini.model,
    )
