"""
Kapsel dynamic environment welcome banner.
Renders concise, modern ASCII logo on startup.
"""

from pathlib import Path
import sys
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from kapsel import __version__

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
    """Renders a concise, modern ASCII capsule logo banner on startup."""
    ensure_utf8_io()
    if console is None:
        console = Console(legacy_windows=False)

    ascii_logo = r""" _  __               _ 
| |/ /__ _ _ __  ___| |
| ' // _` | '_ \/ __| |
|_|\_\__,_| .__/|___|_|
          |_|          """

    grid = Table.grid(padding=(0, 2))
    grid.add_column(style="bold #00f0ff")
    grid.add_column(style="default")

    info_lines = (
        f"[bold #00f0ff]💊 KAPSEL[/] [dim]v{__version__}[/]\n"
        "[dim italic]Wrap complexity, expose simplicity.[/]"
    )
    grid.add_row(ascii_logo, info_lines)

    panel = Panel(
        grid,
        border_style="#0891b2",
        padding=(0, 1),
        expand=False,
    )

    console.print()
    console.print(panel)
    console.print()
