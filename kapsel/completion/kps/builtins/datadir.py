"""
Kapsel Data Directory (datadir / migrate) Command Handler.
Allows users to view, customize, and migrate Kapsel's data storage location.
Automatically moves existing databases, configs, logs, and registry manifests.
"""

from pathlib import Path
from typing import List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from kapsel.storage.logger import (
    POINTER_FILE,
    get_default_kapsel_dir,
    get_kapsel_dir,
)
from kapsel.storage.migrate import migrate_kapsel_data
from kapsel.ui.banner import ensure_utf8_io


def handle_datadir_command(args: List[str], console: Optional[Console] = None) -> int:
    """Dispatches 'datadir' command: view or migrate storage location."""
    ensure_utf8_io()
    con = console or Console(legacy_windows=False)

    if not args:
        return show_current_datadir(con)

    sub = args[0].strip()

    if sub in ("help", "-h", "--help"):
        render_datadir_help(con)
        return 0

    if sub in ("status", "show", "current", "path"):
        return show_current_datadir(con)

    # Any other argument is treated as the target migration path!
    target_path = " ".join(args).strip().strip('"\'').strip()
    return do_migration(target_path, con)


def show_current_datadir(console: Console) -> int:
    current = get_kapsel_dir()
    default = get_default_kapsel_dir()
    is_custom = current.resolve() != default.resolve()

    # Calculate directory size
    total_bytes = 0
    file_count = 0
    try:
        for p in current.rglob("*"):
            if p.is_file():
                total_bytes += p.stat().st_size
                file_count += 1
    except Exception:
        pass

    size_str = f"{total_bytes / 1024:.1f} KB" if total_bytes < 1024 * 1024 else f"{total_bytes / (1024*1024):.2f} MB"

    grid = Table.grid(padding=(0, 2))
    grid.add_column(style="bold #00f0ff", width=18)
    grid.add_column()

    grid.add_row("📂 Data Directory:", f"[bold #10b981]{current}[/]")
    grid.add_row(
        "🏷️ Storage Mode:",
        "[bold #a855f7]Custom Location[/]" if is_custom else "[dim]Default (~/.kapsel)[/]",
    )
    grid.add_row("📦 Storage Size:", f"{size_str} ({file_count} files/databases)")
    if is_custom and POINTER_FILE.exists():
        grid.add_row("📌 Pointer File:", f"[dim]{POINTER_FILE}[/]")

    panel = Panel(
        grid,
        title="[bold #00f0ff]💊 Kapsel Data Directory[/]",
        border_style="#0891b2",
        padding=(1, 2),
    )
    console.print()
    console.print(panel)
    console.print("\n[dim]Usage:[/]")
    console.print("  • Relocate data sandbox: [bold #00f0ff]kps datadir <new_path>[/] (e.g. kps datadir D:\\KapselData)")
    console.print("  • Restore default:       [bold #00f0ff]kps datadir default[/]\n")
    return 0


def do_migration(target_path: str, console: Console) -> int:
    console.print(f"\n[dim]Preparing migration to:[/] [bold #00f0ff]{target_path}[/]")
    console.print("[dim]Moving databases, configs, and plugins...[/]")

    success, msg = migrate_kapsel_data(target_path)
    if success:
        console.print(f"\n[bold #10b981]✔ {msg}[/]\n")
        return 0
    else:
        console.print(f"\n[bold #f43f5e]✘ Migration failed: {msg}[/]\n")
        return 1


def render_datadir_help(console: Console) -> None:
    console.print("\n[bold #00f0ff]kps datadir[/] - View or customize Kapsel storage location\n")
    console.print("Usage:")
    console.print("  kps datadir                 View current storage location and stats")
    console.print("  kps datadir <new_path>      Migrate existing data to a new location")
    console.print("  kps datadir default         Migrate data back to default (~/.kapsel)\n")
