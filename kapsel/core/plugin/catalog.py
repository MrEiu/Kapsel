"""
Kapsel Plugin System - Catalog & Discovery Engine.
Manages repository subcommands dictionary and handles 'kapsel add update'.
All comments and descriptions are in English.
"""

import json
from pathlib import Path
import re
from typing import Any, Dict, List, Optional
from rich.console import Console
from rich.table import Table

from kapsel.storage.config import get_kapsel_dir


DEFAULT_CATALOG: Dict[str, str] = {
    "update": "Scan and update available plugin catalog and completion dictionary",
    "ai": "Terminal AI assistant and setup wizard (aichat)",
    "alias": "Cross-platform Linux command alias mapper",
    "autopilot": "Background task queue and autonomous execution (Pueue)",
    "fuck": "Intelligent console command error correction (thefuck)",
    "help": "Fast interactive command cheat sheets (tealdeer)",
    "init": "Project polyglot development environment and toolchain runtime initializer (mise)",
    "install": "Unified cross-platform package manager (mpm)",
    "portal": "Smart directory teleportation and workspace navigator (zoxide)",
    "profile": "Dotfiles and workspace sync roaming (chezmoi)",
    "rec": "Snippet recorder and interactive runner (pet)",
    "shore": "Fast intelligent mirror source switcher (chsrc)",
}



def _resolve_catalog_paths():
    """Returns candidate paths for catalog.json in order of priority."""
    paths = []
    # 1. Local workspace plugins folder
    workspace_catalog = Path.cwd() / "plugins" / "catalog.json"
    paths.append(workspace_catalog)

    # 2. Global runtime data directory
    global_catalog = get_kapsel_dir() / "plugins_catalog.json"
    paths.append(global_catalog)

    global_in_plugins = get_kapsel_dir() / "plugins" / "catalog.json"
    paths.append(global_in_plugins)

    return paths


def load_plugin_catalog() -> Dict[str, str]:
    """
    Loads the subcommands dictionary from catalog.json in the repository or runtime data directory.
    Returns a dictionary mapping plugin_id -> description (string) for backward compatibility.
    """
    rich_catalog = load_plugin_catalog_rich()
    return {k: v.get("description", str(v)) for k, v in rich_catalog.items()}


