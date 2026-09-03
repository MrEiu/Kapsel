"""
Kapsel command execution subsystem.
Executes native and translated commands via host shell with timing and exit code capture.
"""

from dataclasses import dataclass
import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Optional, Tuple

from kapsel.storage.logger import logger


@dataclass
class ExecutionSummary:
    command: str
    exit_code: int
    duration_ms: int
    duration_str: str
    success: bool
    is_builtin: bool = False


class CommandExecutor:
    """Executes commands seamlessly through the host shell with full TUI/TTY passthrough."""

    def __init__(self, shell_name: str = "pwsh", shell_path: Optional[str] = None):
        self.shell_name = shell_name
        self.shell_path = shell_path or shell_name
        self._prev_dir: Optional[Path] = None

    def set_shell(self, shell_name: str, shell_path: Optional[str]) -> None:
        self.shell_name = shell_name
        self.shell_path = shell_path or shell_name

    def execute(self, cmd_string: str) -> ExecutionSummary:
        """
        Executes a command string.
        Handles built-ins (cd, exit, clear) and delegates other commands to host shell.
        """
        cmd = cmd_string.strip()
        if not cmd:
            return ExecutionSummary(command="", exit_code=0, duration_ms=0, duration_str="0ms", success=True)

        # 1. Check built-in commands
        builtin_result = self._handle_builtin(cmd)
        if builtin_result is not None:
            return builtin_result

        # 2. Host shell execution
        t0 = time.perf_counter()
        exit_code = 0
        try:
            exit_code = self._run_in_host_shell(cmd)
        except KeyboardInterrupt:
            print("\n^C")
            exit_code = 130
        except Exception as e:
            logger.error(f"Error executing command '{cmd}': {e}")
            print(f"Kapsel: execution error: {e}", file=sys.stderr)
            exit_code = 1

        t1 = time.perf_counter()
        duration_ms = int((t1 - t0) * 1000)
        duration_str = self.format_duration(duration_ms)

        return ExecutionSummary(
            command=cmd,
            exit_code=exit_code,
            duration_ms=duration_ms,
            duration_str=duration_str,
            success=(exit_code == 0),
            is_builtin=False,
        )

    def _handle_builtin(self, cmd: str) -> Optional[ExecutionSummary]:
        """Intercepts built-ins like cd, clear, cls."""
        parts = cmd.split()
        if not parts:
            return None

        primary = parts[0].lower()

        # Builtin: cd
        if primary == "cd":
            t0 = time.perf_counter()
            exit_code = self._execute_cd(parts[1:] if len(parts) > 1 else [])
            t1 = time.perf_counter()
            ms = int((t1 - t0) * 1000)
            return ExecutionSummary(
                command=cmd,
                exit_code=exit_code,
                duration_ms=ms,
                duration_str=self.format_duration(ms),
                success=(exit_code == 0),
                is_builtin=True,
            )

        # Check unified commands package (help, status, config, repo, user, install)
        from kapsel.commands import dispatch_builtin
        builtin_code = dispatch_builtin(cmd)
        if builtin_code is not None:
            return ExecutionSummary(
                command=cmd,
                exit_code=builtin_code,
                duration_ms=0,
                duration_str="0ms",
                success=(builtin_code == 0),
                is_builtin=True,
            )

        # Builtin: clear / cls
        if primary in ("clear", "cls"):
            os.system("cls" if os.name == "nt" else "clear")
            from kapsel.ui.banner import render_banner
            render_banner()
            return ExecutionSummary(
                command=cmd,
                exit_code=0,
                duration_ms=0,
                duration_str="0ms",
                success=True,
                is_builtin=True,
            )

        return None

    def _execute_cd(self, args: list[str]) -> int:
        current = Path.cwd()
        if not args or args[0] in ("~", ""):
            target = Path.home()
        elif args[0] == "-":
            if self._prev_dir:
                target = self._prev_dir
                print(target)
            else:
                print("kapsel: cd: OLDPWD not set", file=sys.stderr)
                return 1
        else:
            # Handle quoted paths or joined arguments if spaces were present
            raw_path = " ".join(args).strip("\"'")
            target = Path(raw_path).expanduser()
            if not target.is_absolute():
                target = (current / target).resolve()

        try:
            if not target.exists():
                print(f"kapsel: cd: {target}: No such file or directory", file=sys.stderr)
                return 1
            if not target.is_dir():
                print(f"kapsel: cd: {target}: Not a directory", file=sys.stderr)
                return 1

            os.chdir(target)
            self._prev_dir = current
            return 0
        except Exception as e:
            print(f"kapsel: cd: {e}", file=sys.stderr)
            return 1

    def _run_in_host_shell(self, cmd: str) -> int:
        """
        Runs the command through the detected host shell binary.
        Inherits stdin, stdout, stderr so interactive CLI programs (vim, fzf, git log) work seamlessly.
        """
        shell = self.shell_name.lower()
        args = []

        if shell in ("pwsh", "powershell"):
            # PowerShell: execute via -NoLogo -Command
            exe = self.shell_path if self.shell_path and Path(self.shell_path).exists() else (
                "pwsh.exe" if shell == "pwsh" else "powershell.exe"
            )
            args = [exe, "-NoLogo", "-Command", cmd]
        elif shell == "cmd":
            exe = self.shell_path if self.shell_path and Path(self.shell_path).exists() else "cmd.exe"
            args = [exe, "/c", cmd]
        else:
            # Unix shells (bash, zsh, fish, sh)
            exe = self.shell_path if self.shell_path and Path(self.shell_path).exists() else "/bin/sh"
            args = [exe, "-c", cmd]

        # Use subprocess.run without pipes so it directly controls terminal TTY / console
        proc = subprocess.run(args, shell=False)
        return proc.returncode

    @staticmethod
    def format_duration(ms: int) -> str:
        if ms < 1000:
            return f"{ms}ms"
        secs = ms / 1000.0
        if secs < 60:
            return f"{secs:.2f}s"
        mins = int(secs // 60)
        rem_secs = secs % 60
        return f"{mins}m {rem_secs:.1f}s"
