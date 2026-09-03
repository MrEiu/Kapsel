"""
Kapsel internal help manual and system status dashboard.
Provides rich formatted help and status commands.
"""

from datetime import datetime
from pathlib import Path
import platform
import sqlite3
import sys
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from kapsel import __version__
from kapsel.core.detector import detector
from kapsel.storage.commands import load_commands
from kapsel.storage.config import load_config
from kapsel.storage.history import HistoryManager, get_history_db_path
from kapsel.storage.logger import get_kapsel_dir
from kapsel.ui.banner import ensure_utf8_io


def render_help(console: Optional[Console] = None) -> None:
    """Renders the comprehensive Kapsel help manual."""
    ensure_utf8_io()
    if console is None:
        console = Console(legacy_windows=False)

    console.print()

    # Header
    header = Text()
    header.append("💊 KAPSEL  ", style="bold #00f0ff")
    header.append(f"v{__version__}  ·  使用指南与命令速查手册\n", style="dim #6b7280")
    header.append("核心哲学: 包裹复杂，暴露极简。统一 Linux 肌肉记忆，零侵入原生 Shell。\n", style="italic #9ca3af")
    console.print(header)

    # 1. 核心交互模式
    mode_table = Table(title="🚀 核心交互机制", box=None, title_justify="left", padding=(0, 2))
    mode_table.add_column("模式", style="bold #00f0ff", width=18)
    mode_table.add_column("触发方式", style="#e4e4e7", width=22)
    mode_table.add_column("行为描述", style="dim #9ca3af")

    mode_table.add_row(
        "默认态 (Native Mode)",
        "直接输入任何命令",
        "100% 原生命令无感透传执行（git, npm, vim, python 等）；Tab 补全本地路径",
    )
    mode_table.add_row(
        "映射态 (Kapsel Mode)",
        "输入 'kps ' 加空格",
        "瞬间切入 Linux 指令映射库；Tab 唤起富文本中文候选菜单与底层真实代码预览",
    )
    console.print(mode_table)
    console.print()

    # 2. 内置命令
    builtin_table = Table(title="🛠️ 内置控制台指令", box=None, title_justify="left", padding=(0, 2))
    builtin_table.add_column("指令", style="bold #a855f7", width=18)
    builtin_table.add_column("功能说明", style="#e4e4e7")

    builtin_table.add_row("help", "显示本帮助指南与指令速查表")
    builtin_table.add_row("status / info", "查看当前宿主 Shell、运行权限、数据沙箱与系统详细状态")
    builtin_table.add_row("config [subcmd]", "查看/修改核心配置（支持 config path, config edit, config set, config reload）")
    builtin_table.add_row("repo [subcmd]", "📦 访问指令云仓库 (支持 repo list, search, info, pull, mappings)")
    builtin_table.add_row("register [user]", "注册胶囊用户身份，为跨端云同步做准备")
    builtin_table.add_row("whoami / user", "查看当前设备登录的胶囊用户与设备秘钥")
    builtin_table.add_row("cd [path]", "切换当前目录（支持 cd ~ 家目录、cd - 返回上一目录、cd .. 上级目录）")
    builtin_table.add_row("clear / cls", "清除终端屏幕并重绘胶囊徽标")
    builtin_table.add_row("exit / quit", "安全退出 Kapsel 终端胶囊，无痕返回宿主原生 Shell")
    console.print(builtin_table)
    console.print()

    # 3. 常用 Linux 映射速查
    reg = load_commands()
    linux_table = Table(title=f"📋 常用 Linux-First 跨平台映射速查 ({len(reg.commands)} 条指令已就绪)", box=None, title_justify="left", padding=(0, 2))
    linux_table.add_column("Linux 指令 (kps)", style="bold #00f0ff", width=20)
    linux_table.add_column("功能说明", style="#e4e4e7", width=30)
    linux_table.add_column("当前终端自动转义示例", style="italic #a855f7")

    shell_name, _ = detector.detect_shell()
    # Pick representative samples
    samples = ["rm -rf", "rm", "ls -la", "cat", "touch", "cp -r", "mv", "mkdir -p", "ps", "kill -9", "grep", "find", "which", "df -h", "free -m", "clear"]
    for alias in samples:
        entry = reg.get(alias)
        if entry:
            tmpl = entry.get_template_for_shell(shell_name) or ""
            clean_tmpl = tmpl.replace("{{args}}", "...").strip()
            linux_table.add_row(f"kps {alias}", entry.desc, clean_tmpl)

    console.print(linux_table)
    console.print()

    # 4. 快捷键
    key_table = Table(title="⌨️ 常用快捷键与灵敏交互", box=None, title_justify="left", padding=(0, 2))
    key_table.add_column("按键", style="bold #38bdf8", width=18)
    key_table.add_column("作用说明", style="#e4e4e7")

    key_table.add_row("Tab", "触发当前上下文补全（Native 模式补全路径 / Kapsel 模式展示候选菜单）")
    key_table.add_row(
        "→ (右方向键)",
        "【轻按 Tap】逐词采纳下一个参数；【长按/连按 Hold】直接一键采纳整行命令（阈值可调）",
    )
    key_table.add_row("↑ (上方向键)", "专注历史记录漫游（向上调出历史输入的上一条命令）")
    key_table.add_row("↓ (下方向键)", "一键唤起并循环切换补全候选词（如 git 的 status, add, commit, push 等）")
    key_table.add_row("Shift + Tab", "在补全菜单中向上回退选中的候选词")
    key_table.add_row("Ctrl + C", "取消当前行输入，开始新的一行")
    key_table.add_row("Ctrl + D", "退出当前会话")
    console.print(key_table)
    console.print()


