"""
Kapsel Command Dispatcher.
Dispatches 'kapsel <cmd>' and 'kps <cmd>' uniformly.
Unified architecture ensures both prefixes share the exact same command pipeline.
"""

from typing import List, Optional
from rich.console import Console

from kapsel.completion.kps.registry import get_kps_registry


def dispatch_kps(command_line: str, console: Optional[Console] = None) -> Optional[int]:
    """
    Dispatches command lines starting with 'kapsel' or 'kps'.
    Both 'kapsel <cmd>' and 'kps <cmd>' route to the unified command registry.
    Returns exit code (int) if handled, or None if not recognized or not a kapsel/kps command.
    """
    stripped = command_line.strip()
    if not stripped:
        return 0

    con = console or Console(legacy_windows=False)
    registry = get_kps_registry()

    # Determine command prefix and subcommand string
    if stripped.startswith("kapsel "):
        sub = stripped[7:].strip()
    elif stripped == "kapsel":
        sub = ""
    elif stripped.startswith("kps "):
        sub = stripped[4:].strip()
    elif stripped == "kps":
        sub = ""
    else:
        # Not a kapsel or kps command: do not intercept
        return None

    # Handle bare 'kapsel' or 'kps' -> Show comprehensive manual and commands
    if not sub:
        help_cmd = registry.get("help")
        if help_cmd:
            return help_cmd.handler([], con)
        return 0

    parts = sub.split()
    cmd_name = parts[0].lower()
    args = parts[1:]

    # Check alias shortcuts
    if cmd_name in ("?", "-h", "--help"):
        cmd_name = "help"
    elif cmd_name == "info":
        cmd_name = "status"

    # Route to unified command registry
    cmd = registry.get(cmd_name)
    if cmd:
        return cmd.handler(args, con)

    con.print(f"[bold #f43f5e]kapsel: unknown command '{cmd_name}'.[/] See 'kapsel help'.")
    return 1

