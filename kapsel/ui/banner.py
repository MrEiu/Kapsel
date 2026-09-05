"""
Kapsel dynamic environment welcome banner.
Renders a modern, elegant Claude-style welcome card on startup.
"""

from pathlib import Path
import platform
import sys
from typing import Optional

from rich.box import ROUNDED
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from kapsel import __version__
from kapsel.core.detector import detector
from kapsel.i18n import _


def ensure_utf8_io() -> None:
    """Ensure standard input and output streams use utf-8 encoding."""
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def render_banner(
    console: Optional[Console] = None,
) -> None:
    """Renders a modern, refined Claude-style welcome card on startup."""
    ensure_utf8_io()
    if console is None:
        console = Console(legacy_windows=False)

    # Format current working directory (e.g. ~/Desktop/Kapsel)
    cwd = Path.cwd()
    home = Path.home()
    try:
        if cwd == home or home in cwd.parents:
            cwd_fmt = f"~/{cwd.relative_to(home).as_posix()}"
        else:
            cwd_fmt = cwd.as_posix()
    except Exception:
        cwd_fmt = str(cwd)

    # Sniff git branch and host shell
    branch = detector.get_git_branch()
    branch_badge = f" [dim #10b981](🌿 {branch})[/]" if branch else ""

    shell_name, _shell_path = detector.detect_shell()
    arch = platform.machine()
    shell_info = f"[bold #38bdf8]{shell_name}[/] [dim #6b7280]({arch})[/]"

    grid = Table.grid(padding=(0, 1))
    grid.add_column()

    # Top brand row with modern micro block logo
    top_row = Table.grid(padding=(0, 2))
    top_row.add_column(style="bold #00f0ff", vertical="middle")
    top_row.add_column(vertical="middle")

    logo = (
        "█ █ █▀█ █▀█ █▀▀ █▀▀ █\n"
        "█▀▄ █▀█ █▀▀ ▄██ ██▄ █▄▄"
    )

    info = Text()
    info.append("💊 KAPSEL  ", style="bold #00f0ff")
    info.append(f"v{__version__}\n", style="bold #6366f1")
    info.append("Wrap complexity, expose simplicity.", style="dim italic #9ca3af")

    top_row.add_row(logo, info)
    grid.add_row(top_row)
    grid.add_row("")

    # Session metadata row
    cwd_label = _("cwd:")
    shell_label = _("shell:")
    meta_line = (
        f"[dim #6b7280]{cwd_label}   [/][#e4e4e7]{cwd_fmt}[/]{branch_badge}   "
        f"[dim #6b7280]{shell_label} [/]{shell_info}"
    )
    grid.add_row(meta_line)
    grid.add_row("")

    # Claude Code style tips section
    tips_title = _("Tips for getting started:")
    grid.add_row(f"[bold #a855f7]{tips_title}[/]")

    tip1 = _("Type {cmd1} or {cmd2} to explore available commands").format(
        cmd1="[bold #38bdf8]help[/]", cmd2="[bold #00f0ff]kps help[/]"
    )
    tip2 = _("Press {key} to trigger intelligent context-aware completions").format(
        key="[bold #f59e0b]Tab[/]"
    )
    tip3 = _("Run {cmd1} to inspect dashboard · {cmd2} to quit session").format(
        cmd1="[bold #38bdf8]kps status[/]", cmd2="[bold #f43f5e]exit[/]"
    )

    grid.add_row(f" [dim]•[/] {tip1}")
    grid.add_row(f" [dim]•[/] {tip2}")
    grid.add_row(f" [dim]•[/] {tip3}")

    panel = Panel(
        grid,
        box=ROUNDED,
        border_style="#3f3f46",
        padding=(1, 2),
        expand=False,
    )

    console.print()
    console.print(panel)
    console.print()