def load_plugin_catalog_rich() -> Dict[str, Dict[str, Any]]:
    """
    Loads the rich metadata catalog (version, description, changelog) from catalog.json.
    Gracefully handles both old format (string values) and new format (dict values).
    """
    for candidate in _resolve_catalog_paths():
        if candidate.exists() and candidate.is_file():
            try:
                data = json.loads(candidate.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    result: Dict[str, Dict[str, Any]] = {}
                    for k, v in data.items():
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
                    # Ensure 'update' entry is always present
                    result.setdefault("update", {
                        "version": "0.1.0",
                        "description": "Scan and update available plugin catalog and completion dictionary",
                        "changelog": "Catalog dictionary update scanner.",
                    })
                    return result
            except Exception:
                pass

    # If file not present yet, return default catalog converted to rich format
    return {
        k: {
            "version": "0.2.0" if k in ("alias", "install") else "0.1.0",
            "description": v,
            "changelog": "",
        }
        for k, v in DEFAULT_CATALOG.items()
    }


def _extract_plugin_version(plugin_dir: Path) -> str:
    """Extracts version string from plugin manifest, pyproject.toml, or __init__.py."""
    # 1. Try reading manifest in plugin.py
    plugin_py = plugin_dir / "plugin.py"
    if plugin_py.exists():
        try:
            content = plugin_py.read_text(encoding="utf-8", errors="ignore")
            m = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
            if m:
                return m.group(1).strip()
        except Exception:
            pass

    # 2. Try pyproject.toml
    pyproject = plugin_dir / "pyproject.toml"
    if pyproject.exists():
        try:
            content = pyproject.read_text(encoding="utf-8", errors="ignore")
            m = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
            if m:
                return m.group(1).strip()
        except Exception:
            pass

    return "0.1.0"


def _extract_plugin_description(plugin_dir: Path) -> str:
    """Extracts a human-readable description for a plugin from manifest, pyproject.toml, or docstring."""
    plugin_name = plugin_dir.name

    # 1. Try reading manifest in plugin.py
    plugin_py = plugin_dir / "plugin.py"
    if plugin_py.exists():
        try:
            content = plugin_py.read_text(encoding="utf-8", errors="ignore")
            m = re.search(r'description\s*=\s*["\']([^"\']+)["\']', content)
            if m:
                return m.group(1).strip()
        except Exception:
            pass

    # 2. Try pyproject.toml
    pyproject = plugin_dir / "pyproject.toml"
    if pyproject.exists():
        try:
            content = pyproject.read_text(encoding="utf-8", errors="ignore")
            m = re.search(r'description\s*=\s*["\']([^"\']+)["\']', content)
            if m:
                return m.group(1).strip()
        except Exception:
            pass

    # 3. Try __init__.py docstring
    init_py = plugin_dir / "__init__.py"
    if init_py.exists():
        try:
            content = init_py.read_text(encoding="utf-8", errors="ignore")
            doc_m = re.search(r'"""(.*?)"""', content, re.DOTALL)
            if doc_m:
                first_line = doc_m.group(1).strip().split("\n")[0].strip()
                if first_line:
                    return first_line
        except Exception:
            pass

    return f"Plugin: {plugin_name}"


def update_plugin_catalog(console: Optional[Console] = None) -> Dict[str, str]:
    """
    Scans the repository plugins/ folder, extracts plugin metadata (version & description),
    updates catalog.json, and refreshes the in-memory command registry.
    """
    con = console or Console(legacy_windows=False)
    existing_rich = load_plugin_catalog_rich()

    rich_catalog: Dict[str, Dict[str, Any]] = {
        "update": {
            "version": "0.1.0",
            "description": "Scan and update available plugin catalog and completion dictionary",
            "changelog": "Catalog dictionary update scanner.",
        }
    }

    # Search directories to scan
    scan_dirs = []
    workspace_plugins = Path.cwd() / "plugins"
    if workspace_plugins.exists() and workspace_plugins.is_dir():
        scan_dirs.append(workspace_plugins)

    global_plugins = get_kapsel_dir() / "plugins"
    if global_plugins.exists() and global_plugins.is_dir() and global_plugins not in scan_dirs:
        scan_dirs.append(global_plugins)

    for s_dir in scan_dirs:
        for item in sorted(s_dir.iterdir()):
            if item.is_dir() and not item.name.startswith((".", "_")):
                p_name = item.name.lower()
                if p_name not in rich_catalog:
                    desc = _extract_plugin_description(item)
                    ver = _extract_plugin_version(item)
                    prev_meta = existing_rich.get(p_name, {})
                    rich_catalog[p_name] = {
                        "version": ver or prev_meta.get("version", "0.1.0"),
                        "description": desc or prev_meta.get("description", f"Plugin: {p_name}"),
                        "changelog": prev_meta.get("changelog", ""),
                    }

    # Save to workspace plugins/catalog.json if workspace plugins directory exists
    if workspace_plugins.exists() and workspace_plugins.is_dir():
        target_file = workspace_plugins / "catalog.json"
        try:
            target_file.write_text(json.dumps(rich_catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        except Exception as e:
            con.print(f"[yellow]Warning: Failed to write {target_file}:[/] {e}")

    # Also save to global data directory cache
    global_cache = get_kapsel_dir() / "plugins_catalog.json"
    try:
        global_cache.parent.mkdir(parents=True, exist_ok=True)
        global_cache.write_text(json.dumps(rich_catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    except Exception as e:
        con.print(f"[yellow]Warning: Failed to write global cache {global_cache}:[/] {e}")

    flat_catalog = {k: v["description"] for k, v in rich_catalog.items()}

    # Hot-reload in-memory registry subcommands for 'add' command
    try:
        from kapsel.completion.kps.registry import get_kps_registry
        reg = get_kps_registry()
        add_cmd = reg.get("add")
        if add_cmd:
            add_cmd.subcommands = dict(flat_catalog)
    except Exception:
        pass

    return flat_catalog


def render_catalog_table(catalog: Dict[str, str], console: Console) -> None:
    """Renders the plugin catalog as a modern terminal table."""
    table = Table(
        title="[bold #00f0ff]📦 Kapsel Plugin Catalog (Subcommands Dictionary)[/]",
        border_style="#0891b2",
        header_style="bold #00f0ff",
        show_header=True,
    )
    table.add_column("Command / Plugin", style="bold #a855f7", width=18)
    table.add_column("Description", style="white")

    for name, desc in catalog.items():
        if name == "update":
            table.add_row(f"[bold #10b981]{name}[/]", f"[dim italic]{desc}[/]")
        else:
            table.add_row(name, desc)

    console.print()
    console.print(table)
    console.print(f"[dim]Total items: {len(catalog)} | Run [bold #00f0ff]kapsel add <plugin>[/] to enable any plugin.[/]\n")
