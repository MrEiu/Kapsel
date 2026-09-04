"""
Kapsel Status Command.
Renders comprehensive runtime environment, shell sniffing, and sandbox status dashboard.
"""

from datetime import datetime
from pathlib import Path
import platform
import sys
from typing import List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from kapsel import __version__
from kapsel.core.detector import detector
from kapsel.storage.config import load_config
from kapsel.storage.logger import get_kapsel_dir
from kapsel.ui.banner import ensure_utf8_io


def handle_status(args: Optional[List[str]] = None, console: Optional[Console] = None) -> int:
    """Renders the detailed Kapsel environment and runtime status dashboard."""
    ensure_utf8_io()
    con = console or Console(legacy_windows=False)

    shell_name, shell_path = detector.detect_shell()
    is_elevated, elevated_label = detector.is_elevated()
    cwd_raw = Path.cwd()
    cwd_fmt = detector.format_cwd(cwd_raw)
    branch = detector.get_git_branch(cwd_raw)
    cfg = load_config()
    sandbox_dir = get_kapsel_dir()

    # Status Grid
    grid = Table.grid(expand=True, padding=(0, 2))
    grid.add_column(style="bold #00f0ff", justify="right", width=18)
    grid.add_column(style="#e4e4e7")
    grid.add_column(style="bold #a855f7", justify="right", width=18)
    grid.add_column(style="#e4e4e7")

    priv_badge = (
        f"[bold #10b981][{elevated_label}][/]"
        if not is_elevated
        else f"[bold #f59e0b][{elevated_label} (管理员)][/]"
    )

    grid.add_row(
        "🖥️ 操作系统平台:",
        f"{platform.system()} {platform.release()} ({platform.machine()})",
        "🐚 宿主终端 (Shell):",
        f"[bold #38bdf8]{shell_name}[/] [dim]({shell_path})[/]",
    )

    grid.add_row(
        "⚡ 权限运行等级:",
        priv_badge,
        "🌿 Git 工作分支:",
        f"[bold #10b981]{branch}[/]" if branch else "[dim]非 Git 仓库[/]",
    )

    grid.add_row(
        "📂 当前工作目录:",
        f"[dim]{cwd_fmt}[/]",
        "💊 胶囊内核版本:",
        f"[bold #00f0ff]v{__version__}[/] (Python {sys.version.split()[0]})",
    )

    theme_name = cfg.theme.get("name", "cyber_dark") if isinstance(cfg.theme, dict) else str(cfg.theme)
    grid.add_row(
        "📦 数据沙箱根目录:",
        f"[dim]{sandbox_dir}[/]",
        "🎨 当前激活主题:",
        f"[bold #a855f7]{theme_name}[/] [dim](边框: {'开启' if cfg.enable_card_border else '关闭'})[/]",
    )

    # Completion & Plugins info
    from kapsel.completion.kps.registry import get_kps_registry
    registry = get_kps_registry()
    commands = registry.list_commands()

    # Count Fig Specs
    specs_dir = Path(__file__).resolve().parent.parent.parent / "specs"
    spec_count = len(list(specs_dir.glob("*.json"))) if specs_dir.exists() else 0

    grid.add_row(
        "🎯 自动补全规则库:",
        f"[bold #10b981]{spec_count}[/] 个内置 Fig 工具规范",
        "⚙️ 控制台注册指令:",
        f"[bold #38bdf8]{len(commands)}[/] 个可用指令",
    )

    panel = Panel(
        grid,
        title="[bold #00f0ff]💊 KAPSEL 系统运行与环境状态看板[/]",
        title_align="left",
        border_style="#0891b2",
        padding=(1, 2),
    )

    con.print()
    con.print(panel)
    con.print()
    return 0
