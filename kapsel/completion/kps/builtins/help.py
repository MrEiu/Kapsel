"""
Kapsel Help Command (Data-Driven Renderer).
Loads comprehensive, structured manual datasets from locale resources (defaults to English),
formats rich visual tables and panels, dynamically integrates live registered plugins,
and supports focused topic exploration.
All comments and descriptions are in English.
"""

from typing import Any, Dict, List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from kapsel import __version__
from kapsel.completion.kps.registry import get_kps_registry
from kapsel.i18n import get_current_language, load_help_data
from kapsel.ui.banner import ensure_utf8_io


class HelpRenderer:
    """
    Data-driven renderer for the Kapsel manual and cheatsheet.
    Decouples documentation content from Python code.
    """

    def __init__(self, console: Optional[Console] = None, lang: Optional[str] = None):
        self.console = console or Console(legacy_windows=False)
        self.lang = lang or get_current_language()
        self.data = load_help_data(self.lang)
        self.registry = get_kps_registry()

    def render_full_manual(self) -> None:
        """Renders the complete manual: Header, Modes, Quickstart, Commands, Shortcuts, and Tips."""
        self.console.print()
        self.render_header()
        self.render_modes()
        self.render_quickstart()
        self.render_commands()
        self.render_shortcuts()
        self.render_tips()
        self.console.print()

    def render_header(self) -> None:
        """Renders the title banner and architecture note."""
        meta = self.data.get("meta", {})
        title = meta.get("title", "KAPSEL")
        subtitle = meta.get("subtitle", "User Manual & Fast Command Cheatsheet")
        architecture = meta.get(
            "architecture",
            "Unified Command Pipeline: 'kapsel <cmd>' and 'kps <cmd>' share the exact same execution engine.",
        )

        header = Text()
        header.append(f"💊 {title}  ", style="bold #00f0ff")
        header.append(f"v{__version__}  ·  {subtitle}\n", style="dim #6b7280")
        header.append(f"{architecture}\n", style="italic #9ca3af")
        self.console.print(header)

    def render_modes(self) -> None:
        """Renders the Core Interaction Dual Modes table."""
        section = self.data.get("modes", {})
        title = section.get("title", "🚀 Core Interaction Dual Modes")
        cols = section.get("columns", {})
        rows = section.get("rows", [])

        table = Table(
            title=title,
            box=None,
            title_justify="left",
            padding=(0, 2),
            collapse_padding=True,
        )
        table.add_column(cols.get("mode", "Mode"), style="bold #00f0ff", width=22)
        table.add_column(cols.get("trigger", "Trigger"), style="#e4e4e7", width=26)
        table.add_column(cols.get("description", "Behavior & Capabilities"), style="dim #9ca3af")

        for r in rows:
            table.add_row(r.get("name", ""), r.get("trigger", ""), r.get("description", ""))

        self.console.print(table)
        self.console.print()

    def render_quickstart(self) -> None:
        """Renders the Quickstart workflow guide."""
        section = self.data.get("quickstart", {})
        title = section.get("title", "⚡ Quick Start Workflow")
        items = section.get("items", [])

        table = Table(title=title, box=None, title_justify="left", padding=(0, 2))
        table.add_column("Workflow Step", style="bold #a855f7", width=26)
        table.add_column("Command Line", style="bold #38bdf8", width=28)
        table.add_column("Purpose", style="#e4e4e7")

        for item in items:
            table.add_row(item.get("step", ""), item.get("cmd", ""), item.get("desc", ""))

        self.console.print(table)
        self.console.print()

    def render_commands(self) -> None:
        """
        Renders the Capsule Command Suite.
        Merges documented core commands with dynamically registered plugin commands.
        """
        section = self.data.get("commands", {})
        title = section.get("title", "⚙️ Capsule Command Suite (kapsel / kps)")
        cols = section.get("columns", {})
        builtin_rows = section.get("builtin_rows", [])

        table = Table(title=title, box=None, title_justify="left", padding=(0, 2))
        table.add_column(cols.get("command", "Command"), style="bold #00f0ff", width=22)
        table.add_column(cols.get("description", "Description"), style="#e4e4e7")
        table.add_column(cols.get("origin", "Origin"), style="dim #9ca3af", width=14)

        # Track displayed command names to prevent duplicates
        rendered_names = set()

        # 1. First render structured localized descriptions for built-in rows
        for r in builtin_rows:
            raw_cmd = r.get("name", "")
            table.add_row(raw_cmd, r.get("desc", ""), r.get("origin", "Core"))
            # Normalize command identifier (e.g. 'kps help' -> 'help')
            parts = raw_cmd.split()
            cmd_id = parts[1] if len(parts) > 1 else parts[0]
            rendered_names.add(cmd_id)

        # 2. Dynamically append any installed plugin commands not in static docs
        all_registered = self.registry.list_commands()
        for cmd in all_registered:
            if cmd.name not in rendered_names:
                origin = f"[{cmd.plugin_id}]" if cmd.plugin_id else "Core"
                table.add_row(f"kps {cmd.name}", cmd.help_text, origin)
                rendered_names.add(cmd.name)

        self.console.print(table)
        self.console.print()

    def render_shortcuts(self) -> None:
        """Renders interactive keybindings and ergonomic shortcuts."""
        section = self.data.get("shortcuts", {})
        title = section.get("title", "⌨️ Interactive Keybindings & Ergonomics")
        cols = section.get("columns", {})
        items = section.get("items", [])

        table = Table(title=title, box=None, title_justify="left", padding=(0, 2))
        table.add_column(cols.get("key", "Key"), style="bold #38bdf8", width=22)
        table.add_column(cols.get("description", "Action"), style="#e4e4e7")

        for item in items:
            table.add_row(item.get("key", ""), item.get("desc", ""))

        self.console.print(table)
        self.console.print()

    def render_tips(self) -> None:
        """Renders pro tips and best practices in an aesthetic panel."""
        section = self.data.get("tips", {})
        title = section.get("title", "💡 Pro Tips & Best Practices")
        items = section.get("items", [])

        if not items:
            return

        grid = Table.grid(padding=(0, 1))
        grid.add_column(style="bold #00f0ff", width=3)
        grid.add_column(style="#e4e4e7")

        for tip in items:
            grid.add_row("•", tip)

        panel = Panel(
            grid,
            title=f"[bold #00f0ff]{title}[/]",
            title_align="left",
            border_style="#0891b2",
            padding=(0, 2),
            expand=False,
        )
        self.console.print(panel)

    def render_topic(self, topic: str) -> bool:
        """Renders a single focused topic (e.g. 'keys', 'modes', 'commands', or specific command)."""
        clean = topic.strip().lower()

        if clean in ("mode", "modes", "dual", "architecture"):
            self.console.print()
            self.render_header()
            self.render_modes()
            return True

        if clean in ("quickstart", "start", "workflow"):
            self.console.print()
            self.render_header()
            self.render_quickstart()
            return True

        if clean in ("commands", "cmd", "cmds", "suite"):
            self.console.print()
            self.render_header()
            self.render_commands()
            return True

        if clean in ("key", "keys", "shortcuts", "bindings"):
            self.console.print()
            self.render_header()
            self.render_shortcuts()
            return True

        if clean in ("tip", "tips", "protips"):
            self.console.print()
            self.render_header()
            self.render_tips()
            return True

        # Check if user requested help for a specific registered command (e.g. 'kps help config')
        cmd = self.registry.get(clean)
        if cmd:
            self.console.print()
            grid = Table.grid(padding=(0, 2))
            grid.add_column(style="bold #00f0ff", width=14)
            grid.add_column(style="#e4e4e7")

            origin_str = f"[{cmd.plugin_id}] Plugin" if cmd.plugin_id else "Core Built-in"
            grid.add_row("Command:", f"[bold white]kapsel {cmd.name}[/] [dim](or: kps {cmd.name})[/]")
            grid.add_row("Description:", cmd.help_text)
            grid.add_row("Usage:", f"[bold #a855f7]{cmd.usage or f'kps {cmd.name} [options]'}[/]")
            grid.add_row("Origin:", origin_str)

            if cmd.subcommands:
                grid.add_row("Subcommands:", "")
                for sub, desc in cmd.subcommands.items():
                    grid.add_row("", f"  [bold #38bdf8]{sub:<16}[/] [dim]{desc}[/]")

            panel = Panel(
                grid,
                title=f"[bold #00f0ff]📖 Command Guide: {cmd.name}[/]",
                border_style="#0891b2",
                padding=(1, 2),
                expand=False,
            )
            self.console.print(panel)
            self.console.print()
            return True

        return False


def handle_help(args: Optional[List[str]] = None, console: Optional[Console] = None) -> int:
    """
    Entrypoint for the 'help' command.
    Dispatches to HelpRenderer for complete manual or focused sub-topic query.
    """
    ensure_utf8_io()
    con = console or Console(legacy_windows=False)
    renderer = HelpRenderer(con)

    if not args:
        renderer.render_full_manual()
        return 0

    target_topic = args[0]
    handled = renderer.render_topic(target_topic)
    if not handled:
        con.print(f"[yellow]Notice:[/] Topic or command '[white]{target_topic}[/]' not found in help manual.")
        con.print("[dim]Showing full manual instead:[/]")
        renderer.render_full_manual()

    return 0
