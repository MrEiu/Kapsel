"""
Kapsel System Command: 'kapsel add <plugin_name>'.
Enables and registers plugins into the Kapsel environment.
Executes plugin-specific install.py scripts if provided by the plugin.
All comments and descriptions are in English.
"""

import importlib.util
from pathlib import Path
import shutil
import sys
from typing import List, Optional
from rich.console import Console
from rich.panel import Panel

from kapsel.storage.config import get_kapsel_dir, load_config, update_config_value
from kapsel.ui.banner import ensure_utf8_io


def handle_add_command(args: List[str], console: Optional[Console] = None) -> int:
    """
    Handles 'kapsel add <plugin_name>' system command.
    Enables local plugins, triggers their standalone install.py, and registers them into config.yaml.
    """
    ensure_utf8_io()
    con = console or Console(legacy_windows=False)

    if not args:
        con.print("[bold #f43f5e]Error:[/] Please specify a plugin name to add.")
        con.print("[dim]Usage: kapsel add <plugin_name> (e.g. kapsel add install)[/]\n")
        return 1

    target_raw = args[0].strip()

    # Handle 'kapsel add update' to scan and refresh catalog subcommands dictionary
    if target_raw.lower() == "update":
        from kapsel.core.plugin.catalog import update_plugin_catalog, render_catalog_table
        con.print("[bold #00f0ff]🔄 Scanning repository plugins and updating catalog dictionary...[/]")
        updated_catalog = update_plugin_catalog(con)
        render_catalog_table(updated_catalog, con)
        con.print("[bold #10b981]✔ Plugin catalog and subcommands completion dictionary successfully updated![/]\n")
        return 0

    cfg = load_config()
    is_dev = getattr(cfg, "is_dev", False)

    source_path = Path(target_raw).expanduser()

    global_plugins_dir = get_kapsel_dir() / "plugins"
    global_plugins_dir.mkdir(parents=True, exist_ok=True)

    # Determine plugin ID and source:
    # In release mode, bare names like 'install' will never be hijacked by local folders.
    # Only treat as a local directory if explicit path syntax is used (./, ../, /, \) or in dev mode.
    has_path_qualifier = any(sep in target_raw for sep in ("/", "\\")) or target_raw.startswith(".")

    if (has_path_qualifier or is_dev) and source_path.exists() and source_path.is_dir():
        # User specified an explicit directory path (or in dev mode where local directory takes priority)
        target_name = source_path.name.lower()
        dest_plugin_dir = global_plugins_dir / target_name

        # Verify source has __init__.py
        if not (source_path / "__init__.py").exists():
            con.print(f"[bold #f43f5e]Error:[/] Source directory '{source_path}' does not contain '__init__.py'.")
            return 1

        # Install / sync to user global plugin directory
        shutil.copytree(source_path, dest_plugin_dir, dirs_exist_ok=True)
        plugin_dir = dest_plugin_dir

    else:
        # User specified a plugin name (e.g. kapsel add install)
        target_name = target_raw.lower()
        dest_plugin_dir = global_plugins_dir / target_name
        dev_plugin_dir = Path.cwd() / "plugins" / target_name

        if is_dev and dev_plugin_dir.exists() and dev_plugin_dir.is_dir() and (dev_plugin_dir / "__init__.py").exists():
            # If present in local dev directory (dev mode only), sync to global user directory
            shutil.copytree(dev_plugin_dir, dest_plugin_dir, dirs_exist_ok=True)
            plugin_dir = dest_plugin_dir
        elif dest_plugin_dir.exists() and dest_plugin_dir.is_dir():
            plugin_dir = dest_plugin_dir
        else:
            # 3. Not found locally: Automatically fetch from official remote repository
            from kapsel.core.plugin.fetcher import fetch_plugin_from_remote

            if fetch_plugin_from_remote(target_name, dest_plugin_dir, con):
                plugin_dir = dest_plugin_dir
            else:
                con.print(f"[bold #f43f5e]Error:[/] Plugin '[white]{target_name}[/]' could not be installed.")
                con.print(f"[dim]Expected location:[/] {dest_plugin_dir}")
                con.print("[dim]To install a custom plugin, specify its local path or place it into your global plugins directory.[/]\n")
                return 1

    # Verify that the final plugin directory contains __init__.py
    if not (plugin_dir / "__init__.py").exists():
        con.print(f"[bold #f43f5e]Error:[/] Plugin directory '{plugin_dir}' does not contain a valid '__init__.py'.")
        return 1

    # Add to config.yaml enabled plugins list
    cfg = load_config()
    current_enabled = cfg.enabled_plugins
    if target_name not in current_enabled:
        new_enabled = current_enabled + [target_name]
        update_config_value("plugins", "enabled", new_enabled)

    # Decoupled plugin dependency installation:
    # Trigger standalone install.py if provided by the plugin
    install_script = plugin_dir / "install.py"
    if install_script.exists():
        try:
            bin_dir = get_kapsel_dir() / "bin"
            bin_dir.mkdir(parents=True, exist_ok=True)

            module_name = f"kapsel_installer_{target_name}"
            spec = importlib.util.spec_from_file_location(module_name, install_script)
            if spec and spec.loader:
                installer_mod = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = installer_mod
                spec.loader.exec_module(installer_mod)
                install_fn = getattr(installer_mod, "install", None)
                if callable(install_fn):
                    con.print(f"[dim]Running installer for '[#00f0ff]{target_name}[/]'...[/]")
                    success = install_fn(con, bin_dir)
                    if not success:
                        con.print(f"[yellow]Notice: Installation script for '{target_name}' finished with warnings.[/]")
        except Exception as e:
            con.print(f"[yellow]Warning: Failed to execute installer for '{target_name}':[/] {e}")

    from kapsel.core.plugin.catalog import _extract_plugin_version
    ver = _extract_plugin_version(plugin_dir)

    msg = f"[bold #10b981]✔ Plugin '[#00f0ff]{target_name}[/]' (v{ver}) successfully added and enabled![/]\n\n"
    msg += f"[dim]Location: {plugin_dir}[/]"

    con.print(Panel(msg, title="[bold #00f0ff]🔌 Plugin System[/]", border_style="#0891b2", expand=False))
    return 0
