"""
Kapsel-CLI Standalone Native Packager.
Compiles Kapsel-CLI into single-file standalone native executables (Scenario 2):
  • Windows: kapsel.exe & kps.exe
  • Linux:   kapsel & kps (ELF 64-bit binary)
  • macOS:   kapsel & kps (Mach-O binary)

Users do NOT need Python or pip installed.
"""

import argparse
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT_DIR = Path(__file__).resolve().parent.parent
DIST_DIR = ROOT_DIR / "dist" / "bin"
BUILD_TEMP_DIR = ROOT_DIR / "build" / "packager"


def get_current_os_target() -> str:
    system = platform.system().lower()
    if system == "windows":
        return "windows"
    elif system == "darwin":
        return "macos"
    elif system == "linux":
        return "linux"
    return "unknown"


def clean_build_artifacts():
    print("🧹 Cleaning previous build caches...")
    if BUILD_TEMP_DIR.exists():
        shutil.rmtree(BUILD_TEMP_DIR, ignore_errors=True)
    for p in ROOT_DIR.glob("*.spec"):
        try:
            p.unlink()
        except Exception:
            pass


def check_and_install_builder(builder: str):
    try:
        __import__(builder)
    except ImportError:
        print(f"📦 Packaging tool '{builder}' is not installed. Installing via pip...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", builder])


def build_with_pyinstaller(target_os: str, onefile: bool = True):
    check_and_install_builder("PyInstaller")

    out_dir = DIST_DIR / target_os
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n🚀 Building standalone Kapsel-CLI for [{target_os}] using PyInstaller...")

    # Hidden imports required by Kapsel runtime
    hidden_imports = [
        "shellingham",
        "prompt_toolkit",
        "prompt_toolkit.shortcuts",
        "prompt_toolkit.formatted_text",
        "prompt_toolkit.key_binding",
        "rich",
        "rich.console",
        "rich.table",
        "rich.panel",
        "rich.text",
        "yaml",
        "sqlite3",
        "kapsel",
        "kapsel.cli",
        "kapsel.core",
        "kapsel.core.completion",
        "kapsel.commands",
        "kapsel.storage",
        "kapsel.sync",
        "kapsel.ui",
    ]

    hidden_args = []
    for h in hidden_imports:
        hidden_args.extend(["--hidden-import", h])

    ext = ".exe" if target_os == "windows" else ""

    # 1. Build 'kapsel' (Main interactive capsule shell)
    cmd_kapsel = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--name",
        f"kapsel{ext}",
        "--onefile" if onefile else "--onedir",
        "--clean",
        "--distpath",
        str(out_dir),
        "--workpath",
        str(BUILD_TEMP_DIR / "kapsel"),
        "--specpath",
        str(BUILD_TEMP_DIR),
        *hidden_args,
        str(ROOT_DIR / "kapsel" / "cli.py"),
    ]

    print(f"  • Compiling kapsel{ext}...")
    subprocess.check_call(cmd_kapsel)

    # 2. Build 'kps' (One-shot translator CLI)
    # Create entry wrapper for kps
    kps_wrapper = BUILD_TEMP_DIR / "kps_entry.py"
    BUILD_TEMP_DIR.mkdir(parents=True, exist_ok=True)
    with open(kps_wrapper, "w", encoding="utf-8") as f:
        f.write("import sys\nfrom kapsel.cli import kps_cli\nif __name__ == '__main__':\n    sys.exit(kps_cli())\n")

    cmd_kps = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--name",
        f"kps{ext}",
        "--onefile" if onefile else "--onedir",
        "--clean",
        "--distpath",
        str(out_dir),
        "--workpath",
        str(BUILD_TEMP_DIR / "kps"),
        "--specpath",
        str(BUILD_TEMP_DIR),
        *hidden_args,
        str(kps_wrapper),
    ]

    print(f"  • Compiling kps{ext}...")
    subprocess.check_call(cmd_kps)

    print(f"\n✔ Build Succeeded for [{target_os}]!")
    print(f"  📁 Output Directory: {out_dir.resolve()}")
    for item in out_dir.glob(f"*{ext}"):
        size_mb = item.stat().st_size / (1024 * 1024)
        print(f"    - {item.name:<15} ({size_mb:.2f} MB)")


def main():
    parser = argparse.ArgumentParser(
        description="💊 Kapsel-CLI 独立免环境可执行文件一键打包工具 (Scenario 2: Windows / Linux / macOS)"
    )
    parser.add_argument(
        "--target",
        choices=["current", "windows", "linux", "macos", "all"],
        default="current",
        help="目标操作系统 (默认: 当前运行系统)",
    )
    parser.add_argument(
        "--builder",
        choices=["pyinstaller", "nuitka"],
        default="pyinstaller",
        help="打包编译引擎 (默认: pyinstaller，稳定通用)",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="打包前强制清理旧构建缓存",
    )

    args = parser.parse_args()

    clean_build_artifacts()

    current_os = get_current_os_target()

    if args.target == "current":
        target = current_os
    elif args.target != "all":
        target = args.target
    else:
        target = "all"

    if target == "all":
        print("💡 提示: 原生 C/C++ 机器码跨平台编译通常需在对应系统或 Docker 容器/CI 中运行。")
        print(f"当前先为您打包宿主系统 [{current_os}] 的原生二进制；")
        print("针对 Linux 和 macOS 的交叉构建，已为您生成 GitHub Actions 矩阵流水线 (packaging/build_matrix_ci.yml)。\n")
        target = current_os

    if target != current_os:
        print(f"⚠️ 警告: 当前运行系统是 [{current_os}]，直接在本地编译 [{target}] 二进制可能会受限。")
        print(f"建议使用 Docker 容器或 GitHub Actions 云编译以保证环境纯净。\n")

    build_with_pyinstaller(target)


if __name__ == "__main__":
    main()
