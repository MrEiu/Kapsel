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
        con.print(
            Panel(
                "[bold #00f0ff]🔌 Kapsel 终端托管模式当前处于激活状态 (Active)[/]\n\n"
                "[white]在终端中输入 '[bold #38bdf8]kapsel toggle[/]' 或 '[bold #38bdf8]toggle[/]' 即可关闭退出并切回宿主终端。[/]",
                title="[bold #00f0ff]💊 Kapsel Toggle[/]",
                border_style="#0891b2",
                expand=False,
            )
        )
    else:
        con.print(
            Panel(
                "[bold #10b981]✔ Kapsel 终端托管模式已就绪 (Inactive)[/]\n\n"
                "[white]运行 '[bold #38bdf8]kapsel toggle[/]' 开启并将 Kapsel 作为当前终端默认环境；\n"
                "在会话中再次输入 '[bold #38bdf8]kapsel toggle[/]' 或 '[bold #38bdf8]toggle[/]' 即可关闭。[/]",
                title="[bold #00f0ff]💊 Kapsel Toggle[/]",
                border_style="#0891b2",
                expand=False,
            )
        )
    return 0
