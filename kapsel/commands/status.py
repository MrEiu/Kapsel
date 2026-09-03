"""
Kapsel Status Command.
Renders comprehensive runtime environment, shell sniffing, and sandbox status dashboard.
"""

from datetime import datetime
from pathlib import Path
import platform
from typing import List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from kapsel import __version__
from kapsel.core.detector import detector
from kapsel.storage.config import load_config
from kapsel.storage.logger import get_kapsel_dir
from kapsel.storage.registry.indexer import get_registry_indexer
from kapsel.storage.user_db import get_user_db
from kapsel.ui.banner import ensure_utf8_io


def handle_status(args: Optional[List[str]] = None, console: Optional[Console] = None) -> int:
    """Renders the detailed Kapsel environment and runtime status dashboard."""
    ensure_utf8_io()
    con = console or Console(legacy_windows=False)

    user_db = get_user_db()
    current_user = user_db.get_active_user()
    stats = user_db.get_stats()

    shell_name, shell_path = detector.detect_shell()
    is_elevated, elevated_label = detector.is_elevated()
    cwd_raw = Path.cwd()
    cwd_fmt = detector.format_cwd(cwd_raw)
    branch = detector.get_git_branch(cwd_raw)
    cfg = load_config()
    sandbox_dir = get_kapsel_dir()
    indexer = get_registry_indexer()
    all_cmds = indexer.list_all_commands()

    # Status Grid
    grid = Table.grid(expand=True, padding=(0, 2))
    grid.add_column(style="bold #00f0ff", justify="right", width=18)
    grid.add_column(style="#e4e4e7")
    grid.add_column(style="bold #a855f7", justify="right", width=18)
    grid.add_column(style="#e4e4e7")

    priv_badge = f"[bold #10b981][{elevated_label}][/]" if not is_elevated else f"[bold #f59e0b][{elevated_label} (管理员)][/]"

    user_label = f"[bold #00f0ff]@{current_user['username']}[/]" if current_user else "[dim]未注册 (输入 'register' 注册)[/]"
    sync_label = "[bold #10b981]● 云漫游就绪 (SQLite)[/]" if current_user else "[dim]未配置 (支持多端同步)[/]"

    grid.add_row(
        "👤 胶囊漫游用户:",
        user_label,
        "☁️ 跨端同步状态:",
        sync_label,
    )
    grid.add_row(
        "🖥️ 宿主终端 (Shell):",
        f"[bold #00f0ff]{shell_name}[/] [dim]({shell_path})[/]",
        "🛡️ 权限状态:",
        priv_badge,
    )
    grid.add_row(
        "💻 操作系统平台:",
        f"{platform.system()} {platform.release()} ({platform.machine()})",
        "🐍 Python 环境:",
        f"{platform.python_implementation()} {platform.python_version()}",
    )
    grid.add_row(
        "📂 当前工作目录:",
        f"[#38bdf8]{cwd_fmt}[/] [dim]({cwd_raw})[/]",
        " Git 激活分支:",
        f"[bold #a855f7]{branch}[/]" if branch else "[dim]非 Git 仓库[/]",
    )
    grid.add_row(
        "📦 数据沙箱目录:",
        f"[dim]{sandbox_dir}[/]",
        "⚙️ UI 活跃主题:",
        f"[bold #00f0ff]{cfg.theme.get('name', 'cyber_dark')}[/]",
    )
    grid.add_row(
        "📋 指令映射库:",
        f"[bold #10b981]{len(all_cmds)}[/] 条自适应映射就绪 (目录式)",
        "🕒 历史漫游库:",
        f"[bold #10b981]{stats['total_history']}[/] 条历史 / [bold #a855f7]{stats['unique_commands']}[/] 个独立命令 (user.db)",
    )
    grid.add_row(
        "📝 日志记录路径:",
        f"[dim]{sandbox_dir / 'logs' / 'kapsel.log'}[/]",
        "⏱ 状态卡片封装:",
        "[bold #10b981]已启用 (╭─ ❯ / ╰─ ✔)[/]",
    )

    content = Table.grid(expand=True, padding=(1, 0))
    content.add_column()

    header = Text()
    header.append("💊 KAPSEL 运行环境与状态面板  ", style="bold #00f0ff")
    header.append(f"v{__version__}  ·  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n", style="dim #6b7280")
    header.append("终端级路由嗅探就绪 · 跨平台独立沙箱隔离正常", style="italic #9ca3af")

    content.add_row(header)
    content.add_row(grid)

    panel = Panel(
        content,
        border_style="#0891b2",
        padding=(1, 2),
        expand=False,
    )

    con.print()
    con.print(panel)
    con.print()
    return 0
