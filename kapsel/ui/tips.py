"""
Kapsel dynamic tip of the day loader.
Loads localized tips from kapsel/locales/<lang>/tips.yaml and user config.
All comments and descriptions are in English.
"""

from pathlib import Path
import random
from typing import List, Optional, Tuple
import yaml

from kapsel.i18n import get_current_language, get_locales_dir
from kapsel.storage.config import get_kapsel_dir


def load_tips_data(lang: Optional[str] = None) -> Tuple[str, List[str]]:
    """
    Loads localized title and tip list for the given language.
    Falls back to English if the target language tips file is not found.
    Also merges user custom tips from ~/.kapsel/tips.yaml if present.
    """
    active_lang = lang or get_current_language()
    locales_dir = get_locales_dir()

    tips_file = locales_dir / active_lang / "tips.yaml"
    if not tips_file.exists():
        tips_file = locales_dir / "en" / "tips.yaml"

    title = "Tip:"
    tips: List[str] = []

    if tips_file.exists():
        try:
            with open(tips_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                if isinstance(data, dict):
                    title = data.get("title", title)
                    raw_tips = data.get("tips", [])
                    if isinstance(raw_tips, list):
                        tips.extend(raw_tips)
        except Exception:
            pass

    # Merge user custom tips from ~/.kapsel/tips.yaml if present
    try:
        user_tips_file = get_kapsel_dir() / "tips.yaml"
        if user_tips_file.exists():
            with open(user_tips_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                if isinstance(data, dict):
                    user_tips = data.get("tips", [])
                    if isinstance(user_tips, list):
                        tips.extend(user_tips)
    except Exception:
        pass

    return title, tips


def get_random_tip(lang: Optional[str] = None) -> Tuple[str, str]:
    """
    Returns a tuple of (title, random_tip).
    e.g. ("技巧:", "当补全建议仅剩 1 项候选词时...")
    """
    title, tips = load_tips_data(lang)
    if tips:
        return title, random.choice(tips)
    return title, "Press [bold #f59e0b]Tab[/] to trigger intelligent context-aware completions."
