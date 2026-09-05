"""
Kapsel Search Command (`kps search` / `kapsel search`).
Provides intelligent fuzzy search across the Kapsel plugin ecosystem,
available tools, extensions, and metadata catalog.
All comments and descriptions are in English.
"""

from pathlib import Path
import re
from typing import Any, Dict, List, Optional
from rich.console import Console
from rich.table import Table

from kapsel.core.plugin.catalog import load_plugin_catalog, load_plugin_catalog_rich
from kapsel.storage.config import get_kapsel_dir, load_config
from kapsel.ui.banner import ensure_utf8_io

ensure_utf8_io()

# Extended metadata dictionary for fuzzy matching and categorization
PLUGIN_METADATA: Dict[str, Dict[str, Any]] = {
    "init": {
        "title": "Init & Toolchains",
        "tool": "mise (Rust)",
        "category": "Runtime Manager",
        "tags": ["runtime", "toolchain", "version", "mise", "node", "python", "java", "ruby", "go", "env"],
        "summary": "Project polyglot development environment and toolchain runtime initializer (powered by mise).",
    },
    "portal": {
        "title": "Portal Navigation",
        "tool": "zoxide (Rust)",
        "category": "Navigation",
        "tags": ["cd", "jump", "teleport", "zoxide", "fzf", "directory", "navigation", "frecency", "workspace"],
        "summary": "Frecency-based smart directory teleportation and workspace navigator (powered by zoxide).",
    },
    "shore": {
        "title": "Shore Mirror Switcher",
        "tool": "chsrc (C)",
        "category": "Mirror & Network",
        "tags": ["mirror", "source", "chsrc", "pypi", "npm", "cargo", "brew", "apt", "fast", "speedtest"],
        "summary": "Automated ultra-fast mirror source switcher for packages and OS distros (powered by chsrc).",
    },
    "install": {
        "title": "Universal Installer",
        "tool": "mpm (Python)",
        "category": "Package Manager",
        "tags": ["install", "package", "mpm", "scoop", "winget", "brew", "apt", "pacman", "dnf", "meta"],
        "summary": "Unified cross-platform package manager aggregating Scoop, Winget, Brew, Apt, and 20+ managers.",
    },
    "alias": {
        "title": "Alias Translation",
        "tool": "Native Engine",
        "category": "Command Mapping",
        "tags": ["alias", "mapping", "translation", "linux", "pwsh", "cmd", "bash", "filter"],
        "summary": "Universal command alias translation mapping Linux muscle memory to native host shells.",
    },
    "ai": {
        "title": "Terminal AI Assistant",
        "tool": "aichat (Rust)",
        "category": "AI & Copilot",
        "tags": ["ai", "copilot", "chat", "llm", "aichat", "openai", "claude", "gemini", "deepseek", "ollama"],
        "summary": "Terminal AI copilot with guided setup wizard, multi-model dialogue, and code synthesis.",
    },
    "autopilot": {
        "title": "Autopilot Queue",
        "tool": "pueue (Rust)",
        "category": "Task Management",
        "tags": ["task", "queue", "daemon", "background", "pueue", "pueued", "async", "worker", "job"],
        "summary": "Autonomous background task queue and daemon execution manager (powered by Pueue).",
    },
    "fuck": {
        "title": "Auto-Correction",
        "tool": "thefuck (Python)",
        "category": "Productivity",
        "tags": ["fix", "error", "typo", "thefuck", "correct", "history", "auto-fix"],
        "summary": "Intelligent command auto-correction and syntax fixing tool (powered by thefuck).",
    },
    "help": {
        "title": "Cheat Sheets",
        "tool": "tealdeer (Rust)",
        "category": "Documentation",
        "tags": ["help", "tldr", "tealdeer", "man", "cheat", "example", "doc", "lookup"],
        "summary": "Fast, practical command cheat sheets and quick lookup (powered by tealdeer/tldr).",
    },
    "profile": {
        "title": "Dotfile Manager",
        "tool": "chezmoi (Go)",
        "category": "Environment Sync",
        "tags": ["dotfile", "profile", "chezmoi", "config", "sync", "git", "secret", "roaming"],
        "summary": "Cross-platform dotfile, shell profile, and secret-encrypted environment manager (chezmoi).",
    },
    "rec": {
        "title": "Snippet Recorder",
        "tool": "pet (Go)",
        "category": "Snippets",
        "tags": ["snippet", "record", "pet", "macro", "runner", "history", "template", "bookmark"],
        "summary": "Interactive command snippet recorder, argument parameterizer, and runner (pet CLI).",
    },
}


