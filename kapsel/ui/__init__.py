"""
Kapsel UI and aesthetic package.
"""

from kapsel.ui.theme import PALETTE, PT_STYLE
from kapsel.ui.banner import render_banner, ensure_utf8_io
from kapsel.ui.card import get_prompt_tokens, render_execution_footer
from kapsel.ui.completer import DualStateCompleter
from kapsel.ui.prompt import KapselPrompt

__all__ = [
    "PALETTE",
    "PT_STYLE",
    "render_banner",
    "ensure_utf8_io",
    "get_prompt_tokens",
    "render_execution_footer",
    "DualStateCompleter",
    "KapselPrompt",
]
