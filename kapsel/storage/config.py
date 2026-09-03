"""
Kapsel configuration loader and generator.
Manages ~/.kapsel/config.yaml.
"""

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict
import yaml

from kapsel.storage.logger import get_kapsel_dir, logger

DEFAULT_CONFIG: Dict[str, Any] = {
    "version": "1.0",
    "theme": {
        "name": "cyber_dark",
        "primary": "#00f0ff",      # Cyan accent
        "secondary": "#7928ca",    # Purple accent
        "success": "#00e676",      # Emerald green
        "warning": "#ffab00",      # Amber
        "error": "#ff1744",        # Neon red
        "dim": "#666666",          # Dark gray
        "background": "#121214",
        "foreground": "#e1e1e6",
    },
    "ui": {
        "enable_banner": True,
        "enable_timing": True,
        "enable_autosuggest": True,
        "enable_card_border": True,
        "show_git_branch": True,
        "show_shell_badge": True,
        "show_timestamp": True,
        "prompt_symbols": {
            "top": "╭─",
            "bottom": "╰─",
            "arrow": "❯",
            "capsule": "💊",
            "branch": "",
            "folder": "📁",
            "success": "✔",
            "failure": "✘",
            "clock": "⏱",
        },
    },
    "routing": {
        "prefer_modern_tools": True,  # e.g., eza/bat/rg if available
        "default_fallback_shell": "unix",
    },
}


@dataclass
class KapselConfig:
    raw: Dict[str, Any] = field(default_factory=lambda: DEFAULT_CONFIG.copy())

    @property
    def theme(self) -> Dict[str, str]:
        return self.raw.get("theme", DEFAULT_CONFIG["theme"])

    @property
    def ui(self) -> Dict[str, Any]:
        return self.raw.get("ui", DEFAULT_CONFIG["ui"])

    @property
    def symbols(self) -> Dict[str, str]:
        return self.ui.get("prompt_symbols", DEFAULT_CONFIG["ui"]["prompt_symbols"])

    @property
    def enable_banner(self) -> bool:
        return self.ui.get("enable_banner", True)

    @property
    def enable_timing(self) -> bool:
        return self.ui.get("enable_timing", True)

    @property
    def enable_autosuggest(self) -> bool:
        return self.ui.get("enable_autosuggest", True)

    @property
    def enable_card_border(self) -> bool:
        return self.ui.get("enable_card_border", True)


def get_config_path() -> Path:
    return get_kapsel_dir() / "config.yaml"


def load_config() -> KapselConfig:
    """Load config.yaml from sandbox directory or generate with default values."""
    config_path = get_config_path()
    if not config_path.exists():
        save_default_config(config_path)
        return KapselConfig(DEFAULT_CONFIG)

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        # Merge with defaults for missing keys
        merged = DEFAULT_CONFIG.copy()
        _deep_merge(merged, data)
        return KapselConfig(merged)
    except Exception as e:
        logger.error(f"Failed to load config from {config_path}: {e}")
        return KapselConfig(DEFAULT_CONFIG)


def save_default_config(path: Path) -> None:
    """Save default config to the given path."""
    try:
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(DEFAULT_CONFIG, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        logger.info(f"Initialized default config at {path}")
    except Exception as e:
        logger.error(f"Failed to write default config: {e}")


def _deep_merge(source: Dict[str, Any], destination: Dict[str, Any]) -> Dict[str, Any]:
    for k, v in destination.items():
        if isinstance(v, dict) and k in source and isinstance(source[k], dict):
            _deep_merge(source[k], v)
        else:
            source[k] = v
    return source
