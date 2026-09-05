"""
Kapsel Completion Management Command (`kps completion`).
Provides logical unification for inspecting, synchronizing, creating,
and editing independent declarative Carapace specification files.
All comments and descriptions are in English.
"""

import os
from pathlib import Path
import subprocess
import sys
from typing import List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from kapsel.completion.carapace_engine import get_carapace_engine
from kapsel.completion.spec_manager import (
    CarapaceSpecManager,
    get_carapace_specs_dir,
    get_user_specs_dir,
)
from kapsel.ui.banner import ensure_utf8_io

ensure_utf8_io()


def handle_completion(args: List[str], console: Optional[Console] = None) -> int:
    """Entry point for 'kps completion' management suite."""
    con = console or Console(legacy_windows=False)
    spec_mgr = CarapaceSpecManager()

    if not args or args[0] in ("-h", "--help", "help"):
        _render_help(con)
        return 0

    subcmd = args[0].lower()

    if subcmd in ("ls", "list"):
        return _handle_list(spec_mgr, con)
    elif subcmd == "sync":
        return _handle_sync(spec_mgr, con)
    elif subcmd in ("new", "create"):
        return _handle_new(spec_mgr, args[1:], con)
    elif subcmd == "edit":
        return _handle_edit(spec_mgr, args[1:], con)
    elif subcmd == "path":
        return _handle_path(con)
    else:
        con.print(f"[bold #f43f5e]kps completion: unknown subcommand '{subcmd}'. See 'kps completion --help'.[/]")
        return 1


def _handle_list(spec_mgr: CarapaceSpecManager, con: Console) -> int:
    """Lists all active command specifications and their source layers."""
    specs = spec_mgr.discover_specs()

    if not specs:
        con.print("[dim]No custom completion specifications discovered.[/]")
        con.print(f"[dim]Place spec files into '{spec_mgr.user_specs_dir}' or plugin packages.[/]\n")
        return 0

    table = Table(title="[bold #00f0ff]📋 Declarative Completion Specifications[/]", border_style="#0891b2")
    table.add_column("Command", style="bold #00f0ff", width=14)
    table.add_column("Scope", justify="center", width=14)
    table.add_column("Source", justify="center", width=10)
    table.add_column("Description", style="white", overflow="fold")
    table.add_column("Spec File Path", style="dim", overflow="fold")
    table.add_column("Status", justify="center", width=14)

    has_root = (spec_mgr.carapace_specs_dir / "kps.yaml").exists()

    for cmd_name, info in sorted(specs.items(), key=lambda x: x[0]):
        if info.source_type == "user":
            source_badge = "[bold #a855f7]User[/]"
        elif info.source_type == "plugin":
            source_badge = "[bold #10b981]Plugin[/]"
        else:
            source_badge = "[dim]Core[/]"

        scope_badge = "[bold #38bdf8]Standalone[/]" if info.standalone else "[dim #00f0ff]kps subcommand[/]"

        if info.is_overridden:
            status = "[bold #f59e0b]Overridden[/]"
        elif info.standalone and info.target_path.exists():
            status = "[bold #10b981]✔ Active[/]"
        elif not info.standalone and has_root:
            status = "[bold #10b981]✔ In kps.yaml[/]"
        else:
            status = "[dim #f43f5e]Pending[/]"

        desc = info.description or "[dim]No description[/]"
        table.add_row(cmd_name, scope_badge, source_badge, desc, str(info.source_path), status)

    con.print()
    con.print(table)
    con.print(f"[dim]Total: {len(specs)} specification(s) mapped into root 'kps'/'kapsel' trees and standalone specs.[/]\n")
    return 0


def _handle_sync(spec_mgr: CarapaceSpecManager, con: Console) -> int:
    """Forces synchronization of all specifications into Carapace directory."""
    con.print("[bold #00f0ff]🔄 Synchronizing completion specifications to Carapace...[/]")
    synced, skipped = spec_mgr.sync_specs(force=True)

    # Refresh in-memory tool list
    engine = get_carapace_engine()
    engine.reload_tools()

    con.print(f"  [bold #10b981]✔ Synced:[/] {synced} file(s) updated.")
    con.print(f"  [dim]Mounted at:[/] {spec_mgr.carapace_specs_dir}\n")
    return 0


