"""
Kapsel Plugin Switcher Commands: 'kapsel enable <plugin>' and 'kapsel disable <plugin>'.
Manages plugin activation states in ~/.kapsel/config.yaml and updates autocompletion specs.
All comments and descriptions are in English.
"""

from pathlib import Path
from typing import List, Optional, Set
from rich.console import Console

from kapsel.core.plugin.catalog import load_plugin_catalog_rich
from kapsel.storage.config import get_kapsel_dir, load_config, update_config_value
from kapsel.ui.banner import ensure_utf8_io

ensure_utf8_io()


def get_all_installed_plugins() -> List[str]:
    """Finds all locally installed or workspace plugin IDs."""
    installed: Set[str] = set()

    # 1. Workspace plugins
    local_dev_dir = Path.cwd() / "plugins"
    if local_dev_dir.is_dir():
        for item in local_dev_dir.iterdir():
            if item.is_dir() and not item.name.startswith((".", "__")) and (item / "__init__.py").exists():
                installed.add(item.name.lower())

    # 2. Global plugins
    global_plugins_dir = get_kapsel_dir() / "plugins"
    if global_plugins_dir.is_dir():
        for item in global_plugins_dir.iterdir():
            if item.is_dir() and not item.name.startswith((".", "__")) and (item / "__init__.py").exists():
                installed.add(item.name.lower())

    return sorted(installed)


def handle_enable_plugin(args: List[str], console: Optional[Console] = None) -> int:
    """
    Enables one or more installed Kapsel plugins.
    Usage:
      kapsel enable <plugin_name>
    """
    con = console or Console(legacy_windows=False)
    if not args:
        con.print("[bold #f43f5e]Error:[/] Please specify a plugin name to enable.")
        con.print("[dim]Usage: kapsel enable <plugin_name> (e.g. kapsel enable shore)[/]\n")
        return 1

    target = args[0].strip().lower()
    cfg = load_config()
    current_enabled = list(cfg.enabled_plugins or [])
    all_installed = get_all_installed_plugins()

    # If current_enabled is empty, all installed plugins are already active
    if not current_enabled:
        if target in all_installed:
            con.print(f"[yellow]Plugin '[bold #00f0ff]{target}[/]' is already active and enabled.[/]\n")
            return 0
        # If not installed, start explicit enabled list from all_installed
        current_enabled = list(all_installed)

    if target in current_enabled:
        con.print(f"[yellow]Plugin '[bold #00f0ff]{target}[/]' is already enabled.[/]\n")
        return 0

    # Verify plugin exists locally; if missing, attempt auto-install via fetcher
    global_plugins_dir = get_kapsel_dir() / "plugins"
    dest_plugin_dir = global_plugins_dir / target
    local_dev_dir = Path.cwd() / "plugins" / target

    if not (dest_plugin_dir.exists() or local_dev_dir.exists()):
        con.print(f"[dim]Plugin '[white]{target}[/]' is not installed locally. Fetching from official repository...[/]")
        from kapsel.core.plugin.fetcher import fetch_plugin_from_remote
        if not fetch_plugin_from_remote(target, dest_plugin_dir, con):
            con.print(f"[bold #f43f5e]Error:[/] Plugin '[white]{target}[/]' could not be found or downloaded.")
            con.print("[dim]Run 'kapsel search' to browse available official plugins.[/]\n")
            return 1

    current_enabled.append(target)
    update_config_value("plugins", "enabled", current_enabled)

    # Re-sync autocompletion specs
    try:
        from kapsel.completion.spec_manager import CarapaceSpecManager
        CarapaceSpecManager().sync_specs()
    except Exception:
        pass

    rich_catalog = load_plugin_catalog_rich()
    ver = rich_catalog.get(target, {}).get("version", "0.1.0")
    con.print(f"[bold #10b981]✔ Successfully enabled plugin '[bold #00f0ff]{target}[/]' (v{ver}).[/]")
    con.print(f"[dim]You can now run 'kps {target}' or explore its commands.[/]\n")
    return 0


def handle_disable_plugin(args: List[str], console: Optional[Console] = None) -> int:
    """
    Disables one or more active Kapsel plugins.
    Usage:
      kapsel disable <plugin_name>
    """
    con = console or Console(legacy_windows=False)
    if not args:
        con.print("[bold #f43f5e]Error:[/] Please specify a plugin name to disable.")
        con.print("[dim]Usage: kapsel disable <plugin_name> (e.g. kapsel disable shore)[/]\n")
        return 1

    target = args[0].strip().lower()
    cfg = load_config()
    current_enabled = list(cfg.enabled_plugins or [])
    all_installed = get_all_installed_plugins()

    # If current_enabled is empty, all installed plugins are implicitly active
    if not current_enabled:
        if target not in all_installed:
            con.print(f"[yellow]Plugin '[bold #00f0ff]{target}[/]' is not installed or active.[/]\n")
            return 1
        current_enabled = [p for p in all_installed if p != target]
        update_config_value("plugins", "enabled", current_enabled)
    else:
        if target not in current_enabled:
            con.print(f"[yellow]Plugin '[bold #00f0ff]{target}[/]' is already disabled or not active.[/]\n")
            return 0
        current_enabled.remove(target)
        update_config_value("plugins", "enabled", current_enabled)

    # Re-sync autocompletion specs
    try:
        from kapsel.completion.spec_manager import CarapaceSpecManager
        CarapaceSpecManager().sync_specs()
    except Exception:
        pass

    con.print(f"[bold #10b981]✔ Successfully disabled plugin '[bold #00f0ff]{target}[/]'.[/]")
    con.print(f"[dim]Plugin files remain preserved. Run 'kapsel enable {target}' anytime to reactivate.[/]\n")
    return 0
