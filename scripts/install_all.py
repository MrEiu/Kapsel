#!/usr/bin/env python3
"""
Kapsel Universal All-in-One Toolchain Dispatcher.
Detects current operating system (Windows, macOS, Linux) and executes the
platform-tailored complete toolchain installer script.

All comments and descriptions are in English.
"""

from pathlib import Path
import platform
import subprocess
import sys


def main() -> int:
    system = platform.system().lower()
    script_dir = Path(__file__).resolve().parent

    print(f"=== Kapsel All-in-One Toolchain Installer Dispatcher ===")
    print(f"Detected Platform: {platform.system()} ({platform.machine()})\n")

    if system == "windows":
        ps1_script = script_dir / "install_tools_windows.ps1"
        if not ps1_script.exists():
            print(f"Error: {ps1_script} not found!", file=sys.stderr)
            return 1

        shell_cmd = "pwsh" if subprocess.run(["where", "pwsh"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0 else "powershell"
        cmd = [shell_cmd, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(ps1_script)] + sys.argv[1:]
        return subprocess.run(cmd).returncode

    elif system == "darwin":
        sh_script = script_dir / "install_tools_macos.sh"
        if not sh_script.exists():
            print(f"Error: {sh_script} not found!", file=sys.stderr)
            return 1
        cmd = ["bash", str(sh_script)] + sys.argv[1:]
        return subprocess.run(cmd).returncode

    elif system == "linux":
        sh_script = script_dir / "install_tools_linux.sh"
        if not sh_script.exists():
            print(f"Error: {sh_script} not found!", file=sys.stderr)
            return 1
        cmd = ["bash", str(sh_script)] + sys.argv[1:]
        return subprocess.run(cmd).returncode

    else:
        print(f"Error: Unsupported operating system '{system}'.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
