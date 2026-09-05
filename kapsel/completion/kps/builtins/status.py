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
from kapsel.i18n import _
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

    admin_str = _("Admin")
    priv_badge = (
        f"[bold #10b981][{elevated_label}][/]"
        if not is_elevated
        else f"[bold #f59e0b][{elevated_label} ({admin_str})][/]"
    )

    none_str = _("None")
    grid.add_row(
        f"🖥️ {_('Platform:')}",
        f"{platform.system()} {platform.release()} ({platform.machine()})",
        f"🐚 {_('Host Shell:')}",
        f"[bold #38bdf8]{shell_name}[/] [dim]({shell_path})[/]",
    )

    grid.add_row(
        f"⚡ {_('Privilege:')}",
        priv_badge,
        f"🌿 {_('Git Branch:')}",
        f"[bold #10b981]{branch}[/]" if branch else f"[dim]{none_str}[/]",
    )

    grid.add_row(
        f"📂 {_('Working Dir:')}",
        f"[dim]{cwd_fmt}[/]",
        f"💊 {_('Kapsel Version:')}",
        f"[bold #00f0ff]v{__version__}[/] (Python {sys.version.split()[0]})",
    )

    theme_name = cfg.theme.get("name", "cyber_dark") if isinstance(cfg.theme, dict) else str(cfg.theme)
    border_status = _("On") if cfg.enable_card_border else _("Off")
    grid.add_row(
        f"📦 {_('Sandbox Dir:')}",
        f"[dim]{sandbox_dir}[/]",
        f"🎨 {_('Active Theme:')}",
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
        completer_label = f"[yellow]{_('Basic (offline)')}[/] [dim]({_('Run: kapsel setup-completion')})[/]"

    is_active = os.environ.get("KAPSEL_ACTIVE") == "1"
    active_str = _("Active")
    standby_str = _("Standby")
    grid.add_row(
        f"🎯 {_('Completer:')}",
        completer_label,
        f"⚙️ {_('Session Mode:')}",
        f"[bold #10b981]🟢 {active_str}[/]" if is_active else f"[dim]⚪ {standby_str}[/]",
    )

    # Active Plugins with Versions
    from kapsel.core.plugin.catalog import load_plugin_catalog_rich
    rich_catalog = load_plugin_catalog_rich()
    enabled_plugins = getattr(cfg, "enabled_plugins", []) or []
    if not enabled_plugins:
        from kapsel.completion.kps.builtins.plugin_switch import get_all_installed_plugins
        active_plugins = get_all_installed_plugins()
    else:
        active_plugins = [p.lower() for p in enabled_plugins]

    if active_plugins:
        plugin_badges = [
            f"[bold #00f0ff]{p}[/][dim]@{rich_catalog.get(p, {}).get('version', '0.1.0')}[/]"
            for p in active_plugins
        ]
        plugins_str = ", ".join(plugin_badges)
    else:
        plugins_str = f"[dim]{none_str}[/]"

    grid.add_row(
        f"🧩 {_('Active Plugins:')}",
        plugins_str,
        "",
        "",
    )

    title_str = _("💊 KAPSEL System & Environment Status")
    panel = Panel(
        grid,
        title=f"[bold #00f0ff]{title_str}[/]",
        title_align="left",
        border_style="#0891b2",
        padding=(1, 2),
    )

    con.print()
    con.print(panel)
    if not carapace_eng.is_available():
        con.print(
            f" [dim]💡[/] [yellow]{_('Tip: Carapace engine not found. Run')}[/] "
            f"[bold #00f0ff]kapsel setup-completion[/] "
            f"[yellow]{_('to download and enable 1,000+ dynamic tool completions.')}[/]\n"
        )
    else:
        con.print()
    return 0
