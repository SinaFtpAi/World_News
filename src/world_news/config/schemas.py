from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GeminiConfig:
    model: str = "gemini-2.5-flash"


@dataclass(frozen=True)
class GDELTConfig:
    endpoint: str | None = None


@dataclass(frozen=True)
class ProjectConfig:
    gemini: GeminiConfig = GeminiConfig()
    gdelt: GDELTConfig = GDELTConfig()