def render_status(console: Optional[Console] = None) -> None:
    """Renders the detailed Kapsel environment and runtime status dashboard."""
    ensure_utf8_io()
    if console is None:
        console = Console(legacy_windows=False)

    from kapsel.storage.user import UserManager
    current_user = UserManager.get_current_user()

    shell_name, shell_path = detector.detect_shell()
    is_elevated, elevated_label = detector.is_elevated()
    cwd_raw = Path.cwd()
    cwd_fmt = detector.format_cwd(cwd_raw)
    branch = detector.get_git_branch(cwd_raw)
    reg = load_commands()
    cfg = load_config()
    sandbox_dir = get_kapsel_dir()
    db_path = get_history_db_path()

    # Get history stats
    history_count = 0
    weight_count = 0
    if db_path.exists():
        try:
            with sqlite3.connect(str(db_path)) as conn:
                cur = conn.cursor()
                cur.execute("SELECT COUNT(*) FROM history")
                history_count = cur.fetchone()[0]
                cur.execute("SELECT COUNT(*) FROM command_weights")
                weight_count = cur.fetchone()[0]
        except Exception:
            pass

    # Status Grid
    grid = Table.grid(expand=True, padding=(0, 2))
    grid.add_column(style="bold #00f0ff", justify="right", width=18)
    grid.add_column(style="#e4e4e7")
    grid.add_column(style="bold #a855f7", justify="right", width=18)
    grid.add_column(style="#e4e4e7")

    priv_badge = f"[bold #10b981][{elevated_label}][/]" if not is_elevated else f"[bold #f59e0b][{elevated_label} (管理员)][/]"

    user_label = f"[bold #00f0ff]@{current_user.username}[/]" if current_user else "[dim]未注册 (输入 'register' 注册)[/]"
    sync_label = "[bold #10b981]● 云同步已就绪[/]" if current_user else "[dim]未配置 (支持多端同步)[/]"

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
        f"[bold #10b981]{len(reg.commands)}[/] 条自适应映射就绪",
        "🕒 历史漫游库:",
        f"[bold #10b981]{history_count}[/] 条历史记录 / [bold #a855f7]{weight_count}[/] 个高频权重词",
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

    console.print()
    console.print(panel)
    console.print()
