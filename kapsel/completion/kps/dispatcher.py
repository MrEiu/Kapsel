"""
Kapsel Command Dispatcher.
Dispatches 'kapsel <cmd>' (system management) and 'kps <cmd>' (functional tooling).
Enforces clear architectural separation between system commands and feature plugins.
"""

from typing import List, Optional
from rich.console import Console

from kapsel.completion.kps.registry import get_kps_registry


def dispatch_kps(command_line: str, console: Optional[Console] = None) -> Optional[int]:
    """
    Dispatches command lines starting with 'kapsel' or 'kps'.
    - 'kapsel <cmd>': Routed to system management commands (help, status, config, datadir).
    - 'kps <cmd>': Routed to functional/plugin commands (install, update, search, sync, etc.).
    Returns exit code (int) if handled, or None if not recognized or not a kapsel/kps command.
    """
    stripped = command_line.strip()
    if not stripped:
        return 0

    con = console or Console(legacy_windows=False)
    registry = get_kps_registry()

    # Determine command prefix
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

    # Handle bare 'kapsel' -> Show system help manual
    if prefix == "kapsel" and not sub:
        help_cmd = registry.get("help", scope="system")
        if help_cmd:
            return help_cmd.handler([], con)
        return 0

    # Handle bare 'kps' -> Show quick functional command summary
    if prefix == "kps" and not sub:
        features = registry.list_feature_commands()
        con.print("\n[bold #00f0ff]💊 Kapsel 功能扩展指令 (Feature Commands)[/]")
        con.print("[dim]使用 'kps <command>' 执行下列功能操作:[/]\n")
        for f_cmd in features:
            origin = f"[{f_cmd.plugin_id}]" if f_cmd.plugin_id else "[builtin]"
            con.print(f"  [bold #a855f7]kps {f_cmd.name:<12}[/] {f_cmd.help_text} [dim]{origin}[/]")
        con.print("\n[dim]提示: 系统自身管理指令请使用 'kapsel <command>' (如 kapsel help, kapsel status)[/]\n")
        return 0

    parts = sub.split()
    cmd_name = parts[0].lower()
    args = parts[1:]

    # System Scope ('kapsel <cmd>')
    if prefix == "kapsel":
        # Check alias shortcuts
        if cmd_name in ("?", "-h", "--help"):
            cmd_name = "help"
        elif cmd_name == "info":
            cmd_name = "status"

        sys_cmd = registry.get(cmd_name, scope="system")
        if sys_cmd:
            return sys_cmd.handler(args, con)

        # Cross-scope helpful suggestion
        feat_cmd = registry.get(cmd_name, scope="feature")
        if feat_cmd:
            con.print(
                f"[bold #f59e0b]提示:[/] '{cmd_name}' 属于扩展功能指令，请使用: "
                f"[bold #00f0ff]kps {cmd_name} {' '.join(args)}[/]"
            )
            return 1

        con.print(f"[bold #f43f5e]kapsel: 未知系统指令 '{cmd_name}'。[/] 输入 'kapsel help' 查阅系统指令。")
        return 1

    # Feature Scope ('kps <cmd>')
    if prefix == "kps":
        feat_cmd = registry.get(cmd_name, scope="feature")
        if feat_cmd:
            return feat_cmd.handler(args, con)

        # Cross-scope helpful suggestion
        sys_cmd = registry.get(cmd_name, scope="system")
        if sys_cmd:
            con.print(
                f"[bold #f59e0b]提示:[/] '{cmd_name}' 属于系统管理指令，请使用: "
                f"[bold #00f0ff]kapsel {cmd_name} {' '.join(args)}[/]"
            )
            return 1

        # If not registered in feature scope, return None so mapping plugins / external can process
        return None
