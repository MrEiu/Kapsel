"""
Kapsel Commands Package.
Central dispatcher for all CLI and interactive capsule built-in commands.
"""

from typing import List, Optional
from rich.console import Console

from kapsel.commands.config import handle_config_command
from kapsel.commands.help import handle_help
from kapsel.commands.install import handle_install
from kapsel.commands.repo import handle_repo_command
from kapsel.commands.status import handle_status
from kapsel.commands.user import (
    handle_logout_command,
    handle_register_command,
    handle_whoami_command,
)


def dispatch_builtin(command_line: str, console: Optional[Console] = None) -> Optional[int]:
    """
    Checks if command_line is an internal capsule built-in command.
    Returns exit code (int) if handled, or None if it should be treated as an external shell command.
    """
    stripped = command_line.strip()
    if not stripped:
        return 0

    parts = stripped.split()
    cmd = parts[0].lower()
    args = parts[1:]

    # help / manual
    if cmd in ("help", "?", "-h", "--help"):
        return handle_help(args, console)

    # status / info / doctor
    if cmd in ("status", "info"):
        return handle_status(args, console)

    # config
    if cmd == "config":
        return handle_config_command(args, console)

    # repo / hub
    if cmd in ("repo", "hub"):
        return handle_repo_command(args, console)

    # install (dedicated empty skeleton)
    if cmd == "install":
        return handle_install(args, console)

    # user / auth commands
    if cmd == "register":
        return handle_register_command(args, console)
    if cmd in ("whoami", "user"):
        return handle_whoami_command(args, console)
    if cmd == "logout":
        return handle_logout_command(args, console)

    return None


__all__ = [
    "dispatch_builtin",
    "handle_help",
    "handle_status",
    "handle_config_command",
    "handle_repo_command",
    "handle_install",
    "handle_register_command",
    "handle_whoami_command",
    "handle_logout_command",
]
