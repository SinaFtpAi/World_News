from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .schemas import GDELTConfig, GeminiConfig, ProjectConfig

DEFAULT_CONFIG_FILENAMES = (
    "world_news.yaml",
    "world-news.yaml",
    "config.yaml",
)

DEFAULT_CONFIG_DIRS = (
    Path.cwd(),
    Path.cwd() / "configs",
)


class ConfigManager:
    def __init__(self, search_dirs: tuple[Path, ...] | None = None) -> None:
        self.search_dirs = search_dirs or DEFAULT_CONFIG_DIRS
        self._config = self._load_config()

    @property
    def config(self) -> ProjectConfig:
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
        for directory in self.search_dirs:
            for name in DEFAULT_CONFIG_FILENAMES:
                candidate = directory / name
                if candidate.exists():
                    return candidate
        return None

    def _normalize(self, raw: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(raw, dict):
            return {}
        result: dict[str, Any] = {}
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
