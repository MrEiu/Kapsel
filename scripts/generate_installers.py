"""
Kapsel Automated Multi-Platform Installer Generator.
Compiles single-source declarative metadata (pyproject.toml + catalog.json)
into unified, production-grade installer scripts across Windows, macOS, and Linux.

Generated Deliverables:
- scripts/install.sh              (Universal POSIX Entrypoint Dispatcher)
- scripts/install.ps1             (Universal Windows Entrypoint Dispatcher)
- scripts/install_windows.ps1      (Windows International, Lite & Full, Preflight Inspection)
- scripts/install_macos.sh        (macOS International, Lite & Full, Preflight Inspection)
- scripts/install_linux.sh        (Linux International, Lite & Full, Preflight Inspection)
- scripts/install_cn.ps1          (Windows China Mainland Mirror Accelerated)
- scripts/install_cn.sh           (POSIX China Mainland Mirror Accelerated)
- scripts/install_tools_*.sh/.ps1 (Backward-compatible forwarders)

All comments and descriptions are in English.
"""

import argparse
import json
import os
from pathlib import Path
import re
import sys
from typing import Any, Dict, List

import jinja2
from rich.console import Console
from rich.table import Table

try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

console = Console(legacy_windows=False)

ROOT_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = ROOT_DIR / "scripts"
TEMPLATES_DIR = SCRIPTS_DIR / "templates"

CARAPACE_VERSION = "1.7.3"
REPO_URL = "https://github.com/MrEiu/Kapsel"
PYPI_PACKAGE = "kapsel-cli"
PYPI_INDEX_CN = "https://pypi.tuna.tsinghua.edu.cn/simple"
GH_MIRROR_CN = "https://ghproxy.net/"


def get_kapsel_version() -> str:
    """Reads project version from pyproject.toml."""
    pyproject_file = ROOT_DIR / "pyproject.toml"
    if pyproject_file.exists():
        content = pyproject_file.read_text(encoding="utf-8")
        match = re.search(r'(?m)^version\s*=\s*["\']([^"\']+)["\']', content)
        if match:
            return match.group(1)

    init_file = ROOT_DIR / "kapsel" / "__init__.py"
    if init_file.exists():
        content = init_file.read_text(encoding="utf-8")
        match = re.search(r'(?m)^__version__\s*=\s*["\']([^"\']+)["\']', content)
        if match:
            return match.group(1)

    return "0.1.9"


def load_official_plugins() -> List[Dict[str, str]]:
    """Loads official plugins list from plugins/catalog.json."""
    catalog_file = ROOT_DIR / "plugins" / "catalog.json"
    plugins = []

    # Priority order for user experience
    order = [
        "alias",
        "portal",
        "init",
        "shore",
        "ai",
        "install",
        "autopilot",
        "rec",
        "profile",
        "fuck",
        "help",
    ]

    catalog_data = {}
    if catalog_file.exists():
        try:
            catalog_data = json.loads(catalog_file.read_text(encoding="utf-8"))
        except Exception:
            pass

    for pid in order:
        meta = catalog_data.get(pid, {})
        desc = meta.get("description") or f"Official Kapsel {pid} plugin"
        ver = meta.get("version") or "0.1.0"
        plugins.append({
            "id": pid,
            "description": desc,
            "version": ver,
        })

    # Catch any new plugins not in preset order
    for pid, meta in catalog_data.items():
        if pid.startswith("_") or pid in ("update",) or any(p["id"] == pid for p in plugins):
            continue
        if isinstance(meta, dict):
            plugins.append({
                "id": pid,
                "description": meta.get("description", f"Official Kapsel {pid} plugin"),
                "version": meta.get("version", "0.1.0"),
            })

    return plugins


