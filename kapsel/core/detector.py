"""
Kapsel environment and shell sniffing detector.
Identifies host shell, elevation level, current working directory, and Git branch.
"""

import ctypes
import os
from pathlib import Path
import platform
import sys
from typing import Optional, Tuple

import psutil
import shellingham

from kapsel.storage.logger import logger


class EnvironmentDetector:
    """Sniffs host shell, user privileges, Git state, and directory paths."""

    KNOWN_SHELLS = {
        "pwsh": "pwsh",
        "pwsh.exe": "pwsh",
        "powershell": "powershell",
        "powershell.exe": "powershell",
        "cmd": "cmd",
        "cmd.exe": "cmd",
        "bash": "bash",
        "bash.exe": "bash",
        "zsh": "zsh",
        "fish": "fish",
        "sh": "sh",
    }

    def __init__(self):
        self._cached_shell: Optional[str] = None
        self._cached_shell_path: Optional[str] = None

    def detect_shell(self) -> Tuple[str, str]:
        """
        Detects the outer host shell name and executable path.
        Returns (shell_name, executable_path), e.g. ('pwsh', 'C:\\...\\pwsh.exe').
        """
        if self._cached_shell and self._cached_shell_path:
            return self._cached_shell, self._cached_shell_path

        # 1. Try psutil process tree lookup (inspect parents of current process)
        try:
            current_proc = psutil.Process(os.getpid())
            for parent in current_proc.parents():
                name = parent.name().lower()
                if name in self.KNOWN_SHELLS:
                    canonical = self.KNOWN_SHELLS[name]
                    try:
                        exe = parent.exe()
                    except Exception:
                        exe = name
                    self._cached_shell = canonical
                    self._cached_shell_path = exe
                    logger.debug(f"Detected host shell from parent process: {canonical} ({exe})")
                    return canonical, exe
        except Exception as e:
            logger.debug(f"Process tree shell detection failed: {e}")

        # 2. Try shellingham
        try:
            detected = shellingham.detect_shell()
            if detected:
                raw_name, raw_path = detected
                canonical = self.KNOWN_SHELLS.get(raw_name.lower(), raw_name.lower())
                self._cached_shell = canonical
                self._cached_shell_path = raw_path
                logger.debug(f"Detected host shell from shellingham: {canonical} ({raw_path})")
                return canonical, raw_path
        except Exception as e:
            logger.debug(f"Shellingham detection failed: {e}")

        # 3. Environment variable fallback
        if platform.system() == "Windows":
            comspec = os.environ.get("COMSPEC", "cmd.exe")
            # If PSModulePath is set and contains pwsh
            ps_module_path = os.environ.get("PSModulePath", "")
            if "PowerShell\\7" in ps_module_path or "pwsh" in ps_module_path.lower():
                self._cached_shell = "pwsh"
                self._cached_shell_path = "pwsh.exe"
            elif "WindowsPowerShell" in ps_module_path:
                self._cached_shell = "powershell"
                self._cached_shell_path = "powershell.exe"
            else:
                self._cached_shell = "cmd"
                self._cached_shell_path = comspec
        else:
            shell_env = os.environ.get("SHELL", "/bin/sh")
            base_name = Path(shell_env).name.lower()
            self._cached_shell = self.KNOWN_SHELLS.get(base_name, base_name)
            self._cached_shell_path = shell_env

        logger.debug(f"Fallback shell detection: {self._cached_shell} ({self._cached_shell_path})")
        return self._cached_shell, self._cached_shell_path

    def is_elevated(self) -> Tuple[bool, str]:
        """
        Check if running with elevated privileges (Admin on Windows, Root on Unix).
        Returns (is_elevated, label), e.g. (True, "Admin") or (False, "User").
        """
        try:
            if platform.system() == "Windows":
                is_admin = bool(ctypes.windll.shell32.IsUserAnAdmin())
                return is_admin, "Admin" if is_admin else "User"
            else:
                is_root = (os.geteuid() == 0)
                return is_root, "Root" if is_root else "User"
        except Exception as e:
            logger.debug(f"Elevation detection failed: {e}")
            return False, "User"

    def get_git_branch(self, path: Optional[Path] = None) -> Optional[str]:
        """
        Quickly inspects .git/HEAD in current or ancestor directories to extract the active branch.
        Does not spawn external git processes, ensuring near-instant performance.
        """
        target = (path or Path.cwd()).resolve()
        for directory in [target] + list(target.parents):
            git_dir = directory / ".git"
            if git_dir.is_file():
                # Git worktree / submodule pointer
                try:
                    content = git_dir.read_text(encoding="utf-8").strip()
                    if content.startswith("gitdir:"):
                        ref_path = (directory / content.split(":", 1)[1].strip()).resolve()
                        git_dir = ref_path
                except Exception:
                    pass

            if git_dir.is_dir():
                head_file = git_dir / "HEAD"
                if head_file.exists():
                    try:
                        content = head_file.read_text(encoding="utf-8").strip()
                        if content.startswith("ref: refs/heads/"):
                            return content.replace("ref: refs/heads/", "").strip()
                        elif content:
                            return content[:7]  # Detached commit hash
                    except Exception:
                        pass
        return None

    def format_cwd(self, path: Optional[Path] = None) -> str:
        """
        Formats current working directory, abbreviating home directory to '~'.
        """
        p = (path or Path.cwd()).resolve()
        home = Path.home().resolve()
        try:
            rel = p.relative_to(home)
            return f"~/{rel.as_posix()}" if str(rel) != "." else "~"
        except ValueError:
            return str(p)


detector = EnvironmentDetector()
