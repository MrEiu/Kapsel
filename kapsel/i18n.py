"""
Kapsel Internationalization (i18n) Engine.
Powered by Python standard gettext and Babel.
Supports 7 major world languages:
- en: English (default)
- zh_CN: Simplified Chinese
- ja: Japanese
- es: Spanish
- fr: French
- de: German
- ru: Russian
"""

import gettext
import locale
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

SUPPORTED_LANGUAGES: Dict[str, Dict[str, Any]] = {
    "en": {
        "name": "English",
        "native": "English",
        "aliases": ["en_us", "english"],
    },
    "zh_CN": {
        "name": "Chinese (Simplified)",
        "native": "简体中文",
        "aliases": ["zh", "cn", "chinese"],
    },
    "ja": {
        "name": "Japanese",
        "native": "日本語",
        "aliases": ["jp", "japanese"],
    },
    "es": {
        "name": "Spanish",
        "native": "Español",
        "aliases": ["spanish"],
    },
    "fr": {
        "name": "French",
        "native": "Français",
        "aliases": ["french"],
    },
    "de": {
        "name": "German",
        "native": "Deutsch",
        "aliases": ["german"],
    },
    "ru": {
        "name": "Russian",
        "native": "Русский",
        "aliases": ["russian"],
    },
}

DEFAULT_LANGUAGE = "en"
DOMAIN = "kapsel"

_CURRENT_LANGUAGE_OVERRIDE: Optional[str] = None
_TRANSLATION_CACHE: Dict[str, gettext.NullTranslations] = {}


def get_locales_dir() -> Path:
    """Returns absolute path to locales directory."""
    return Path(__file__).resolve().parent / "locales"


def normalize_language_code(raw: Optional[str]) -> Optional[str]:
    """Normalizes raw user or OS language string into standard Kapsel code."""
    if not raw:
        return None
    cleaned = raw.strip().lower().replace("-", "_")
    for code in SUPPORTED_LANGUAGES:
        if cleaned == code.lower():
            return code
    for code, meta in SUPPORTED_LANGUAGES.items():
        if cleaned in [a.lower() for a in meta.get("aliases", [])]:
            return code
        if cleaned.startswith(code.lower() + "_") or cleaned.startswith(code.lower()):
            return code
    return None


def detect_system_language() -> str:
    """Detects host operating system language."""
    for var in ("LC_ALL", "LC_MESSAGES", "LANG"):
        val = os.environ.get(var)
        if val:
            matched = normalize_language_code(val.split(".")[0])
            if matched:
                return matched
    try:
        loc = locale.getdefaultlocale()
        if loc and loc[0]:
            matched = normalize_language_code(loc[0])
            if matched:
                return matched
    except Exception:
        pass
    return DEFAULT_LANGUAGE


def get_current_language() -> str:
    """Resolves current language following priority: override -> config -> system -> en."""
    global _CURRENT_LANGUAGE_OVERRIDE
    if _CURRENT_LANGUAGE_OVERRIDE:
        return _CURRENT_LANGUAGE_OVERRIDE

    try:
        from kapsel.storage.config import load_config
        cfg = load_config()
        configured = getattr(cfg, "language", None) or cfg.raw.get("language")
        if configured and str(configured).lower() != "auto":
            matched = normalize_language_code(str(configured))
            if matched:
                return matched
    except Exception:
        pass

    return detect_system_language()


def set_current_language(lang_code: str, persist: bool = True) -> bool:
    """Sets active language and optionally persists to config."""
    global _CURRENT_LANGUAGE_OVERRIDE
    matched = normalize_language_code(lang_code)
    if not matched:
        return False
    _CURRENT_LANGUAGE_OVERRIDE = matched
    _TRANSLATION_CACHE.clear()

    if persist:
        try:
            from kapsel.storage.config import update_config_value
            update_config_value("language", matched)
        except Exception:
            pass

    return True


def get_translation(lang: Optional[str] = None) -> gettext.NullTranslations:
    """Loads and caches gettext translation catalog for the target language."""
    target_lang = lang or get_current_language()
    if target_lang in _TRANSLATION_CACHE:
        return _TRANSLATION_CACHE[target_lang]

    locales_dir = get_locales_dir()
    try:
        trans = gettext.translation(
            domain=DOMAIN,
            localedir=str(locales_dir),
            languages=[target_lang],
            fallback=True,
        )
    except Exception:
        trans = gettext.NullTranslations()

    _TRANSLATION_CACHE[target_lang] = trans
    return trans


def load_help_data(lang: Optional[str] = None) -> Dict[str, Any]:
    """Loads structured help manual data file for the specified language with fallback to English."""
    import yaml
    target_lang = lang or get_current_language()
    locales_dir = get_locales_dir()
    primary = locales_dir / target_lang / "help.yaml"
    fallback = locales_dir / DEFAULT_LANGUAGE / "help.yaml"
    if primary.exists():
        try:
            with open(primary, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception:
            pass
    if fallback.exists():
        try:
            with open(fallback, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception:
            pass
    return {}


def _(message: str) -> str:
    """Standard gettext translation function."""
    trans = get_translation()
    return trans.gettext(message)


def ngettext(singular: str, plural: str, n: int) -> str:
    """Standard gettext pluralization function."""
    trans = get_translation()
    return trans.ngettext(singular, plural, n)
