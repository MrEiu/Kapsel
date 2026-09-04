"""
Kapsel System Command: 'kapsel add <plugin_name>'.
Enables and registers plugins into the Kapsel environment.
All comments and descriptions are in English.
"""

from pathlib import Path
import shutil
from typing import List, Optional
from rich.console import Console
from rich.panel import Panel

from kapsel.storage.config import get_kapsel_dir, load_config, update_config_value
from kapsel.ui.banner import ensure_utf8_io


import os
import platform
import subprocess
import sys
import urllib.request


def _silently_install_mpm() -> bool:
    """
    Silently installs meta-package-manager using best available methods:
    1. Native package managers (Scoop on Windows, Homebrew on macOS/Linux)
    2. Python pip (if Python environment is available)
    3. Official standalone binary download from GitHub Releases
    """
    bin_dir = get_kapsel_dir() / "bin"
    is_win = sys.platform == "win32"
    local_mpm = bin_dir / ("mpm.exe" if is_win else "mpm")

    if shutil.which("mpm") or local_mpm.exists():
        return True

    # 1. Native package managers (Scoop / Homebrew)
    if is_win and shutil.which("scoop"):
        try:
            res = subprocess.run(
                ["scoop", "install", "main/meta-package-manager"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=90,
            )
            if res.returncode == 0 and shutil.which("mpm"):
                return True
        except Exception:
            pass
    elif (sys.platform == "darwin" or sys.platform.startswith("linux")) and shutil.which("brew"):
        try:
            res = subprocess.run(
                ["brew", "install", "meta-package-manager"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=90,
            )
            if res.returncode == 0 and shutil.which("mpm"):
                return True
        except Exception:
            pass

    # 2. Python pip
    try:
        res = subprocess.run(
            [sys.executable, "-m", "pip", "install", "meta-package-manager", "--quiet"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=120,
        )
        if res.returncode == 0:
            return True
    except Exception:
        pass

    # 3. Direct official standalone binary download (Zero-dependency fallback)
    try:
        bin_dir.mkdir(parents=True, exist_ok=True)
        machine = platform.machine().lower()
        is_arm = "arm" in machine or "aarch64" in machine

        if is_win:
            url = "https://github.com/kdeldycke/meta-package-manager/releases/latest/download/meta-package-manager-windows-x64.exe"
        elif sys.platform == "darwin":
            url = f"https://github.com/kdeldycke/meta-package-manager/releases/latest/download/meta-package-manager-macos-{'arm64' if is_arm else 'x64'}.bin"
        elif sys.platform.startswith("linux"):
            url = f"https://github.com/kdeldycke/meta-package-manager/releases/latest/download/meta-package-manager-linux-{'arm64' if is_arm else 'x64'}.bin"
        else:
            url = None

        if url:
            urllib.request.urlretrieve(url, local_mpm)
            if not is_win:
                os.chmod(local_mpm, 0o755)
            if local_mpm.exists():
                return True
    except Exception:
        pass

    return bool(shutil.which("mpm") or local_mpm.exists())


def _silently_install_pet() -> bool:
    """
    Silently installs the pet CLI snippet manager:
    1. Homebrew on macOS / Linux (if available)
    2. Official standalone tar.gz release from GitHub extracted to ~/.kapsel/bin/
    """
    bin_dir = get_kapsel_dir() / "bin"
    is_win = sys.platform == "win32"
    local_pet = bin_dir / ("pet.exe" if is_win else "pet")

    if shutil.which("pet") or local_pet.exists():
        return True

    # 1. Homebrew on macOS / Linux
    if (sys.platform == "darwin" or sys.platform.startswith("linux")) and shutil.which("brew"):
        try:
            res = subprocess.run(
                ["brew", "install", "pet"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=90,
            )
            if res.returncode == 0 and shutil.which("pet"):
                return True
        except Exception:
            pass

    # 2. Direct official standalone binary download (GitHub release tar.gz)
    try:
        bin_dir.mkdir(parents=True, exist_ok=True)
        machine = platform.machine().lower()
        is_arm = "arm" in machine or "aarch64" in machine

        if is_win:
            arch = "arm64" if is_arm else "amd64"
            url = f"https://github.com/knqyf263/pet/releases/download/v1.0.1/pet_1.0.1_windows_{arch}.tar.gz"
        elif sys.platform == "darwin":
            arch = "arm64" if is_arm else "amd64"
            url = f"https://github.com/knqyf263/pet/releases/download/v1.0.1/pet_1.0.1_darwin_{arch}.tar.gz"
        elif sys.platform.startswith("linux"):
            arch = "arm64" if is_arm else "amd64"
            url = f"https://github.com/knqyf263/pet/releases/download/v1.0.1/pet_1.0.1_linux_{arch}.tar.gz"
        else:
            url = None

        if url:
            archive_path = bin_dir / "pet.tar.gz"
            # Try curl first for robust network connection
            curl_res = subprocess.run(
                ["curl", "-sL", url, "-o", str(archive_path)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=60,
            )
            if curl_res.returncode != 0 or not archive_path.exists():
                urllib.request.urlretrieve(url, archive_path)

            import tarfile
            with tarfile.open(archive_path, "r:gz") as tar:
                tar.extractall(path=bin_dir)
            archive_path.unlink(missing_ok=True)

            if not is_win and local_pet.exists():
                os.chmod(local_pet, 0o755)
            return local_pet.exists()
    except Exception:
        pass

    return bool(shutil.which("pet") or local_pet.exists())


def _silently_install_chezmoi() -> bool:
    """
    Silently installs the chezmoi CLI tool using official one-line scripts and package managers:
    1. Windows: Scoop, Winget, or official one-line PowerShell script (get.chezmoi.io/ps1)
    2. Linux/macOS: Homebrew or official one-line curl script (get.chezmoi.io)
    """
    bin_dir = get_kapsel_dir() / "bin"
    is_win = sys.platform == "win32"
    local_chezmoi = bin_dir / ("chezmoi.exe" if is_win else "chezmoi")

    if shutil.which("chezmoi") or local_chezmoi.exists():
        return True

    # Windows methods
    if is_win:
        # 1. Scoop
        if shutil.which("scoop"):
            try:
                res = subprocess.run(
                    ["scoop", "install", "chezmoi"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=90,
                )
                if res.returncode == 0 and shutil.which("chezmoi"):
                    return True
            except Exception:
                pass

        # 2. Winget
        if shutil.which("winget"):
            try:
                res = subprocess.run(
                    ["winget", "install", "--id", "twpayne.chezmoi", "-e", "--silent", "--accept-source-agreements", "--accept-package-agreements"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=120,
                )
                if res.returncode == 0 and shutil.which("chezmoi"):
                    return True
            except Exception:
                pass

        # 3. Official PowerShell one-liner script (get.chezmoi.io/ps1)
        try:
            bin_dir.mkdir(parents=True, exist_ok=True)
            cmd = f'powershell -NoProfile -ExecutionPolicy Bypass -Command "iex \\"&{{$(irm \'https://get.chezmoi.io/ps1\')}}\\" -b \'{bin_dir}\'"'
            res = subprocess.run(
                cmd,
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=90,
            )
            if local_chezmoi.exists():
                return True
        except Exception:
            pass

    else:
        # Unix / macOS / Linux methods
        # 1. Homebrew
        if shutil.which("brew"):
            try:
                res = subprocess.run(
                    ["brew", "install", "chezmoi"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=90,
                )
                if res.returncode == 0 and shutil.which("chezmoi"):
                    return True
            except Exception:
                pass

        # 2. Official curl one-liner script (get.chezmoi.io)
        try:
            bin_dir.mkdir(parents=True, exist_ok=True)
            cmd = f'sh -c "$(curl -fsLS https://get.chezmoi.io)" -- -b "{bin_dir}"'
            res = subprocess.run(
                cmd,
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=90,
            )
            if local_chezmoi.exists():
                os.chmod(local_chezmoi, 0o755)
                return True
        except Exception:
            pass

    return bool(shutil.which("chezmoi") or local_chezmoi.exists())


def handle_add_command(args: List[str], console: Optional[Console] = None) -> int:
    """
    Handles 'kapsel add <plugin_name>' system command.
    Enables local plugins, verifies requirements, and registers them into config.yaml.
    """
    ensure_utf8_io()
    con = console or Console(legacy_windows=False)

    if not args:
        con.print("[bold #f43f5e]Error:[/] Please specify a plugin name to add.")
        con.print("[dim]Usage: kapsel add <plugin_name> (e.g. kapsel add install)[/]\n")
        return 1

    target_raw = args[0].strip()
    source_path = Path(target_raw).expanduser()

    global_plugins_dir = get_kapsel_dir() / "plugins"
    global_plugins_dir.mkdir(parents=True, exist_ok=True)

    # Determine plugin ID and source
    if source_path.exists() and source_path.is_dir():
        # User specified an explicit directory path (e.g. kapsel add ./plugins/install or /path/to/my-plugin)
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

        if dest_plugin_dir.exists() and dest_plugin_dir.is_dir():
            plugin_dir = dest_plugin_dir
        elif dev_plugin_dir.exists() and dev_plugin_dir.is_dir() and (dev_plugin_dir / "__init__.py").exists():
            # If present in local dev directory, automatically install it to global user directory
            shutil.copytree(dev_plugin_dir, dest_plugin_dir, dirs_exist_ok=True)
            plugin_dir = dest_plugin_dir
        else:
            con.print(f"[bold #f43f5e]Error:[/] Plugin '[white]{target_name}[/]' not found in global plugin directory.")
            con.print(f"[dim]Expected location:[/] {dest_plugin_dir}")
            con.print("[dim]To install a plugin, specify its local path or place it into your global plugins directory.[/]\n")
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

    # Silent official dependency installation
    if target_name == "install":
        if not shutil.which("mpm"):
            _silently_install_mpm()
    elif target_name == "rec":
        _silently_install_pet()
    elif target_name == "profile":
        _silently_install_chezmoi()

    msg = f"[bold #10b981]✔ Plugin '[#00f0ff]{target_name}[/]' successfully added and enabled![/]\n\n"
    msg += f"[dim]Location: {plugin_dir}[/]"

    con.print(Panel(msg, title="[bold #00f0ff]🔌 Plugin System[/]", border_style="#0891b2", expand=False))
    return 0
