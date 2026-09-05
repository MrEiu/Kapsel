"""
Kapsel Upgrade Command: 'kapsel upgrade [plugin_name]'.
Performs two-stage update checks:
1. Checks Kapsel Core updates against GitHub Releases & PyPI with changelog/release notes.
2. Checks official plugins updates against remote catalog.json with update descriptions (changelog).
Supports targeting a specific plugin: 'kapsel upgrade <plugin_name>'.
All comments and descriptions are in English.
"""

import json
from pathlib import Path
import re
import sys
from typing import Any, Dict, List, Optional, Tuple
import urllib.request
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from kapsel import __version__ as CURRENT_KAPSEL_VERSION
from kapsel.core.plugin.catalog import (
    load_plugin_catalog_rich,
    _extract_plugin_version,
)
from kapsel.core.plugin.fetcher import fetch_plugin_from_remote
from kapsel.storage.config import get_kapsel_dir, load_config
from kapsel.ui.banner import ensure_utf8_io

ensure_utf8_io()

# Remote endpoints for Kapsel Core releases
KAPSEL_GITHUB_RELEASE_API = "https://api.github.com/repos/MrEiu/Kapsel/releases/latest"
KAPSEL_GITHUB_RELEASE_MIRROR_API = "https://ghproxy.net/https://api.github.com/repos/MrEiu/Kapsel/releases/latest"
KAPSEL_PYPI_JSON_API = "https://pypi.org/pypi/kapsel-cli/json"
KAPSEL_PYPI_MIRROR_JSON_API = "https://pypi.tuna.tsinghua.edu.cn/pypi/kapsel-cli/json"

# Remote endpoints for official plugins catalog
OFFICIAL_PLUGINS_CATALOG_URL = "https://raw.githubusercontent.com/MrEiu/plugins/master/catalog.json"
OFFICIAL_PLUGINS_CATALOG_MIRROR_URL = "https://ghproxy.net/https://raw.githubusercontent.com/MrEiu/plugins/master/catalog.json"


def _parse_semver(ver_str: str) -> Tuple[int, ...]:
    """Parses a semver version string into an integer tuple for accurate comparison."""
    clean = re.sub(r"^[vV]", "", ver_str.strip())
    # Extract only numeric version parts e.g. "0.2.1" from "0.2.1-beta"
    parts = []
    for part in clean.split("."):
        num_m = re.match(r"^(\d+)", part)
        if num_m:
            parts.append(int(num_m.group(1)))
        else:
            parts.append(0)
    return tuple(parts) if parts else (0, 0, 0)


def _fetch_url_json(urls: List[str], timeout: float = 6.0) -> Optional[Dict[str, Any]]:
    """Attempts HTTP GET requests against candidate URLs with timeouts and headers."""
    headers = {"User-Agent": f"Kapsel-Upgrade/{CURRENT_KAPSEL_VERSION}"}
    for url in urls:
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    if isinstance(data, dict):
                        return data
        except Exception:
            continue
    return None


def check_kapsel_core_update() -> Dict[str, Any]:
    """
    Checks if a newer version of Kapsel Core is available on GitHub Releases or PyPI.
    Returns: { "has_update": bool, "current": str, "latest": str, "notes": str, "published_at": str }
    """
    res = {
        "has_update": False,
        "current": CURRENT_KAPSEL_VERSION,
        "latest": CURRENT_KAPSEL_VERSION,
        "notes": "",
        "published_at": "",
    }

    # 1. Try GitHub Releases API first (provides rich release notes)
    gh_data = _fetch_url_json([KAPSEL_GITHUB_RELEASE_API, KAPSEL_GITHUB_RELEASE_MIRROR_API])
    if gh_data and "tag_name" in gh_data:
        latest_tag = gh_data["tag_name"]
        latest_ver = re.sub(r"^[vV]", "", latest_tag)
        res["latest"] = latest_ver
        res["notes"] = gh_data.get("body", "").strip()
        res["published_at"] = gh_data.get("published_at", "")[:10]
        if _parse_semver(latest_ver) > _parse_semver(CURRENT_KAPSEL_VERSION):
            res["has_update"] = True
            return res

    # 2. Fallback to PyPI JSON API
    pypi_data = _fetch_url_json([KAPSEL_PYPI_JSON_API, KAPSEL_PYPI_MIRROR_JSON_API])
    if pypi_data and "info" in pypi_data:
        info = pypi_data["info"]
        latest_ver = info.get("version", CURRENT_KAPSEL_VERSION)
        res["latest"] = latest_ver
        if not res["notes"]:
            res["notes"] = info.get("summary", "")
        if _parse_semver(latest_ver) > _parse_semver(CURRENT_KAPSEL_VERSION):
            res["has_update"] = True
            return res

    return res


