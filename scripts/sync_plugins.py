"""
Plugin Synchronization Tool for Kapsel.
Synchronizes plugins developed in the local workspace ('./plugins/<name>') to:
1. The external repository folder ('C:\\Users\\meru6\\Desktop\\plugins\\<name>')
2. The global Kapsel runtime directory ('~/.kapsel/plugins/<name>')

Usage:
    python scripts/sync_plugins.py           # Sync all plugins
    python scripts/sync_plugins.py install   # Sync only 'install' plugin
"""

import argparse
from pathlib import Path
import shutil
import sys

from rich.console import Console

from kapsel.storage.config import get_kapsel_dir
from kapsel.ui.banner import ensure_utf8_io

ensure_utf8_io()
console = Console(legacy_windows=False)


def sync_plugin(
    plugin_name: str,
    src_dir: Path,
    desktop_plugins_dir: Path,
    global_plugins_dir: Path,
) -> bool:
    """Synchronizes a single plugin directory to both destinations."""
    plugin_src = src_dir / plugin_name
    if not plugin_src.exists() or not plugin_src.is_dir():
        console.print(f"[bold #f43f5e]Error:[/] Plugin source directory '{plugin_src}' does not exist.")
        return False

    console.print(f"\n[bold #00f0ff]🔄 Syncing plugin: [white]{plugin_name}[/][/]")

    # Filter pattern: ignore Python cache and git internal objects during file sync
    ignore_func = shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo", ".pytest_cache", ".git")

    # 1. Sync to Desktop/plugins/<plugin_name>
    target_desktop = desktop_plugins_dir / plugin_name
    target_desktop.mkdir(parents=True, exist_ok=True)
    try:
        shutil.copytree(plugin_src, target_desktop, dirs_exist_ok=True, ignore=ignore_func)
        console.print(f"  [bold #10b981]✔[/] External repo: [dim]{target_desktop}[/]")
    except Exception as e:
        console.print(f"  [bold #f43f5e]✘ Failed to copy to external repo:[/] {e}")
        return False

    # 2. Sync to Global runtime directory (~/.kapsel/plugins/<plugin_name>)
    target_global = global_plugins_dir / plugin_name
    target_global.mkdir(parents=True, exist_ok=True)
    try:
        shutil.copytree(plugin_src, target_global, dirs_exist_ok=True, ignore=ignore_func)
        console.print(f"  [bold #10b981]✔[/] Global runtime: [dim]{target_global}[/]")
    except Exception as e:
        console.print(f"  [bold #f43f5e]✘ Failed to copy to global runtime:[/] {e}")
        return False

    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Synchronize Kapsel development plugins.")
    parser.add_argument("plugin", nargs="?", default=None, help="Name of specific plugin to sync (default: all)")
    parser.add_argument(
        "--src",
        type=Path,
        default=Path.cwd() / "plugins",
        help="Local workspace plugins folder (default: ./plugins)",
    )
    parser.add_argument(
        "--desktop",
        type=Path,
        default=Path.home() / "Desktop" / "plugins",
        help="Target Desktop plugins directory (default: ~/Desktop/plugins)",
    )

    args = parser.parse_args()

    src_dir = args.src.resolve()
    desktop_plugins_dir = args.desktop.resolve()
    global_plugins_dir = (get_kapsel_dir() / "plugins").resolve()

    if not src_dir.exists():
        console.print(f"[bold #f43f5e]Error:[/] Source directory '{src_dir}' not found.")
        return 1

    plugins_to_sync = []
    if args.plugin:
        plugins_to_sync.append(args.plugin)
    else:
        for item in src_dir.iterdir():
            if item.is_dir() and not item.name.startswith("."):
                plugins_to_sync.append(item.name)

    if not plugins_to_sync:
        console.print(f"[yellow]No plugins found in '{src_dir}'.[/]")
        return 0

    success_count = 0
    for p_name in plugins_to_sync:
        if sync_plugin(p_name, src_dir, desktop_plugins_dir, global_plugins_dir):
            success_count += 1

    console.print(
        f"\n[bold #10b981]✨ Done! Successfully synchronized {success_count}/{len(plugins_to_sync)} plugin(s).[/]\n"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
