"""
Kapsel Internationalization (i18n) Core Engine.
Provides lightweight, zero-dependency localization across seven major languages:
- English (en - default)
- Simplified Chinese (zh_CN)
- Japanese (ja)
- Spanish (es)
- French (fr)
- German (de)
- Russian (ru)

All comments and descriptions are in English.
"""

from functools import lru_cache
import locale
import os
from pathlib import Path
import sys
from typing import Any, Dict, List, Optional, Tuple
import yaml

from kapsel.storage.logger import logger

# Supported world languages with metadata and common CLI shorthand aliases
SUPPORTED_LANGUAGES: Dict[str, Dict[str, Any]] = {
    "en": {
        "name": "English",
        "native": "English",
        "aliases": ["en_us", "en_gb", "english"],
    },
    "zh_CN": {
        "name": "Chinese (Simplified)",
        "native": "简体中文",
        "aliases": ["zh", "cn", "zh_hans", "chinese"],
    },
    "ja": {
        "name": "Japanese",
        "native": "日本語",
        "aliases": ["jp", "japanese"],
    },
    "es": {
        "name": "Spanish",
        "native": "Español",
        "aliases": ["es_es", "spanish"],
    },
    "fr": {
        "name": "French",
        "native": "Français",
        "aliases": ["fr_fr", "french"],
    },
    "de": {
        "name": "German",
        "native": "Deutsch",
        "aliases": ["de_de", "german"],
    },
    "ru": {
        "name": "Russian",
        "native": "Русский",
        "aliases": ["ru_ru", "russian"],
    },
}

DEFAULT_LANGUAGE = "en"

# In-memory runtime language override (None means defer to config/system)
_CURRENT_LANGUAGE_OVERRIDE: Optional[str] = None

# Cache for loaded YAML locale datasets
_LOCALE_CACHE: Dict[Tuple[str, str], Dict[str, Any]] = {}


class SafeFormatDict(dict):
    """Dictionary that leaves unmatched format keys intact instead of raising KeyError."""
    def __missing__(self, key: str) -> str:
        return "{" + key + "}"


def normalize_language_code(raw_input: Optional[str]) -> Optional[str]:
    """
    Normalizes user-supplied or OS-provided language string into standard Kapsel language code.
    E.g.: 'zh' -> 'zh_CN', 'jp' -> 'ja', 'en-US' -> 'en', 'spanish' -> 'es'.
    """
    if not raw_input:
        return None

    cleaned = raw_input.strip().lower().replace("-", "_")

    # Direct match
    for code in SUPPORTED_LANGUAGES:
        if cleaned == code.lower():
            return code

    # Match aliases
    for code, meta in SUPPORTED_LANGUAGES.items():
        aliases = [a.lower() for a in meta.get("aliases", [])]
        if cleaned in aliases:
            return code
        # Check prefix match (e.g. 'zh_hk', 'zh_tw' fallback to zh_CN)
        if cleaned.startswith(code.lower() + "_") or cleaned.startswith(code.lower()):
            return code

    return None


def detect_system_language() -> str:
    """Detects host operating system language, mapping to closest supported language code."""
    try:
        # Check environment variables first (common in POSIX and modern terminals)
        for env_var in ("LC_ALL", "LC_MESSAGES", "LANG"):
            val = os.environ.get(env_var)
            if val:
                matched = normalize_language_code(val.split(".")[0])
                if matched:
                    return matched

        # Use Python standard locale library
        loc_tuple = locale.getdefaultlocale()
        if loc_tuple and loc_tuple[0]:
            matched = normalize_language_code(loc_tuple[0])
            if matched:
                return matched
    except Exception:
        pass

    return DEFAULT_LANGUAGE


