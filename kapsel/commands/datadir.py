"""
Kapsel Data Directory (datadir / migrate) Command Handler.
Allows users to view, customize, and migrate Kapsel's data storage location.
Automatically moves existing databases, configs, logs, and registry manifests ("原来不留").
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

    grid.add_row("📂 当前数据目录:", f"[bold #10b981]{current}[/]")
    grid.add_row(
        "🏷️ 存储位置模式:",
        "[bold #a855f7]自定义路径 (Custom Location)[/]" if is_custom else "[dim]系统默认路径 (Default: ~/.kapsel)[/]",
    )
    grid.add_row("📦 当前数据容量:", f"{size_str} ({file_count} 个文件/配置/数据库)")
    if is_custom and POINTER_FILE.exists():
        grid.add_row("📌 路径指针记录:", f"[dim]{POINTER_FILE}[/]")

    panel = Panel(
        grid,
        title="[bold #00f0ff]💊 Kapsel 数据存储目录看板[/]",
        border_style="#0891b2",
        padding=(1, 2),
    )
    console.print()
    console.print(panel)
    console.print("\n[dim]使用提示:[/]")
    console.print("  • 修改存储位置并自动搬迁数据:  [bold #00f0ff]kps datadir <新路径>[/] (例如: kps datadir D:\\KapselData)")
    console.print("  • 恢复为默认 ~/.kapsel 路径:   [bold #00f0ff]kps datadir default[/]\n")
    return 0


def do_migration(target_path: str, console: Console) -> int:
    console.print(f"\n[dim]正在准备迁移数据目录至:[/] [bold #00f0ff]{target_path}[/]")
    console.print("[dim]正在转移数据库、配置文件与指令仓库，并清理旧目录...[/]")

    success, msg = migrate_kapsel_data(target_path)
    if success:
        console.print(f"\n[bold #10b981]✔ {msg}[/]")
        console.print("[dim]新路径已在全局生效，未来所有会话与数据将自动读写该位置。[/]\n")
        return 0
    else:
        console.print(f"\n[bold #f43f5e]✘ 迁移失败: {msg}[/]\n")
        return 1


def render_datadir_help(console: Console) -> None:
    console.print("\n[bold #00f0ff]kps datadir[/] - 查看或修改 Kapsel 数据存储位置\n")
    console.print("用法:")
    console.print("  kps datadir                 查看当前数据存储目录与容量")
    console.print("  kps datadir <新目录绝对路径>  将现有全部数据自动搬迁至新位置 (旧位置彻底清除)")
    console.print("  kps datadir default         将数据搬迁回系统默认位置 (~/.kapsel)\n")
