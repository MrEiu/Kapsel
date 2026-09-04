"""
Plugin Synchronization & Publishing Tool for Kapsel.
Synchronizes plugins developed in the local workspace ('./plugins/<name>') to:
1. The external repository folder ('C:\\Users\\meru6\\Desktop\\plugins')
2. The global Kapsel runtime directory ('~/.kapsel/plugins/<name>')
3. Automatically runs 'git add', 'git commit', and 'git push' to the remote GitHub repository.

Usage:
    python scripts/sync_plugins.py                  # Sync all plugins
    python scripts/sync_plugins.py install          # Sync only 'install' plugin
    python scripts/sync_plugins.py install --push   # Sync and automatically git push to GitHub
    python scripts/sync_plugins.py --new mytool     # Scaffold new plugin and sync/push
"""

import argparse
from pathlib import Path
import shutil
import subprocess
import sys
from typing import List, Optional

from rich.console import Console

from kapsel.storage.config import get_kapsel_dir
from kapsel.ui.banner import ensure_utf8_io

ensure_utf8_io()
console = Console(legacy_windows=False)


def run_git(args: List[str], cwd: Path) -> subprocess.CompletedProcess:
    """Executes a git command in the specified directory."""
    return subprocess.run(
        ["git"] + args,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def scaffold_new_plugin(plugin_name: str, src_dir: Path) -> Path:
    """Scaffolds a new plugin directory structure with boilerplate code in English."""
    plugin_dir = src_dir / plugin_name
    if plugin_dir.exists():
        console.print(f"[yellow]Plugin directory '{plugin_dir}' already exists.[/]")
        return plugin_dir

    plugin_dir.mkdir(parents=True, exist_ok=True)
    class_name = "".join(part.capitalize() for part in plugin_name.replace("-", "_").split("_")) + "Plugin"

    # 1. plugin.py
    (plugin_dir / "plugin.py").write_text(
        f'''"""
{plugin_name.capitalize()} Plugin for Kapsel.
All comments and descriptions are in English.
"""

from typing import List, Optional
from rich.console import Console

from kapsel.core.plugin.base import KapselPlugin, PluginManifest
from kapsel.core.plugin.context import PluginContext


class {class_name}(KapselPlugin):
    """Kapsel {plugin_name} feature plugin."""

    manifest = PluginManifest(
        id="{plugin_name}",
        name="{plugin_name.capitalize()}",
        version="0.1.0",
        description="Feature plugin for Kapsel shell.",
        author="Kapsel Team",
        min_kapsel_version="0.1.0",
        tags=["tools", "{plugin_name}"],
    )

    def on_load(self, context: PluginContext) -> None:
        """Register functional commands under the 'kps' scope."""
        context.register_kps_command(
            name="{plugin_name}",
            handler=self.handle_command,
            help_text="Execute {plugin_name} functional command",
            usage="kps {plugin_name} [options]",
            scope="feature",
        )

    def handle_command(self, args: List[str], console: Optional[Console] = None) -> int:
        con = console or Console(legacy_windows=False)
        con.print(f"[bold #00f0ff]Hello from {plugin_name} plugin![/] Args: {{args}}")
        return 0
''',
        encoding="utf-8",
    )

    # 2. __init__.py
    (plugin_dir / "__init__.py").write_text(
        f'''"""Plugin package entry point."""
from .plugin import {class_name} as Plugin

__all__ = ["Plugin"]
''',
        encoding="utf-8",
    )

    # 3. pyproject.toml
    (plugin_dir / "pyproject.toml").write_text(
        f'''[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "kapsel-plugin-{plugin_name}"
version = "0.1.0"
description = "Kapsel plugin: {plugin_name}"
authors = [{{ name = "Kapsel Team" }}]
license = {{ text = "MIT" }}
dependencies = []
''',
        encoding="utf-8",
    )

    # 4. README.md
    (plugin_dir / "README.md").write_text(
        f'''# {plugin_name.capitalize()} Plugin for Kapsel

Feature plugin providing `{plugin_name}` integration for the Kapsel shell environment.

## Usage

```bash
# Enable the plugin
kapsel add {plugin_name}

# Use the feature command
kps {plugin_name}
```
''',
        encoding="utf-8",
    )

    console.print(f"[bold #10b981]✔ Scaffolding for '[#00f0ff]{plugin_name}[/]' created successfully.[/]")
    return plugin_dir


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


def git_commit_and_push(repo_dir: Path, commit_msg: str) -> bool:
    """Runs git add, commit, and push in the external repository."""
    if not (repo_dir / ".git").exists():
        console.print(f"[yellow]'{repo_dir}' is not a git repository. Skipping git push.[/]")
        return False

    console.print(f"\n[bold #a855f7]📦 Git Sync for External Repository:[/] [dim]{repo_dir}[/]")

    # Check status
    st = run_git(["status", "--porcelain"], repo_dir)
    if not st.stdout.strip():
        console.print("  [dim]Working tree clean; no uncommitted changes to push.[/]")
        return True

    # Git add
    add_res = run_git(["add", "-A"], repo_dir)
    if add_res.returncode != 0:
        console.print(f"  [bold #f43f5e]git add failed:[/] {add_res.stderr}")
        return False
    console.print("  [bold #10b981]✔[/] git add -A")

    # Git commit
    commit_res = run_git(["commit", "-m", commit_msg], repo_dir)
    if commit_res.returncode != 0:
        console.print(f"  [bold #f43f5e]git commit failed:[/] {commit_res.stderr}")
        return False
    console.print(f"  [bold #10b981]✔[/] git commit -m '{commit_msg}'")

    # Git push
    console.print("  [dim]Pushing to remote origin...[/]")
    push_res = run_git(["push", "origin", "master"], repo_dir)
    if push_res.returncode != 0:
        # Try 'main' branch if 'master' fails
        push_res = run_git(["push", "origin", "main"], repo_dir)

    if push_res.returncode == 0:
        console.print("  [bold #10b981]🚀 Successfully pushed changes to remote repository![/]")
        return True
    else:
        console.print(f"  [bold #f43f5e]git push failed:[/] {push_res.stderr.strip() or push_res.stdout.strip()}")
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Synchronize and publish Kapsel development plugins.")
    parser.add_argument("plugin", nargs="?", default=None, help="Name of specific plugin to sync (default: all)")
    parser.add_argument("--new", type=str, default=None, help="Create and scaffold a new plugin boilerplate")
    parser.add_argument(
        "-m", "--message", type=str, default=None, help="Custom git commit message for publishing"
    )
    parser.add_argument(
        "--push",
        action="store_true",
        default=True,
        help="Automatically commit and push to remote repository (enabled by default)",
    )
    parser.add_argument(
        "--no-push",
        action="store_false",
        dest="push",
        help="Do not git commit or push after syncing",
    )
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

    # Handle --new scaffold
    if args.new:
        target_plugin = args.new.strip().lower()
        scaffold_new_plugin(target_plugin, src_dir)
        args.plugin = target_plugin

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
        f"\n[bold #10b981]✨ Synchronized {success_count}/{len(plugins_to_sync)} plugin(s).[/]"
    )

    # Git commit and push to external repo
    if args.push:
        plugin_desc = args.plugin if args.plugin else "all"
        msg = args.message or f"feat/update: sync {plugin_desc} plugin"
        git_commit_and_push(desktop_plugins_dir, msg)

    return 0


if __name__ == "__main__":
    sys.exit(main())