def get_current_language() -> str:
    """
    Resolves active language code following priority hierarchy:
    1. Runtime in-memory override (e.g. during session or unit testing)
    2. User configuration ~/.kapsel/config.yaml ('language' field)
    3. Host OS detection (if config is 'auto' or unset)
    4. Fallback default ('en')
    """
    global _CURRENT_LANGUAGE_OVERRIDE
    if _CURRENT_LANGUAGE_OVERRIDE:
        return _CURRENT_LANGUAGE_OVERRIDE

    try:
        from kapsel.storage.config import load_config
        cfg = load_config()
        configured_lang = getattr(cfg, "language", None) or cfg.raw.get("language")

        if configured_lang and configured_lang.lower() != "auto":
            normalized = normalize_language_code(str(configured_lang))
            if normalized:
                return normalized
    except Exception:
        pass

    return detect_system_language()


def set_current_language(lang_input: str, persist: bool = True) -> bool:
    """
    Sets the active language code.
    If persist=True, writes the updated setting to ~/.kapsel/config.yaml.
    """
    global _CURRENT_LANGUAGE_OVERRIDE
    normalized = normalize_language_code(lang_input)
    if not normalized:
        return False

    _CURRENT_LANGUAGE_OVERRIDE = normalized

    if persist:
        try:
            from kapsel.storage.config import update_config_value
            update_config_value("language", normalized)
        except Exception as e:
            logger.warning(f"Could not persist language setting to config.yaml: {e}")

    return True


def get_locales_dir() -> Path:
    """Returns absolute path to the package's locales directory."""
    return Path(__file__).resolve().parent.parent / "locales"


def load_locale_file(namespace: str, lang: Optional[str] = None) -> Dict[str, Any]:
    """
    Loads a structured YAML locale file for given namespace ('help', 'messages', etc.).
    Falls back to 'en' (default) if the specified language file does not exist.
    """
    target_lang = lang or get_current_language()
    cache_key = (namespace, target_lang)

    if cache_key in _LOCALE_CACHE:
        return _LOCALE_CACHE[cache_key]

    locales_dir = get_locales_dir()
    primary_path = locales_dir / target_lang / f"{namespace}.yaml"
    fallback_path = locales_dir / DEFAULT_LANGUAGE / f"{namespace}.yaml"

    data: Dict[str, Any] = {}

    if primary_path.exists():
        try:
            with open(primary_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
        except Exception as e:
            logger.error(f"Failed to load locale file {primary_path}: {e}")

    # Fallback to English if primary file missing or empty
    if not data and target_lang != DEFAULT_LANGUAGE and fallback_path.exists():
        try:
            with open(fallback_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
        except Exception as e:
            logger.error(f"Failed to load fallback locale file {fallback_path}: {e}")

    _LOCALE_CACHE[cache_key] = data
    return data


def clear_locale_cache() -> None:
    """Clears cached locale datasets from memory (useful on hot-reloading)."""
    global _LOCALE_CACHE
    _LOCALE_CACHE.clear()


def get_text(
    key: str,
    default: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: Any,
) -> str:
    """
    Main translation retrieval function.
    Supports dot-notation keys (e.g. 'ui.status.platform').
    Safely interpolates named keyword arguments (e.g. cmd='help') without risking command corruption.
    """
    target_lang = lang or get_current_language()
    messages = load_locale_file("messages", target_lang)

    # Resolve dot notation
    keys = key.split(".")
    curr: Any = messages
    for k in keys:
        if isinstance(curr, dict) and k in curr:
            curr = curr[k]
        else:
            curr = None
            break

    # If missing in primary language, try fallback English
    if curr is None and target_lang != DEFAULT_LANGUAGE:
        en_messages = load_locale_file("messages", DEFAULT_LANGUAGE)
        curr = en_messages
        for k in keys:
            if isinstance(curr, dict) and k in curr:
                curr = curr[k]
            else:
                curr = None
                break

    resolved_text = curr if isinstance(curr, str) else (default or key)

    if kwargs and "{" in resolved_text:
        try:
            resolved_text = resolved_text.format_map(SafeFormatDict(kwargs))
        except Exception:
            pass

    return resolved_text


# Convenient standard i18n alias
_ = get_text
