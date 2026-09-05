"""
Kapsel Toggle Command: 'kapsel toggle'.
Toggles Kapsel as the default terminal environment.
Typing it once opens the interactive Kapsel capsule shell.
Typing it a second time closes the shell and returns to the host terminal.
All comments and descriptions are in English.
"""

import os
from typing import List, Optional
from rich.console import Console
from rich.panel import Panel

from kapsel.i18n import _
from kapsel.ui.banner import ensure_utf8_io


def handle_toggle_command(args: Optional[List[str]] = None, console: Optional[Console] = None) -> int:
    """
    Handles 'kapsel toggle' command.
    Reports the toggle mechanism or current status.
    """
    ensure_utf8_io()
    con = console or Console(legacy_windows=False)

    is_active = os.environ.get("KAPSEL_ACTIVE") == "1"

    if is_active:
        msg = _("🔌 Kapsel session is active. Type 'kapsel toggle' or 'exit' to quit.")
        con.print(f"[bold #00f0ff]{msg}[/]")
    else:
        msg = _("✔ Kapsel session is ready. Run 'kapsel toggle' to launch.")
        con.print(f"[bold #10b981]{msg}[/]")
    return 0
