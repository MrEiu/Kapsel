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
    """Renders a responsive, modern Claude-style welcome card with dynamic i18n tips."""
    ensure_utf8_io()
    if console is None:
        console = Console(legacy_windows=False)

    term_width = console.width
    is_narrow = term_width < 68

    from kapsel.storage.config import load_config
    cfg = load_config()
    mode_badge = f" [bold #a855f7][dev][/]" if cfg.is_dev else ""

    # Format current working directory with smart truncation
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

    if is_narrow:
        # Compact adaptive header for narrow terminals / small windows
        header_text = Text()
        header_text.append("💊 KAPSEL  ", style="bold #00f0ff")
        header_text.append(f"v{__version__}{mode_badge}\n", style="bold #6366f1")
        header_text.append("Wrap complexity, expose simplicity.", style="dim italic #9ca3af")
        grid.add_row(header_text)
    else:
        # Standard wide layout with micro-block logo
        top_row = Table.grid(padding=(0, 2))
        top_row.add_column(style="bold #00f0ff", vertical="middle")
        top_row.add_column(vertical="middle")

        logo = (
            "█ █ █▀█ █▀█ █▀▀ █▀▀ █\n"
            "█▀▄ █▀█ █▀▀ ▄██ ██▄ █▄▄"
        )

        info = Text()
        info.append("💊 KAPSEL  ", style="bold #00f0ff")
        info.append(f"v{__version__}{mode_badge}\n", style="bold #6366f1")
        info.append("Wrap complexity, expose simplicity.", style="dim italic #9ca3af")

        top_row.add_row(logo, info)
        grid.add_row(top_row)

    grid.add_row("")

    # Session metadata row
    cwd_label = _("cwd:")
    shell_label = _("shell:")

    if is_narrow:
        grid.add_row(f"[dim #6b7280]{cwd_label} [/][#e4e4e7]{cwd_fmt}[/]{branch_badge}")
        grid.add_row(f"[dim #6b7280]{shell_label} [/]{shell_info}")
    else:
        # Truncate overly long path if needed to protect borders
        max_path_len = max(24, term_width - 40)
        if len(cwd_fmt) > max_path_len:
            cwd_fmt = "..." + cwd_fmt[-(max_path_len - 3):]
        meta_line = (
            f"[dim #6b7280]{cwd_label} [/][#e4e4e7]{cwd_fmt}[/]{branch_badge}    "
            f"[dim #6b7280]{shell_label} [/]{shell_info}"
        )
        grid.add_row(meta_line)

    grid.add_row("")

    # Dynamic localized Tip of the Day
    from kapsel.ui.tips import get_random_tip
    tip_title, tip_body = get_random_tip()
    grid.add_row(f"[bold #f59e0b]💡 {tip_title}[/] {tip_body}")

    panel = Panel(
        grid,
        box=ROUNDED,
        border_style="#3f3f46",
        padding=(0, 1) if is_narrow else (1, 2),
        expand=False,
    )

    console.print()
    console.print(panel)
    console.print()


