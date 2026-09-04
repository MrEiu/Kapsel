"""
Kapsel Config Command.
Handles 'config', 'config path', 'config edit', 'config get', 'config set', 'config reload'.
"""

import os
from pathlib import Path
import platform
import subprocess
from typing import Any, List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from kapsel.storage.config import (
    KapselConfig,
    get_config_path,
    load_config,
    update_config_value,
)
from kapsel.ui.banner import ensure_utf8_io


def handle_config_command(args: List[str], console: Optional[Console] = None) -> int:
    """Handles 'config [subcommand]' and renders rich output."""
    ensure_utf8_io()
    con = console or Console(legacy_windows=False)

    config_path = get_config_path()
    cfg = load_config()

    if not args:
        render_config_dashboard(cfg, config_path, con)
        return 0

    sub = args[0].lower()

    if sub == "path":
        print(str(config_path))
        return 0

    if sub == "edit":
        con.print(f"[dim]Opening configuration file:[/] [bold #00f0ff]{config_path}[/]")
        try:
            if platform.system() == "Windows":
                os.startfile(str(config_path))
            elif platform.system() == "Darwin":
                subprocess.run(["open", str(config_path)])
            else:
                subprocess.run(["xdg-open", str(config_path)])
            con.print("[bold #10b981]✔ Opened in external editor[/]")
        except Exception as e:
            con.print(f"[bold #f43f5e]Failed to open editor: {e}[/]")
            con.print(f"[dim]You can edit it manually at: {config_path}[/]")
        return 0

    if sub == "reload":
        new_cfg = load_config(force_reload=True)
        con.print(f"[bold #10b981]✔ Configuration reloaded.[/] (Theme: {new_cfg.theme.get('name')}, Tap: {new_cfg.interaction.get('autosuggest_tap_mode')})")
        return 0

    if sub in ("datadir", "migrate"):
        from kapsel.commands.datadir import handle_datadir_command
        return handle_datadir_command(args[1:], con)

    if sub == "get":
        if len(args) < 2:
            con.print("[bold #f43f5e]Error: Please specify configuration key (e.g. config get interaction.autosuggest_tap_mode)[/]")
            return 1
        key_path = args[1]
        val = get_nested_val(cfg.raw, key_path)
        if val is None:
            con.print(f"[dim]Config key '{key_path}' is not set (using default)[/]")
        else:
            con.print(f"[bold #00f0ff]{key_path}[/] = [bold #10b981]{val}[/]")
        return 0

    if sub == "set":
        if len(args) < 3:
            con.print("[bold #f43f5e]Error: Invalid format. Usage: config set <key.path> <value>[/]")
            con.print("[dim]Example: config set interaction.autosuggest_tap_mode full[/]")
            con.print("[dim]Example: config set interaction.autosuggest_sensitivity 0.15[/]")
            return 1
        key_path = args[1]
        val_str = args[2]

        parsed_val: Any = val_str
        if val_str.lower() in ("true", "yes", "1", "on"):
            parsed_val = True
        elif val_str.lower() in ("false", "no", "0", "off"):
            parsed_val = False
        else:
            try:
                if "." in val_str:
                    parsed_val = float(val_str)
                else:
                    parsed_val = int(val_str)
            except ValueError:
                parsed_val = val_str

        success = update_config_value(key_path, parsed_val)
        if success:
            con.print(f"[bold #10b981]✔ Config updated:[/] [bold #00f0ff]{key_path}[/] = [bold #10b981]{parsed_val}[/]")
            con.print("[dim]Saved to ~/.kapsel/config.yaml and reloaded.[/]")
            return 0
        else:
            con.print(f"[bold #f43f5e]✘ Failed to update config. Check key path: '{key_path}'[/]")
            return 1

    con.print(f"[bold #f43f5e]Unknown config subcommand: '{sub}'.[/] See 'kapsel config --help'.")
    return 1


def get_nested_val(data: dict, path: str) -> Any:
    keys = path.split(".")
    curr = data
    for k in keys:
        if isinstance(curr, dict) and k in curr:
            curr = curr[k]
        else:
            return None
    return curr


def render_config_dashboard(cfg: KapselConfig, config_path: Path, console: Console) -> None:
    inter = cfg.interaction
    ui_cfg = cfg.ui
    theme_cfg = cfg.theme
    cloud_cfg = cfg.raw.get("cloud", {})

    grid = Table.grid(expand=True, padding=(0, 2))
    grid.add_column(style="bold #00f0ff", justify="right", width=22)
    grid.add_column(style="#e4e4e7")
    grid.add_column(style="bold #a855f7", justify="right", width=22)
    grid.add_column(style="#e4e4e7")

    grid.add_row(
        "🎯 Autosuggest Tap:",
        f"[bold #10b981]{inter.get('autosuggest_tap_mode', 'word')}[/]",
        "🎨 Active Theme:",
        f"[bold #00f0ff]{theme_cfg.get('name', 'cyber_dark')}[/]",
    )
    grid.add_row(
        "⚡ Hold Action:",
        f"[bold #10b981]{inter.get('autosuggest_hold_action', 'full')}[/]",
        "⏱ Card Border:",
        f"[bold #10b981]{'On' if ui_cfg.get('enable_card_border') else 'Off'}[/]",
    )
    grid.add_row(
        "⏲ Sensitivity:",
        f"[bold #10b981]{inter.get('autosuggest_sensitivity', 0.25)}s[/]",
        " Git Badge:",
        f"[bold #10b981]{'On' if ui_cfg.get('show_git_branch') else 'Off'}[/]",
    )
    grid.add_row(
        "🔢 Threshold Count:",
        f"[bold #10b981]{inter.get('consecutive_press_threshold', 2)}[/]",
        "🌐 Cloud Endpoint:",
        f"[dim]{cloud_cfg.get('server_endpoint', 'http://127.0.0.1:8000')}[/]",
    )

    content = Table.grid(expand=True, padding=(1, 0))
    content.add_column()

    header = Text()
    header.append("⚙️ KAPSEL Configuration Dashboard\n", style="bold #00f0ff")
    header.append(f"Config path: {config_path}\n", style="dim #6b7280")
    header.append("Run 'config edit' to open editor · Run 'config set <key> <val>' to update", style="italic #9ca3af")

    content.add_row(header)
    content.add_row(grid)

    panel = Panel(
        content,
        border_style="#0891b2",
        padding=(1, 2),
        expand=False,
    )

    console.print()
    console.print(panel)
    console.print()
