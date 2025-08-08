"""YAML-backed configuration manager.

Loads typed configuration from YAML files with environment-aware overrides.
API keys remain sourced from environment variables (via `.env`).
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

from .config_schemas import GDELTConfig, GeminiConfig, ProjectConfig

DEFAULT_CONFIG_FILENAMES = (
    "world_news.yaml",
    "world-news.yaml",
    "config.yaml",
)


class ConfigManager:
    """Load and provide typed access to project configuration.

    The manager searches for a YAML config file in the provided directory (or
    current working directory by default). Missing fields fall back to defaults
    defined in dataclasses.
    """

    def __init__(self, root_dir: str | Path | None = None) -> None:
        self.root_dir = Path(root_dir or os.getcwd())
        self._config = self._load_config()

    @property
    def config(self) -> ProjectConfig:
        """Return the loaded configuration as a typed dataclass instance."""

        return self._config

    def _load_config(self) -> ProjectConfig:
        data: dict[str, Any] = {}
        path = self._find_config_file()
        if path is not None and path.exists():
            with path.open("r", encoding="utf-8") as fp:
                raw = yaml.safe_load(fp) or {}
            data = self._normalize(raw)
        return self._from_dict(data)

    def _find_config_file(self) -> Path | None:
        for name in DEFAULT_CONFIG_FILENAMES:
            candidate = self.root_dir / name
            if candidate.exists():
                return candidate
        return None

    def _normalize(self, raw: dict[str, Any]) -> dict[str, Any]:
        # Support simple top-level keys with minimal nesting.
        result: dict[str, Any] = {}
        if not isinstance(raw, dict):
            return result
        # Only pick known sections
        if "gemini" in raw and isinstance(raw["gemini"], dict):
            result["gemini"] = {"model": raw["gemini"].get("model")}
        if "gdelt" in raw and isinstance(raw["gdelt"], dict):
            result["gdelt"] = {"endpoint": raw["gdelt"].get("endpoint")}
        return result

    def _from_dict(self, data: dict[str, Any]) -> ProjectConfig:
        gemini = GeminiConfig(
            **{k: v for k, v in (data.get("gemini") or {}).items() if v is not None}
        )
        gdelt = GDELTConfig(**{k: v for k, v in (data.get("gdelt") or {}).items() if v is not None})
        return ProjectConfig(gemini=gemini, gdelt=gdelt)
