"""
Backwards-compatibility forwarder for kapsel.i18n.
"""

from kapsel.i18n import (
    DEFAULT_LANGUAGE,
    DOMAIN,
    SUPPORTED_LANGUAGES,
    _,
    detect_system_language,
    get_current_language,
    get_locales_dir,
    get_translation,
    ngettext,
    normalize_language_code,
    set_current_language,
)

__all__ = [
    "DEFAULT_LANGUAGE",
    "DOMAIN",
    "SUPPORTED_LANGUAGES",
    "_",
    "ngettext",
    "detect_system_language",
    "get_current_language",
    "get_locales_dir",
    "get_translation",
    "normalize_language_code",
    "set_current_language",
]