def fetch_remote_plugin_catalog() -> Dict[str, Dict[str, Any]]:
    """
    Fetches the latest official plugins catalog from GitHub/mirror.
    Falls back to local catalog if network is unavailable.
    """
    remote_data = _fetch_url_json([OFFICIAL_PLUGINS_CATALOG_URL, OFFICIAL_PLUGINS_CATALOG_MIRROR_URL])
    if remote_data:
        result: Dict[str, Dict[str, Any]] = {}
        for k, v in remote_data.items():
            if k.startswith(("_", "$")):
                continue
            if isinstance(v, dict):
                result[k] = {
                    "version": v.get("version", "0.1.0"),
                    "description": v.get("description", f"Plugin {k}"),
                    "changelog": v.get("changelog", ""),
                }
            else:
                result[k] = {
                    "version": "0.1.0",
                    "description": str(v),
                    "changelog": "",
                }
        return result

    # Fallback to local catalog
    return load_plugin_catalog_rich()


def check_plugins_update(target_plugin: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Checks for updates across installed plugins (or a single targeted plugin).
    Returns list of update items: [{ "name": str, "current": str, "latest": str, "has_update": bool, "changelog": str, "dir": Path }]
    """
    remote_catalog = fetch_remote_plugin_catalog()
    installed_plugins: Dict[str, Path] = {}

    # Inspect global data directory plugins
    data_plugins = get_kapsel_dir() / "plugins"
    if data_plugins.is_dir():
        for item in data_plugins.iterdir():
            if item.is_dir() and not item.name.startswith((".", "__")):
                installed_plugins[item.name.lower()] = item

    # Inspect workspace plugins if present
    workspace_plugins = Path.cwd() / "plugins"
    if workspace_plugins.is_dir():
        for item in workspace_plugins.iterdir():
            if item.is_dir() and not item.name.startswith((".", "__")):
                if item.name.lower() not in installed_plugins:
                    installed_plugins[item.name.lower()] = item

    results: List[Dict[str, Any]] = []

    plugins_to_check = [target_plugin.lower()] if target_plugin else sorted(installed_plugins.keys())

    for pid in plugins_to_check:
        p_dir = installed_plugins.get(pid)
        current_ver = _extract_plugin_version(p_dir) if p_dir else "0.0.0"
        remote_meta = remote_catalog.get(pid, {})
        latest_ver = remote_meta.get("version", current_ver)
        changelog = remote_meta.get("changelog", "")
        desc = remote_meta.get("description", "")

        has_update = _parse_semver(latest_ver) > _parse_semver(current_ver)

        results.append({
            "name": pid,
            "current": current_ver,
            "latest": latest_ver,
            "has_update": has_update,
            "changelog": changelog,
            "description": desc,
            "dir": p_dir,
            "is_installed": p_dir is not None,
        })

    return results


def handle_upgrade(args: List[str], console: Optional[Console] = None) -> int:
    """
    Handles 'kapsel upgrade [plugin_name]' system command.
    Two-stage upgrade:
      1. Kapsel Core updates & release notes
      2. Official plugins updates & changelogs
    Or targets a specific plugin if provided.
    """
    con = console or Console(legacy_windows=False)
    check_only = "--check" in args or "-c" in args
    clean_args = [a for a in args if a not in ("--check", "-c", "-h", "--help")]

    target_plugin = clean_args[0].lower() if clean_args else None

    # ==========================================================================
    # Mode A: Targeted Upgrade for a Specific Plugin ('kapsel upgrade <name>')
    # ==========================================================================
    if target_plugin:
        con.print(f"\n[bold #00f0ff]🔍 Checking updates for plugin '[white]{target_plugin}[/]'...[/]")
        plugin_updates = check_plugins_update(target_plugin=target_plugin)
        if not plugin_updates:
            con.print(f"[bold #f43f5e]Error:[/] Unknown plugin '{target_plugin}'. Run 'kapsel search' to browse official plugins.\n")
            return 1

        info = plugin_updates[0]
        if not info["is_installed"]:
            con.print(f"[yellow]Plugin '[bold #00f0ff]{target_plugin}[/]' is not currently installed.[/]")
            con.print(f"[dim]Run 'kapsel add {target_plugin}' to install it.[/]\n")
            return 1

        if not info["has_update"]:
            con.print(f"[bold #10b981]✔ Plugin '[bold #00f0ff]{target_plugin}[/]' is already at the latest version (v{info['current']}).[/]\n")
            return 0

        # Update available for this plugin
        con.print(f"\n[bold #00f0ff]📦 Plugin Update Available:[/] [white]{target_plugin}[/] "
                  f"([dim]v{info['current']}[/] -> [bold #10b981]v{info['latest']}[/])")

        if info["changelog"]:
            con.print(Panel(
                f"[white]{info['changelog']}[/]",
                title=f"[bold #a855f7]📝 Update Notes (更新说明)[/]",
                border_style="#0891b2",
                padding=(0, 1),
            ))

        if check_only:
            con.print("[dim]Check-only mode. Skipping download.[/]\n")
            return 0

        # Perform plugin update download
        dest_dir = info["dir"] or (get_kapsel_dir() / "plugins" / target_plugin)
        con.print(f"[dim]Downloading and updating plugin package...[/]")
        if fetch_plugin_from_remote(target_plugin, dest_dir, con):
            try:
                from kapsel.completion.spec_manager import CarapaceSpecManager
                CarapaceSpecManager().sync_specs()
            except Exception:
                pass
            con.print(f"[bold #10b981]✔ Plugin '[bold #00f0ff]{target_plugin}[/]' successfully updated to v{info['latest']}![/]\n")
            return 0
        else:
            con.print(f"[bold #f43f5e]✘ Failed to download update for '{target_plugin}'.[/]\n")
            return 1

    # ==========================================================================
    # Mode B: Full System & Plugins Upgrade ('kapsel upgrade')
    # ==========================================================================
    con.print("\n[bold #00f0ff]============================================================[/]")
    con.print("[bold #00f0ff]   🚀 Kapsel System & Official Plugins Upgrade Inspector   [/]")
    con.print("[bold #00f0ff]============================================================[/]\n")

    # --------------------------------------------------------------------------
    # Step 1: Check Kapsel Core Update
    # --------------------------------------------------------------------------
    con.print("[bold #00f0ff]1. Checking Kapsel Core System Updates...[/]")
    core_info = check_kapsel_core_update()

    if core_info["has_update"]:
        con.print(f"  [bold #f59e0b]⚡ New Kapsel version available:[/] "
                  f"[dim]v{core_info['current']}[/] -> [bold #10b981]v{core_info['latest']}[/]")
        if core_info["published_at"]:
            con.print(f"  [dim]Released on: {core_info['published_at']}[/]")

        if core_info["notes"]:
            con.print(Panel(
                f"[white]{core_info['notes']}[/]",
                title=f"[bold #a855f7]📝 Kapsel v{core_info['latest']} Release Notes (更新说明)[/]",
                border_style="#f59e0b",
                padding=(0, 1),
            ))

        con.print("  [bold #00f0ff]To upgrade Kapsel Core, run:[/] [bold white]pip install -U kapsel-cli[/]\n")
    else:
        con.print(f"  [bold #10b981]✔ Kapsel Core is up to date (v{CURRENT_KAPSEL_VERSION}).[/]\n")

    # --------------------------------------------------------------------------
    # Step 2: Check Official Plugins Updates
    # --------------------------------------------------------------------------
    con.print("[bold #00f0ff]2. Checking Official Plugins Updates...[/]")
    plugin_updates = check_plugins_update()

    updates_found = [p for p in plugin_updates if p["has_update"]]

    if not updates_found:
        con.print(f"  [bold #10b981]✔ All {len(plugin_updates)} installed official plugins are up to date.[/]\n")
        return 0

    con.print(f"  [bold #f59e0b]Found {len(updates_found)} plugin(s) with available updates:[/]\n")

    table = Table(
        title="[bold #00f0ff]📦 Plugins Update Summary[/]",
        border_style="#0891b2",
        header_style="bold #00f0ff",
    )
    table.add_column("Plugin", style="bold #00f0ff", width=12)
    table.add_column("Current", style="dim", justify="center", width=10)
    table.add_column("Latest", style="bold #10b981", justify="center", width=10)
    table.add_column("Update Description / Changelog", style="white")

    for p in updates_found:
        note = p["changelog"] or p["description"] or "Plugin bug fixes and performance improvements."
        table.add_row(
            p["name"],
            f"v{p['current']}",
            f"v{p['latest']}",
            note,
        )

    con.print(table)
    con.print()

    if check_only:
        con.print("[dim]Check-only mode. Run 'kapsel upgrade' without flags to apply updates.[/]\n")
        return 0

    # Apply plugin updates
    success_count = 0
    for p in updates_found:
        con.print(f"[dim]Updating [bold #00f0ff]{p['name']}[/] to v{p['latest']}...[/]")
        dest_dir = p["dir"] or (get_kapsel_dir() / "plugins" / p["name"])
        if fetch_plugin_from_remote(p["name"], dest_dir, con):
            success_count += 1
            con.print(f"  [bold #10b981]✔ Updated {p['name']} to v{p['latest']}[/]")
        else:
            con.print(f"  [bold #f43f5e]✘ Failed to update {p['name']}[/]")

    # Re-sync completion specifications
    try:
        from kapsel.completion.spec_manager import CarapaceSpecManager
        CarapaceSpecManager().sync_specs()
    except Exception:
        pass

    con.print(f"\n[bold #10b981]✨ Successfully updated {success_count}/{len(updates_found)} plugin(s)![/]\n")
    return 0
