"""
Kapsel UI and Aesthetic Presentation Package.
Pure presentation components: banner logo, status cards, prompt session, and cyber dark theme.
"""

from kapsel.core.completion import DualStateCompleter
from kapsel.ui.banner import ensure_utf8_io, render_banner
from kapsel.ui.card import get_prompt_tokens, render_execution_footer
from kapsel.ui.prompt import KapselPrompt
from kapsel.ui.theme import PALETTE, PT_STYLE

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
