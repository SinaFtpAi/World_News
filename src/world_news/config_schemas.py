"""Typed configuration schemas for YAML-based configs.

These mirror the structure of YAML files loaded by the ConfigManager.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GeminiConfig:
    """Gemini model configuration.

    Attributes:
        model: Gemini model name (e.g., ``gemini-2.5-flash``).
    """

    model: str = "gemini-2.5-flash"


@dataclass(frozen=True)
class GDELTConfig:
    """GDELT configuration.

    Attributes:
        endpoint: Optional custom endpoint; typically not needed.
    """

    endpoint: str | None = None


@dataclass(frozen=True)
class ProjectConfig:
    """Top-level project configuration.

    Attributes:
        gemini: Gemini configuration.
        gdelt: GDELT configuration.
    """

    gemini: GeminiConfig = GeminiConfig()
    gdelt: GDELTConfig = GDELTConfig()
