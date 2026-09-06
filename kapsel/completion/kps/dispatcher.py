"""
Kapsel Command Dispatcher.
Dispatches 'kapsel <cmd>' and 'kps <cmd>' uniformly.
Unified architecture ensures both prefixes share the exact same command pipeline.
"""

from typing import Any, List, Optional
from rich.console import Console

from kapsel.completion.kps.registry import get_kps_registry
from kapsel.i18n import _


def dispatch_kps(
    command_line: str,
    console: Optional[Console] = None,
    executor: Optional[Any] = None,
) -> Optional[int]:
    """
    Dispatches command lines starting with 'kapsel', 'kps', or 'kp'.
    Routes 'kapsel <cmd>' to system management commands,
    'kps <cmd>' to plugin/tool extension commands,
    and 'kp <cmd>' to block/batch pipeline execution.
    Returns exit code (int) if handled, or None if not recognized.
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
    elif stripped.startswith("kp ") or stripped.startswith("kp\n"):
        prefix = "kp"
        sub = stripped[2:].strip()
    elif stripped == "kp":
        prefix = "kp"
        sub = ""
    else:
        # Not a kapsel, kps, or kp command: do not intercept
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

    # Handle 'kp' namespace (Block & Parallel Batch Execution Pipeline)
    if prefix == "kp":
        return _handle_kp_command(sub, con, executor)

    return None


def _handle_kp_command(
    sub: str,
    con: Console,
    executor: Optional[Any] = None,
) -> int:
    """
    Handles 'kp [-c] <commands...>' execution.
    - Default: Atomic sequential execution of multi-line commands (preserves env/cwd).
    - With '-c' / '--concurrent': Concurrent parallel execution of task blocks.
    """
    cleaned = sub.strip()
    if not cleaned or cleaned in ("-h", "--help", "help"):
        con.print("\n[bold #00f0ff]⚡ Kapsel Block & Batch Pipeline Runner (kp)[/]")
        con.print("[dim]Executes multiple commands or pasted blocks cleanly.[/]\n")
        con.print("[bold white]Usage:[/]")
        con.print("  [bold #a855f7]kp <commands...>[/]             Execute multi-line commands sequentially (atomic, context-preserving)")
        con.print("  [bold #a855f7]kp -c <commands...>[/]          Execute commands concurrently in parallel tracks\n")
        con.print("[bold white]Examples:[/]")
        con.print("  kp git clone url\\ncd repo\\npnpm install      (Runs step-by-step sequentially)")
        con.print("  kp -c pnpm build:app\\npnpm build:docs         (Runs build tasks in parallel)\n")
        return 0

    from kapsel.core.block.runner import (
        split_commands,
        execute_sequential_block,
        execute_parallel_block,
    )
    from kapsel.core.executor import CommandExecutor

    is_concurrent = False
    body = sub

    if sub.startswith("-c ") or sub.startswith("--concurrent "):
        is_concurrent = True
        body = sub.split(" ", 1)[1]
    elif sub == "-c" or sub == "--concurrent":
        con.print("[bold #f43f5e]Error:[/] Please provide commands to execute with 'kp -c'.\n")
        return 1
    elif sub.startswith("-c\n") or sub.startswith("--concurrent\n"):
        is_concurrent = True
        body = sub.split("\n", 1)[1]

    commands = split_commands(body)
    if not commands:
        con.print("[yellow]Notice: No executable commands found in block.[/]\n")
        return 0

    if is_concurrent:
        exit_code, _ = execute_parallel_block(commands, console=con)
        return exit_code
    else:
        active_executor = executor or CommandExecutor()
        exit_code, _ = execute_sequential_block(
            commands, executor=active_executor, console=con
        )
        return exit_code


