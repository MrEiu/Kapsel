"""
Kapsel Command Dispatcher.
Dispatches 'kps <cmd>' calls to registered built-in or plugin-provided command handlers.
"""

from typing import List, Optional
from rich.console import Console

from kapsel.completion.kps.registry import get_kps_registry


def dispatch_kps(command_line: str, console: Optional[Console] = None) -> Optional[int]:
    """
    Checks if command_line is a recognized 'kps' subcommand.
    Returns exit code (int) if handled, or None if not recognized as a registered kps command.
    """
    stripped = command_line.strip()
    if not stripped:
        return 0

    # Strip optional leading 'kps' prefix
    if stripped.startswith("kps "):
        stripped = stripped[4:].strip()
    elif stripped == "kps":
        # Bare 'kps' renders help
        registry = get_kps_registry()
        help_cmd = registry.get("help")
        if help_cmd:
            return help_cmd.handler([], console)
        return 0

    parts = stripped.split()
    cmd_name = parts[0].lower()
    args = parts[1:]

    # Fast aliases for help
    if cmd_name in ("?", "-h", "--help"):
        cmd_name = "help"
    # Fast alias for status
    if cmd_name == "info":
        cmd_name = "status"

    registry = get_kps_registry()
    cmd = registry.get(cmd_name)
    if cmd:
        return cmd.handler(args, console)

    return None
