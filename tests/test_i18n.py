"""
Unit tests for Kapsel Internationalization (i18n) engine.
Validates gettext + Babel integration, translation lookup, fallback mechanism,
and help data loading across all 7 supported languages.
"""

import pytest
from kapsel.i18n import (
    SUPPORTED_LANGUAGES,
    _,
    get_current_language,
    get_locales_dir,
    get_translation,
    load_help_data,
    normalize_language_code,
    set_current_language,
)


def test_supported_languages():
    """Verify that all 7 required languages are configured."""
    expected = {"en", "zh_CN", "ja", "es", "fr", "de", "ru"}
    assert set(SUPPORTED_LANGUAGES.keys()) == expected


def test_normalize_language_code():
    """Verify normalizer handles raw codes, locales, and aliases."""
    assert normalize_language_code("en") == "en"
    assert normalize_language_code("EN_us") == "en"
    assert normalize_language_code("english") == "en"
    assert normalize_language_code("zh") == "zh_CN"
    assert normalize_language_code("zh-CN") == "zh_CN"
    assert normalize_language_code("chinese") == "zh_CN"
    assert normalize_language_code("ja") == "ja"
    assert normalize_language_code("jp") == "ja"
    assert normalize_language_code("japanese") == "ja"
    assert normalize_language_code("es") == "es"
    assert normalize_language_code("spanish") == "es"
    assert normalize_language_code("fr") == "fr"
    assert normalize_language_code("french") == "fr"
    assert normalize_language_code("de") == "de"
    assert normalize_language_code("german") == "de"
    assert normalize_language_code("ru") == "ru"
    assert normalize_language_code("russian") == "ru"
    assert normalize_language_code("nonexistent_lang") is None
    assert normalize_language_code(None) is None


def test_gettext_translation_lookup():
    """Verify gettext catalogs translate UI strings properly."""
    try:
        set_current_language("en", persist=False)
        assert _("Available Languages") == "Available Languages"

        set_current_language("zh_CN", persist=False)
        assert _("Available Languages") == "支持的系统语言"

        set_current_language("ja", persist=False)
        assert _("Available Languages") == "利用可能な言語一覧"

        set_current_language("es", persist=False)
        assert _("Available Languages") == "Idiomas disponibles"

        set_current_language("fr", persist=False)
        assert _("Available Languages") == "Langues disponibles"

        set_current_language("de", persist=False)
        assert _("Available Languages") == "Verfügbare Sprachen"

        set_current_language("ru", persist=False)
        assert _("Available Languages") == "Доступные языки"
    finally:
        set_current_language("en", persist=False)


def test_help_data_loading_all_languages():
    """Verify data-driven help datasets exist and parse correctly for all 7 languages."""
    required_sections = ["meta", "modes", "quickstart", "commands", "shortcuts", "tips"]
    for lang in SUPPORTED_LANGUAGES:
        data = load_help_data(lang)
        assert data, f"Help data for language '{lang}' should not be empty."
        for sec in required_sections:
            assert sec in data, f"Missing section '{sec}' in help.yaml for language '{lang}'"


def test_help_data_fallback():
    """Verify fallback to English when an unknown language is queried."""
    data = load_help_data("unsupported_fake_lang")
    assert data
    assert data.get("meta", {}).get("title") == "KAPSEL"
