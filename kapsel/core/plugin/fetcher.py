"""
Kapsel Plugin Remote Fetcher.
Downloads and installs plugins from the official Kapsel plugins repository (https://github.com/MrEiu/plugins).
Supports both Git shallow clone and pure-Python HTTP archive streaming with mirror fallbacks.
All comments and descriptions are in English.
"""

import io
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile
import urllib.request
from typing import Optional
from rich.console import Console

from kapsel.storage.logger import logger

OFFICIAL_PLUGINS_REPO_GIT = "https://github.com/MrEiu/plugins.git"
OFFICIAL_PLUGINS_REPO_MIRROR_GIT = "https://ghproxy.net/https://github.com/MrEiu/plugins.git"

OFFICIAL_ARCHIVE_URL = "https://github.com/MrEiu/plugins/archive/refs/heads/master.tar.gz"
OFFICIAL_ARCHIVE_MIRROR_URL = "https://ghproxy.net/https://github.com/MrEiu/plugins/archive/refs/heads/master.tar.gz"


def _fetch_via_git(plugin_name: str, dest_dir: Path, console: Console) -> bool:
    """Attempts to fetch a plugin using git shallow clone."""
    if not shutil.which("git"):
        return False

    with tempfile.TemporaryDirectory(prefix="kapsel_plugin_git_") as tmp_str:
        tmp_path = Path(tmp_str)
        console.print(f"[dim]Attempting Git clone from {OFFICIAL_PLUGINS_REPO_GIT}...[/]")

        cloned = False
        for repo_url in [OFFICIAL_PLUGINS_REPO_GIT, OFFICIAL_PLUGINS_REPO_MIRROR_GIT]:
            try:
                res = subprocess.run(
                    ["git", "clone", "--depth", "1", repo_url, str(tmp_path / "repo")],
                    capture_output=True,
                    text=True,
                    timeout=20.0,
                )
                if res.returncode == 0:
                    cloned = True
                    break
            except Exception as e:
                logger.debug(f"Git clone failed for {repo_url}: {e}")

        if not cloned:
            return False

        src_plugin = tmp_path / "repo" / plugin_name
        if src_plugin.exists() and src_plugin.is_dir() and (src_plugin / "__init__.py").exists():
            dest_dir.mkdir(parents=True, exist_ok=True)
            shutil.copytree(src_plugin, dest_dir, dirs_exist_ok=True)
            return True

    return False


def _fetch_via_archive(plugin_name: str, dest_dir: Path, console: Console) -> bool:
    """Attempts to fetch a plugin by streaming and extracting the GitHub tarball."""
    console.print(f"[dim]Downloading plugin package from remote repository...[/]")

    headers = {"User-Agent": "Kapsel-Plugin-Fetcher/1.0"}
    archive_bytes: Optional[bytes] = None

    for url, label in [(OFFICIAL_ARCHIVE_URL, "GitHub"), (OFFICIAL_ARCHIVE_MIRROR_URL, "Mirror")]:
        try:
            console.print(f"[dim]Connecting to {label}...[/]")
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15.0) as resp:
                if resp.status == 200:
                    archive_bytes = resp.read()
                    break
        except Exception as ex:
            logger.debug(f"Archive download failed from {label} ({url}): {ex}")

    if not archive_bytes:
        return False

    try:
        dest_dir.mkdir(parents=True, exist_ok=True)
        found_any = False

        with tarfile.open(fileobj=io.BytesIO(archive_bytes), mode="r:gz") as tf:
            # Locate prefix inside archive (typically 'plugins-master/<plugin_name>/')
            prefix_pattern = f"/{plugin_name}/"
            for member in tf.getmembers():
                name = member.name.replace("\\", "/")
                # Check if file belongs to this plugin
                # e.g. 'plugins-master/install/__init__.py'
                idx = name.find(prefix_pattern)
                if idx != -1:
                    rel_subpath = name[idx + len(prefix_pattern) :]
                    if not rel_subpath:
                        continue
                    out_path = dest_dir / rel_subpath
                    if member.isdir():
                        out_path.mkdir(parents=True, exist_ok=True)
                    elif member.isreg():
                        out_path.parent.mkdir(parents=True, exist_ok=True)
                        extracted_f = tf.extractfile(member)
                        if extracted_f:
                            with open(out_path, "wb") as f:
                                shutil.copyfileobj(extracted_f, f)
                            found_any = True

        if found_any and (dest_dir / "__init__.py").exists():
            return True
        else:
            # Clean up empty directory on failure
            if dest_dir.exists():
                shutil.rmtree(dest_dir, ignore_errors=True)
            return False

    except Exception as e:
        logger.exception(f"Failed to unpack plugin '{plugin_name}' from archive: {e}")
        if dest_dir.exists():
            shutil.rmtree(dest_dir, ignore_errors=True)
        return False


def fetch_plugin_from_remote(
    plugin_name: str,
    dest_dir: Path,
    console: Optional[Console] = None,
) -> bool:
    """
    Downloads and installs a plugin from the official remote repository (https://github.com/MrEiu/plugins).
    Tries Git first, then pure Python tarball download.
    """
    con = console or Console(legacy_windows=False)
    con.print(
        f"[bold #00f0ff]🌐 Plugin '[white]{plugin_name}[/]' not found locally. "
        f"Fetching from official repository...[/]"
    )

    # 1. Try Git clone
    if _fetch_via_git(plugin_name, dest_dir, con):
        con.print(f"[bold #10b981]✔ Successfully fetched '{plugin_name}' via Git.[/]")
        return True

    # 2. Try HTTP tarball download
    if _fetch_via_archive(plugin_name, dest_dir, con):
        con.print(f"[bold #10b981]✔ Successfully downloaded and extracted '{plugin_name}'.[/]")
        return True

    con.print(
        f"[bold #f43f5e]Error:[/] Plugin '[white]{plugin_name}[/]' could not be found or downloaded "
        f"from official repository (https://github.com/MrEiu/plugins)."
    )
    return False