def _handle_new(spec_mgr: CarapaceSpecManager, args: List[str], con: Console) -> int:
    """Creates a new user specification template."""
    if not args:
        con.print("[bold #f43f5e]Error:[/] Command name required.")
        con.print("[dim]Usage: kps completion new <command_name> [description][/]")
        return 1

    cmd_name = args[0].strip().lower()
    desc = " ".join(args[1:]) if len(args) > 1 else ""

    target_file = spec_mgr.user_specs_dir / f"{cmd_name}.yaml"
    if target_file.exists():
        con.print(f"[yellow]Specification already exists at:[/] {target_file}")
        return 0

    path = spec_mgr.create_template(cmd_name, desc)
    con.print(f"[bold #10b981]✔ Created spec template:[/] [white]{path}[/]")
    con.print("[dim]Run 'kps completion edit " + cmd_name + "' to customize options and subcommands.[/]\n")
    return 0


def _handle_edit(spec_mgr: CarapaceSpecManager, args: List[str], con: Console) -> int:
    """Opens a specification YAML in the default system editor."""
    if not args:
        con.print("[bold #f43f5e]Error:[/] Command name required.")
        con.print("[dim]Usage: kps completion edit <command_name>[/]")
        return 1

    cmd_name = args[0].strip().lower()
    specs = spec_mgr.discover_specs()

    if cmd_name in specs:
        target_path = specs[cmd_name].source_path
    else:
        # Create user spec if not found
        con.print(f"[dim]Spec for '{cmd_name}' not found. Creating user template...[/]")
        target_path = spec_mgr.create_template(cmd_name)

    con.print(f"[dim]Opening spec in editor:[/] [white]{target_path}[/]")
    try:
        if sys.platform == "win32":
            os.startfile(str(target_path))
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(target_path)])
        else:
            editor = os.environ.get("EDITOR", "nano")
            subprocess.Popen([editor, str(target_path)])
        return 0
    except Exception as e:
        con.print(f"[bold #f43f5e]Failed to launch editor:[/] {e}")
        return 1


def _handle_path(con: Console) -> int:
    """Prints active specification directory paths."""
    con.print(Panel(
        f"[bold #00f0ff]User Custom Specs:[/]     {get_user_specs_dir()}\n"
        f"[bold #a855f7]Carapace Engine Specs:[/] {get_carapace_specs_dir()}\n\n"
        "[dim]Note: Specs placed in user directory automatically take highest precedence.[/]",
        title="[bold #00f0ff]📂 Completion Spec Directories[/]",
        border_style="#0891b2",
    ))
    return 0


def _render_help(con: Console) -> None:
    """Renders help panel for 'kps completion'."""
    help_text = (
        "[bold #00f0ff]Kapsel Completion Management Suite[/]\n"
        "[dim]Manage and synchronize independent declarative Carapace specification files.[/]\n\n"
        "[bold #a855f7]Commands:[/]\n"
        "  [#10b981]kps completion ls[/]              List all active specs and their source layer\n"
        "  [#10b981]kps completion sync[/]            Force refresh & mirror all specs to Carapace\n"
        "  [#10b981]kps completion new <cmd> [desc][/] Scaffold new spec template in ~/.kapsel/specs/\n"
        "  [#10b981]kps completion edit <cmd>[/]      Open spec in default system editor\n"
        "  [#10b981]kps completion path[/]            Display physical spec storage locations\n\n"
        "[bold #a855f7]Architecture (Physical Independence, Logical Unification):[/]\n"
        "  • [white]Plugins:[/] Plugins package their own [dim]plugins/<name>/spec.yaml[/]\n"
        "  • [white]User:[/]    Custom user specs live in [dim]~/.kapsel/specs/<cmd>.yaml[/]\n"
        "  • [white]Engine:[/]  Automatically mirrored to Carapace native directory"
    )
    con.print(Panel(help_text, title="[bold #00f0ff]⚙️ kps completion[/]", border_style="#0891b2"))