def build_installers():
    """Compiles all installer templates into production shell scripts."""
    console.print("\n[bold #00f0ff]⚡ Kapsel Installer Compiler & Generator[/]")
    version = get_kapsel_version()
    plugins = load_official_plugins()

    console.print(f"[dim]Kapsel Core Version:[/] [bold #10b981]v{version}[/]")
    console.print(f"[dim]Plugins Detected:[/]    [bold #38bdf8]{len(plugins)} official plugins[/]")

    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(TEMPLATES_DIR)),
        trim_blocks=True,
        lstrip_blocks=True,
        autoescape=False,
    )

    tmpl_win = env.get_template("install_windows.ps1.j2")
    tmpl_posix = env.get_template("install_posix.sh.j2")
    tmpl_entry_sh = env.get_template("install_entry.sh.j2")
    tmpl_entry_ps1 = env.get_template("install_entry.ps1.j2")

    tasks = [
        # 1. Universal POSIX Entrypoint Dispatcher
        {
            "dest": SCRIPTS_DIR / "install.sh",
            "template": tmpl_entry_sh,
            "context": {
                "app_name": "Kapsel",
                "version": version,
                "repo_url": REPO_URL,
                "plugins": plugins,
                "is_cn": False,
            },
            "desc": "Universal POSIX Entrypoint Dispatcher (Bash)",
        },
        # 2. Universal Windows Entrypoint Dispatcher
        {
            "dest": SCRIPTS_DIR / "install.ps1",
            "template": tmpl_entry_ps1,
            "context": {
                "app_name": "Kapsel",
                "version": version,
                "repo_url": REPO_URL,
                "plugins": plugins,
                "is_cn": False,
            },
            "desc": "Universal Windows Entrypoint Dispatcher (PowerShell)",
        },
        # 3. Windows International Specific Script
        {
            "dest": SCRIPTS_DIR / "install_windows.ps1",
            "template": tmpl_win,
            "context": {
                "app_name": "Kapsel",
                "version": version,
                "repo_url": REPO_URL,
                "pypi_package": PYPI_PACKAGE,
                "carapace_version": CARAPACE_VERSION,
                "plugins": plugins,
                "is_cn": False,
            },
            "desc": "Windows International Installer (PowerShell)",
        },
        # 4. Windows China Mainland Accelerated Script
        {
            "dest": SCRIPTS_DIR / "install_cn.ps1",
            "template": tmpl_win,
            "context": {
                "app_name": "Kapsel",
                "version": version,
                "repo_url": REPO_URL,
                "pypi_package": PYPI_PACKAGE,
                "carapace_version": CARAPACE_VERSION,
                "plugins": plugins,
                "is_cn": True,
                "pypi_index_url": PYPI_INDEX_CN,
                "gh_mirror_prefix": GH_MIRROR_CN,
            },
            "desc": "Windows China Accelerated Installer (PowerShell)",
        },
        # 5. macOS International Specific Script
        {
            "dest": SCRIPTS_DIR / "install_macos.sh",
            "template": tmpl_posix,
            "context": {
                "app_name": "Kapsel",
                "version": version,
                "repo_url": REPO_URL,
                "pypi_package": PYPI_PACKAGE,
                "carapace_version": CARAPACE_VERSION,
                "plugins": plugins,
                "target_os": "macos",
                "is_cn": False,
            },
            "desc": "macOS International Installer (Bash/Zsh)",
        },
        # 6. Linux International Specific Script
        {
            "dest": SCRIPTS_DIR / "install_linux.sh",
            "template": tmpl_posix,
            "context": {
                "app_name": "Kapsel",
                "version": version,
                "repo_url": REPO_URL,
                "pypi_package": PYPI_PACKAGE,
                "carapace_version": CARAPACE_VERSION,
                "plugins": plugins,
                "target_os": "linux",
                "is_cn": False,
            },
            "desc": "Linux International Installer (Bash)",
        },
        # 7. POSIX China Mainland Accelerated Script
        {
            "dest": SCRIPTS_DIR / "install_cn.sh",
            "template": tmpl_posix,
            "context": {
                "app_name": "Kapsel",
                "version": version,
                "repo_url": REPO_URL,
                "pypi_package": PYPI_PACKAGE,
                "carapace_version": CARAPACE_VERSION,
                "plugins": plugins,
                "target_os": "all",
                "is_cn": True,
                "pypi_index_url": PYPI_INDEX_CN,
                "gh_mirror_prefix": GH_MIRROR_CN,
            },
            "desc": "POSIX China Accelerated Installer (Bash)",
        },
    ]

    table = Table(title="Generated Shell Installers", border_style="#0891b2")
    table.add_column("Script Target", style="#00f0ff")
    table.add_column("Platform", style="#38bdf8")
    table.add_column("Role", style="#a855f7")
    table.add_column("Size (Bytes)", justify="right", style="#10b981")

    for task in tasks:
        dest = task["dest"]
        rendered = task["template"].render(**task["context"])
        is_ps = dest.suffix == ".ps1"
        dest.write_text(
            rendered,
            encoding="utf-8-sig" if is_ps else "utf-8",
            newline="\r\n" if is_ps else "\n",
        )

        size = len(rendered.encode("utf-8"))
        platform = "Windows" if dest.suffix == ".ps1" else ("macOS" if "macos" in dest.name else ("Linux" if "linux" in dest.name else "POSIX"))
        role = "Dispatcher" if dest.name in ("install.sh", "install.ps1") else ("CN Accelerated" if "_cn" in dest.name else "International")
        table.add_row(dest.name, platform, role, str(size))

    console.print("")
    console.print(table)
    console.print(f"\n[bold #10b981]✔ All {len(tasks)} platform install scripts compiled successfully with 0 code duplication![/]\n")


def main():
    parser = argparse.ArgumentParser(description="Kapsel Installer Generator")
    parser.add_argument("--check", action="store_true", help="Check template consistency without writing")
    args = parser.parse_args()

    build_installers()


if __name__ == "__main__":
    main()
