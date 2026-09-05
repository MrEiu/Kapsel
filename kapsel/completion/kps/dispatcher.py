"""
Kapsel Command Dispatcher.
Dispatches 'kapsel <cmd>' and 'kps <cmd>' uniformly.
Unified architecture ensures both prefixes share the exact same command pipeline.
"""

from typing import List, Optional
from rich.console import Console

from kapsel.completion.kps.registry import get_kps_registry
from kapsel.i18n import _


def dispatch_kps(command_line: str, console: Optional[Console] = None) -> Optional[int]:
    """
    Dispatches command lines starting with 'kapsel' or 'kps'.
    Routes 'kapsel <cmd>' to system management commands,
    and 'kps <cmd>' to plugin/tool extension commands.
    Returns exit code (int) if handled, or None if not recognized or not a kapsel/kps command.
    """
    stripped = command_line.strip()
    if not stripped:
        return 0

    con = console or Console(legacy_windows=False)
    registry = get_kps_registry()

    # Determine command prefix and subcommand string
    if stripped.startswith("kapsel "):
        prefix = "kapsel"
        sub = stripped[7:].strip()
    elif stripped == "kapsel":
        prefix = "kapsel"
        sub = ""
    elif stripped.startswith("kps "):
        prefix = "kps"
        sub = stripped[4:].strip()
    elif stripped == "kps":
        prefix = "kps"
        sub = ""
    else:
        # Not a kapsel or kps command: do not intercept
        return None

    # Handle 'kapsel' namespace (System Platform & Shell Management)
    if prefix == "kapsel":
        if not sub:
            help_cmd = registry.get_system_command("help")
            if help_cmd:
                return help_cmd.handler([], con)
            return 0

        parts = sub.split()
        cmd_name = parts[0].lower()
        args = parts[1:]

        if cmd_name in ("?", "-h", "--help"):
            cmd_name = "help"
        elif cmd_name == "info":
            cmd_name = "status"

        sys_cmd = registry.get_system_command(cmd_name)
        if sys_cmd:
            return sys_cmd.handler(args, con)

        # Check if user accidentally invoked a tool command under kapsel prefix
        feat_cmd = registry.get_feature_command(cmd_name)
        if feat_cmd:
            con.print(f"[yellow]Notice:[/] '{cmd_name}' is a tool extension command. Forwarding to [bold #00f0ff]kps {sub}[/]...\n")
            return feat_cmd.handler(args, con)

        msg = _("kapsel: unknown command '{cmd}'. See 'kapsel help'.").format(cmd=cmd_name)
        con.print(f"[bold #f43f5e]{msg}[/]")
        return 1

    # Handle 'kps' namespace (Tools & Plugins Execution)
    if prefix == "kps":
        if not sub:
            con.print("\n[bold #00f0ff]🚀 Kapsel Tool Execution Subsystem (kps)[/]")
            con.print("[dim]Run 'kps <tool> [args...]' to invoke plugin tools (shore, init, portal, install, ai, etc.).[/]")
            con.print("[dim]To manage Kapsel terminal shell itself, run 'kapsel <cmd>' (status, config, datadir, add).[/]\n")
            return 0

        parts = sub.split()
        cmd_name = parts[0].lower()
        args = parts[1:]

        feat_cmd = registry.get_feature_command(cmd_name)
        if feat_cmd:
            return feat_cmd.handler(args, con)

        # Check if user tried to run a system command under kps prefix (e.g. kps status, kps config)
        sys_cmd = registry.get_system_command(cmd_name)
        if sys_cmd:
            con.print(f"[bold #f43f5e]Error:[/] '{cmd_name}' is a Kapsel system command, not a kps tool command.")
            con.print(f"[dim]Please use:[/] [bold #00f0ff]kapsel {sub}[/]\n")
            return 1

        con.print(f"[bold #f43f5e]kps: unknown command '{cmd_name}'. Run 'kapsel help' for available commands.[/]")
        return 1


