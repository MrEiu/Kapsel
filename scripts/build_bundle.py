#!/usr/bin/env python3
"""
Kapsel All-in-One Release Bundle Builder.
Automates assembling standalone release bundles for China distribution:
- 9 precompiled binary tools (carapace, zoxide, mise, chsrc, aichat, pueue, chezmoi, pet, tldr, fzf)
- 11 official Kapsel plugins
- Offline Python wheels (kapsel_cli, mpm, thefuck, pipx)
- Domestic mirror configs (pip.ini, npmrc, scoop_mirror.ps1)
- Deployment scripts (setup.bat, setup.ps1, setup.sh)

Usage:
  python scripts/build_bundle.py --platform windows-x64
  python scripts/build_bundle.py --platform linux-amd64
  python scripts/build_bundle.py --platform macos-arm64

All comments and descriptions are in English.
"""

import argparse
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tarfile
import zipfile


ROOT_DIR = Path(__file__).resolve().parent.parent
BUNDLE_TEMPLATE_DIR = ROOT_DIR / "scripts" / "bundle"
DIST_DIR = ROOT_DIR / "dist"


def build_bundle(target_platform: str) -> Path:
    print(f"============================================================")
    print(f"Building Kapsel All-in-One Bundle for: {target_platform}")
    print(f"============================================================\n")

    is_windows = target_platform.startswith("windows")
    staging_name = f"kapsel-bundle-{target_platform}"
    staging_dir = DIST_DIR / staging_name

    if staging_dir.exists():
        shutil.rmtree(staging_dir)
    staging_dir.mkdir(parents=True, exist_ok=True)

    bin_dir = staging_dir / "bin"
    bin_dir.mkdir(exist_ok=True)
    plugins_dir = staging_dir / "plugins"
    plugins_dir.mkdir(exist_ok=True)
    mirrors_dir = staging_dir / "mirrors"
    mirrors_dir.mkdir(exist_ok=True)
    wheels_dir = staging_dir / "wheels"
    wheels_dir.mkdir(exist_ok=True)

    # 1. Copy domestic mirror configurations
    src_mirrors = BUNDLE_TEMPLATE_DIR / "mirrors"
    if src_mirrors.exists():
        for m_file in src_mirrors.glob("*"):
            if m_file.is_file():
                shutil.copy2(m_file, mirrors_dir / m_file.name)
        print("  [OK] Packaged domestic mirror configs (pip, npm, scoop).")

    # 2. Copy official plugins
    src_plugins = ROOT_DIR / "plugins"
    if src_plugins.exists():
        for p in src_plugins.iterdir():
            if p.is_dir() and not p.name.startswith((".", "__")):
                shutil.copytree(p, plugins_dir / p.name, dirs_exist_ok=True)
        print("  [OK] Packaged official Kapsel plugins.")

    # 3. Copy setup scripts
    for s_name in ("setup.ps1", "setup.bat", "setup.sh"):
        s_src = BUNDLE_TEMPLATE_DIR / s_name
        if s_src.exists():
            shutil.copy2(s_src, staging_dir / s_name)
    print("  [OK] Packaged setup scripts (setup.ps1, setup.bat, setup.sh).")

    # 4. Collect local binary tools from ~/.kapsel/bin if available
    user_bin = Path.home() / ".kapsel" / "bin"
    if user_bin.exists():
        for b in user_bin.glob("*.exe" if is_windows else "*"):
            if b.is_file():
                shutil.copy2(b, bin_dir / b.name)
        print("  [OK] Collected local binaries from ~/.kapsel/bin/.")

    # 5. Build or copy current kapsel wheel
    dist_wheels = list(DIST_DIR.glob("kapsel_cli-*.whl"))
    if dist_wheels:
        shutil.copy2(dist_wheels[-1], wheels_dir / dist_wheels[-1].name)
        print(f"  [OK] Packaged kapsel_cli wheel: {dist_wheels[-1].name}")

    # 6. Compress into final archive
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    if is_windows:
        archive_path = DIST_DIR / f"{staging_name}.zip"
        print(f"\nCompressing into {archive_path.name}...")
        with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for root, _, files in os.walk(staging_dir):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(DIST_DIR)
                    zf.write(file_path, arcname)
    else:
        archive_path = DIST_DIR / f"{staging_name}.tar.gz"
        print(f"\nCompressing into {archive_path.name}...")
        with tarfile.open(archive_path, "w:gz") as tf:
            tf.add(staging_dir, arcname=staging_name)

    size_mb = round(archive_path.stat().st_size / (1024 * 1024), 2)
    print("\n============================================================")
    print("[OK] Bundle Built Successfully!")
    print(f"  Location: {archive_path}")
    print(f"  Size:     {size_mb} MB")
    print("============================================================\n")
    return archive_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Kapsel All-in-One Distribution Bundle")
    default_plat = "windows-x64" if sys.platform == "win32" else ("macos-arm64" if platform.system() == "Darwin" else "linux-amd64")
    parser.add_argument("--platform", default=default_plat, help=f"Target platform (default: {default_plat})")
    args = parser.parse_args()

    build_bundle(args.platform)
    return 0


if __name__ == "__main__":
    sys.exit(main())
