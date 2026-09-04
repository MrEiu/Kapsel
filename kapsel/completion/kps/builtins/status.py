"""
Kapsel Status Command.
Renders comprehensive runtime environment, shell sniffing, and sandbox status dashboard.
"""

from datetime import datetime
import os
from pathlib import Path
import platform
import sys
from typing import List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from kapsel import __version__
from kapsel.core.detector import detector
from kapsel.storage.config import load_config
from kapsel.storage.logger import get_kapsel_dir
from kapsel.ui.banner import ensure_utf8_io


def handle_status(args: Optional[List[str]] = None, console: Optional[Console] = None) -> int:
    """Renders the detailed Kapsel environment and runtime status dashboard."""
    ensure_utf8_io()
    con = console or Console(legacy_windows=False)

    shell_name, shell_path = detector.detect_shell()
    is_elevated, elevated_label = detector.is_elevated()
    cwd_raw = Path.cwd()
    cwd_fmt = detector.format_cwd(cwd_raw)
    branch = detector.get_git_branch(cwd_raw)
    cfg = load_config()
    sandbox_dir = get_kapsel_dir()

    # Status Grid
    grid = Table.grid(expand=True, padding=(0, 2))
    grid.add_column(style="bold #00f0ff", justify="right", width=18)
    grid.add_column(style="#e4e4e7")
    grid.add_column(style="bold #a855f7", justify="right", width=18)
    grid.add_column(style="#e4e4e7")

    priv_badge = (
        f"[bold #10b981][{elevated_label}][/]"
        if not is_elevated
        else f"[bold #f59e0b][{elevated_label} (Admin)][/]"
    )

    grid.add_row(
        "🖥️ Platform:",
        f"{platform.system()} {platform.release()} ({platform.machine()})",
        "🐚 Host Shell:",
        f"[bold #38bdf8]{shell_name}[/] [dim]({shell_path})[/]",
    )

    grid.add_row(
        "⚡ Privilege:",
        priv_badge,
        "🌿 Git Branch:",
        f"[bold #10b981]{branch}[/]" if branch else "[dim]None[/]",
    )

    grid.add_row(
        "📂 Working Dir:",
        f"[dim]{cwd_fmt}[/]",
        "💊 Kapsel Version:",
        f"[bold #00f0ff]v{__version__}[/] (Python {sys.version.split()[0]})",
    )

    theme_name = cfg.theme.get("name", "cyber_dark") if isinstance(cfg.theme, dict) else str(cfg.theme)
    border_status = "On" if cfg.enable_card_border else "Off"
    grid.add_row(
        "📦 Sandbox Dir:",
        f"[dim]{sandbox_dir}[/]",
        "🎨 Active Theme:",
        f"[bold #a855f7]{theme_name}[/] [dim](Border: {border_status})[/]",
    )

    # Completion & Plugins info
    from kapsel.completion.kps.registry import get_kps_registry
    registry = get_kps_registry()
    commands = registry.list_commands()

    from kapsel.completion.carapace_engine import get_carapace_engine
    carapace_eng = get_carapace_engine()
    if carapace_eng.is_available():
        tools_count = len(carapace_eng.get_supported_tools())
        completer_label = f"[bold #10b981]{tools_count}+[/] Carapace specs"
    else:
        specs_dir = Path(__file__).resolve().parent.parent.parent / "specs"
        spec_count = len(list(specs_dir.glob("*.json"))) if specs_dir.exists() else 0
        completer_label = f"[dim]{spec_count} Fig specs[/]"

    is_active = os.environ.get("KAPSEL_ACTIVE") == "1"
    grid.add_row(
        "🎯 Completer:",
        completer_label,
        "⚙️ Session Mode:",
        f"[bold #10b981]🟢 Active[/]" if is_active else "[dim]⚪ Standby[/]",
    )

    panel = Panel(
        grid,
        title="[bold #00f0ff]💊 KAPSEL System & Environment Status[/]",
        title_align="left",
        border_style="#0891b2",
        padding=(1, 2),
    )

    con.print()
    con.print(panel)
    con.print()
    return 0
