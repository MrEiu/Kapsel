"""
Kapsel theme, styling, and aesthetic tokens.
Modern dark cyber palette for rich and prompt_toolkit.
"""

from typing import Dict
from prompt_toolkit.styles import Style

# Rich color palette
PALETTE = {
    "primary": "#00f0ff",       # Electric Cyan
    "primary_dim": "#0891b2",
    "secondary": "#a855f7",     # Neon Purple
    "secondary_dim": "#7c3aed",
    "success": "#10b981",       # Emerald Green
    "warning": "#f59e0b",       # Amber
    "error": "#f43f5e",         # Neon Red
    "dim": "#6b7280",           # Slate Gray
    "bg_dark": "#18181b",       # Zinc 900
    "bg_card": "#27272a",       # Zinc 800
    "fg_light": "#f4f4f5",      # Zinc 100
    "accent_blue": "#38bdf8",   # Sky Blue
}

# Prompt Toolkit Style mapping
PT_STYLE = Style.from_dict({
    # Prompt styles
    "prompt.top": "#0891b2 bold",
    "prompt.bottom": "#0891b2 bold",
    "prompt.capsule": "#00f0ff bold",
    "prompt.shell": "bg:#27272a #00f0ff bold",
    "prompt.cwd": "#38bdf8 bold",
    "prompt.branch": "#a855f7 bold",
    "prompt.arrow": "#00f0ff bold",
    "prompt.time": "#6b7280",

    # Auto suggestion (inline ghost text)
    "auto-suggestion": "#6b7280 italic",

    # Bottom Toolbar
    "toolbar.kps": "bg:#a855f7 #ffffff bold",
    "toolbar.kps_info": "bg:#27272a #e4e4e7 italic",
    "toolbar.native": "bg:#0891b2 #ffffff bold",
    "toolbar.native_info": "bg:#18181b #9ca3af",

    # Completion Menu
    "completion-menu": "bg:#1e1e24 #d4d4d8",
    "completion-menu.completion": "bg:#1e1e24 #f4f4f5",
    "completion-menu.completion.current": "bg:#0891b2 #ffffff bold",
    "completion-menu.meta": "bg:#27272a #9ca3af",
    "completion-menu.meta.current": "bg:#0e7490 #ffffff italic",
    "completion-menu.progress-button": "bg:#3f3f46",
    "completion-menu.progress-bar": "bg:#18181b",

    # Custom tags inside completion
    "kps.alias": "#00f0ff bold",
    "kps.desc": "#10b981",
    "kps.preview": "#a855f7 italic",

    # Block Roaming Mode toolbar styles
    "roaming.badge": "bg:#0891b2 #ffffff bold",
    "roaming.index": "bg:#18181b #00f0ff bold",
    "roaming.success": "bg:#27272a #10b981",
    "roaming.failed": "bg:#27272a #f43f5e",
    "roaming.help": "bg:#18181b #9ca3af",
    "roaming.bar": "bg:#18181b #9ca3af italic",
})
