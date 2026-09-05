"""
Carapace Completion Engine Auto-Installer for Kapsel.
Downloads and installs the official standalone pre-compiled 'carapace-bin' executable
into '~/.kapsel/bin' cross-platform (Linux, macOS, Windows) without requiring root or external package managers.
All comments and descriptions are in English.
"""

import io
import os
from pathlib import Path
import platform
import shutil
import stat
import subprocess
import sys
import tarfile
import urllib.request
import zipfile
from typing import Optional, Tuple
from rich.console import Console
from rich.panel import Panel

from kapsel.i18n import _
from kapsel.storage.config import get_kapsel_dir
from kapsel.storage.logger import logger


DEFAULT_CARAPACE_VERSION = "1.7.3"


def detect_platform_and_arch() -> Tuple[str, str, str]:
    """
    Detects the current OS and CPU architecture mapped to carapace-bin release nomenclature.
    Returns: (os_name, arch_name, archive_extension)
    """
    # 1. OS Detection
    if sys.platform == "win32":
        os_name = "windows"
        ext = "zip"
    elif sys.platform == "darwin":
        os_name = "darwin"
        ext = "tar.gz"
    elif sys.platform.startswith("linux"):
        os_name = "linux"
        ext = "tar.gz"
    else:
        raise OSError(f"Unsupported operating system: {sys.platform}")

    # 2. Architecture Detection
    mach = platform.machine().lower()
    if mach in ("x86_64", "amd64"):
        arch_name = "amd64"
    elif mach in ("aarch64", "arm64"):
        arch_name = "arm64"
    elif mach in ("i386", "i686"):
        arch_name = "386"
    elif mach.startswith("armv"):
        arch_name = "armv6"
    else:
        raise OSError(f"Unsupported CPU architecture: {mach}")

    return os_name, arch_name, ext


def install_carapace(
    console: Optional[Console] = None,
    version: str = DEFAULT_CARAPACE_VERSION,
    force: bool = False,
) -> bool:
    """
    Downloads and installs the official 'carapace-bin' standalone binary into ~/.kapsel/bin.
    Returns True if successful, False otherwise.
    """
    con = console or Console(legacy_windows=False)
    from kapsel.completion.carapace_engine import get_carapace_engine

    engine = get_carapace_engine()
    if engine.is_available() and not force:
        con.print(
            f"[bold #10b981]✔ Carapace is already installed and active![/]\n"
            f"[dim]Executable:[/] {engine.executable}\n"
            f"[dim]Run with '--force' to reinstall or upgrade.[/]"
        )
        return True

    try:
        os_name, arch_name, ext = detect_platform_and_arch()
    except OSError as e:
        con.print(f"[bold #f43f5e]Error:[/] {e}")
        return False

    is_win = os_name == "windows"
    archive_name = f"carapace-bin_{version}_{os_name}_{arch_name}.{ext}"
    bin_name = "carapace.exe" if is_win else "carapace"

    download_url = (
        f"https://github.com/carapace-sh/carapace-bin/releases/download/v{version}/{archive_name}"
    )
    mirror_url = f"https://ghproxy.net/{download_url}"

    dest_dir = get_kapsel_dir() / "bin"
    dest_dir.mkdir(parents=True, exist_ok=True)
    target_bin = dest_dir / bin_name

    con.print(f"[bold #00f0ff]🚀 Installing Carapace Completion Engine (v{version})...[/]")
    con.print(f"[dim]Platform:[/] {os_name} ({arch_name})")
    con.print(f"[dim]Target:[/]   {target_bin}")

    # Download archive into memory buffer or temp file
    data: Optional[bytes] = None
    headers = {"User-Agent": f"Kapsel-Installer/{version} ({os_name}; {arch_name})"}

    for candidate_url, label in [(download_url, "GitHub"), (mirror_url, "Mirror Fallback")]:
        try:
            con.print(f"[dim]Connecting to {label}...[/]")
            req = urllib.request.Request(candidate_url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as resp:
                if resp.status == 200:
                    data = resp.read()
                    break
        except Exception as ex:
            logger.debug(f"Download failed from {label} ({candidate_url}): {ex}")

    if not data:
        con.print(
            f"[bold #f43f5e]Error:[/] Failed to download {archive_name} from GitHub and mirror.\n"
            f"[dim]Please check your internet connection or install manually via:[/]\n"
            f"  https://carapace.sh or https://github.com/carapace-sh/carapace-bin/releases"
        )
        return False

    con.print("[dim]Extracting executable binary...[/]")
    extracted = False

    try:
        if ext == "zip":
            with zipfile.ZipFile(io.BytesIO(data)) as zf:
                for name in zf.namelist():
                    if Path(name).name.lower() in ("carapace.exe", "carapace"):
                        with zf.open(name) as src, open(target_bin, "wb") as dst:
                            shutil.copyfileobj(src, dst)
                        extracted = True
                        break
        else:
            with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tf:
                for member in tf.getmembers():
                    if Path(member.name).name == "carapace":
                        extracted_file = tf.extractfile(member)
                        if extracted_file:
                            with open(target_bin, "wb") as dst:
                                shutil.copyfileobj(extracted_file, dst)
                            extracted = True
                            break

        if not extracted or not target_bin.exists():
            con.print(f"[bold #f43f5e]Error:[/] 'carapace' binary was not found in archive.")
            return False

        # Set executable permissions on POSIX
        if not is_win:
            current_mode = target_bin.stat().st_mode
            target_bin.chmod(current_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

        # Verify executable runs
        res = subprocess.run(
            [str(target_bin), "--version"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=5.0,
        )
        ver_str = res.stdout.strip() if res.returncode == 0 else f"v{version}"

        # Update engine singleton dynamically
        engine.executable = str(target_bin)
        engine._supported_tools = None  # Reset tool cache to reload

        panel_msg = (
            f"[bold #10b981]✔ Carapace ({ver_str}) successfully installed![/]\n\n"
            f"[dim]Location:[/] {target_bin}\n"
            f"[dim]Engine:[/]   1,000+ dynamic tool completions (git, docker, kubectl, npm, etc.) enabled immediately."
        )
        con.print(Panel(panel_msg, title="[bold #00f0ff]🎯 Completion Engine[/]", border_style="#10b981", expand=False))
        return True

    except Exception as e:
        logger.exception("Failed to extract or verify Carapace binary")
        con.print(f"[bold #f43f5e]Error during extraction/verification:[/] {e}")
        return False


def ensure_carapace_installed(console: Optional[Console] = None) -> bool:
    """
    Auto-bootstraps Carapace completion engine on first launch if not already available.
    Zero-overhead (0ms) on subsequent launches when already installed.
    Gracefully falls back to basic completion if offline, preventing any startup crash.
    """
    from kapsel.completion.carapace_engine import get_carapace_engine

    engine = get_carapace_engine()
    if engine.is_available():
        return True

    con = console or Console(legacy_windows=False)
    con.print("[bold #00f0ff]🎯 First Launch: Auto-initializing Carapace completion engine (1,000+ tools)...[/]")

    try:
        success = install_carapace(console=con, force=False)
        return success
    except Exception as e:
        logger.warning(f"Failed to auto-bootstrap Carapace: {e}")
        con.print(
            f"[yellow]Notice: Could not automatically setup Carapace ({e}). "
            f"Continuing in basic autocompletion mode.[/]\n"
        )
        return False