def _get_installed_and_enabled_plugins() -> tuple[set[str], set[str]]:
    """Returns sets of (installed_plugin_ids, enabled_plugin_ids)."""
    installed = set()
    enabled = set()

    # Check local workspace
    local_plugins = Path.cwd() / "plugins"
    if local_plugins.is_dir():
        for item in local_plugins.iterdir():
            if item.is_dir() and not item.name.startswith((".", "__")):
                installed.add(item.name.lower())

    # Check user data dir
    data_plugins = get_kapsel_dir() / "plugins"
    if data_plugins.is_dir():
        for item in data_plugins.iterdir():
            if item.is_dir() and not item.name.startswith((".", "__")):
                installed.add(item.name.lower())

    cfg = load_config()
    if cfg.enabled_plugins:
        enabled.update(p.lower() for p in cfg.enabled_plugins)
    else:
        # Default behavior: all installed plugins are enabled if no explicit list
        enabled.update(installed)

    return installed, enabled


def handle_search(args: List[str], console: Optional[Console] = None) -> int:
    """
    Searches available plugins and tools using fuzzy matching.
    Usage:
      kapsel search [query]
      kps search [query] [-a | --all]
    """
    con = console or Console(legacy_windows=False)
    show_all = "--all" in args or "-a" in args
    clean_args = [a for a in args if a not in ("--all", "-a", "-h", "--help")]

    query = " ".join(clean_args).strip().lower()

    catalog = load_plugin_catalog()
    rich_catalog = load_plugin_catalog_rich()
    installed_set, enabled_set = _get_installed_and_enabled_plugins()

    # Combine all known plugin IDs
    all_plugin_ids = sorted(
        set(list(PLUGIN_METADATA.keys()) + [k for k in catalog.keys() if k != "update"])
    )

    matches: List[Dict[str, Any]] = []

    for pid in all_plugin_ids:
        meta = PLUGIN_METADATA.get(pid, {})
        title = meta.get("title", pid.capitalize())
        tool = meta.get("tool", "CLI Tool")
        category = meta.get("category", "Extension")
        tags = meta.get("tags", [])
        summary = meta.get("summary", catalog.get(pid, f"Kapsel {pid} plugin"))

        is_enabled = pid in enabled_set
        is_installed = pid in installed_set or is_enabled

        if is_enabled:
            status = "[bold #10b981]✔ Enabled[/]"
        elif is_installed:
            status = "[bold #00f0ff]Installed[/]"
        else:
            status = "[dim]Available[/]"

        ver = rich_catalog.get(pid, {}).get("version", "0.1.0")

        # Match criteria: if show_all or query is empty -> match everything
        if show_all or not query:
            matches.append({
                "id": pid,
                "title": title,
                "version": ver,
                "tool": tool,
                "category": category,
                "summary": summary,
                "status": status,
                "tags": tags,
            })
            continue

        # Search matching across id, title, tool, tags, category, summary, version
        searchable_text = f"{pid} {title} {tool} {category} {' '.join(tags)} {summary} v{ver}".lower()
        if query in searchable_text:
            matches.append({
                "id": pid,
                "title": title,
                "version": ver,
                "tool": tool,
                "category": category,
                "summary": summary,
                "status": status,
                "tags": tags,
            })

    if not matches:
        con.print(f"\n[bold #f43f5e]No matching plugins or tools found for query:[/] '{query}'")
        con.print("[dim]Tip: Run 'kapsel search --all' to inspect all available extensions.[/]\n")
        return 0

    table = Table(
        title=f"[bold #00f0ff]🔍 Kapsel Plugin Catalog Search Results[/] [dim]({len(matches)} matches)[/]",
        border_style="#0891b2",
        header_style="bold #00f0ff",
    )
    table.add_column("Plugin / Command", style="bold #00f0ff", min_width=14)
    table.add_column("Version", justify="center", style="bold #10b981", min_width=9)
    table.add_column("Category", style="dim", min_width=14)
    table.add_column("Backed Tool", style="bold #a855f7", min_width=12)
    table.add_column("Description", style="white")
    table.add_column("Status", justify="center", min_width=10)

    for m in matches:
        cmd_display = f"kps {m['id']}"
        table.add_row(
            cmd_display,
            f"v{m['version']}",
            m["category"],
            m["tool"],
            m["summary"],
            m["status"],
        )

    con.print()
    con.print(table)
    con.print(f"[dim]To install/enable a plugin: 'kapsel add <plugin_name>' | To search all: 'kapsel search -a'[/]\n")
    return 0
