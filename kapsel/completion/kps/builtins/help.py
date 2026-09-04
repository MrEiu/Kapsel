"""
Kapsel Help Command.
Provides comprehensive manual and quick-reference cheatsheets.
Separates system management commands (kapsel) from feature extension commands (kps).
"""

from typing import List, Optional

from rich.console import Console
from rich.table import Table
from rich.text import Text

from kapsel import __version__
from kapsel.completion.kps.registry import get_kps_registry
from kapsel.ui.banner import ensure_utf8_io


def handle_help(args: Optional[List[str]] = None, console: Optional[Console] = None) -> int:
    """Renders the comprehensive Kapsel help manual with distinct command scopes."""
    ensure_utf8_io()
    con = console or Console(legacy_windows=False)

    con.print()

    # Header
    header = Text()
    header.append("💊 KAPSEL  ", style="bold #00f0ff")
    header.append(f"v{__version__}  ·  使用指南与命令速查手册\n", style="dim #6b7280")
    header.append("核心架构: kapsel / kps (统一胶囊交互管道，kps 为官方快捷缩写)\n", style="italic #9ca3af")
    con.print(header)

    # 1. 核心交互机制
    mode_table = Table(title="🚀 核心交互双态", box=None, title_justify="left", padding=(0, 2))
    mode_table.add_column("模式", style="bold #00f0ff", width=18)
    mode_table.add_column("触发方式", style="#e4e4e7", width=24)
    mode_table.add_column("行为描述", style="dim #9ca3af")

    mode_table.add_row(
        "默认态 (Native Mode)",
        "直接输入原生系统命令",
        "100% 原生命令透传执行（git, docker, npm, vim, python 等）；Carapace 深度上下文感知补全",
    )
    mode_table.add_row(
        "胶囊态 (Kapsel Mode)",
        "输入 'kapsel ' 或 'kps '",
        "统一胶囊指令（help, status, config, datadir, add, toggle 及插件扩展）；Tab 展开候选",
    )
    con.print(mode_table)
    con.print()

    registry = get_kps_registry()
    all_cmds = registry.list_commands()

    # 2. 胶囊指令列表
    cmd_table = Table(title="⚙️ 胶囊指令集 (Kapsel Commands - 支持 kapsel / kps 互通调用)", box=None, title_justify="left", padding=(0, 2))
    cmd_table.add_column("指令", style="bold #00f0ff", width=22)
    cmd_table.add_column("功能说明", style="#e4e4e7")
    cmd_table.add_column("来源", style="dim #9ca3af", width=14)

    for cmd in all_cmds:
        origin = f"[{cmd.plugin_id}]" if cmd.plugin_id else "Core 核心"
        cmd_table.add_row(f"kps {cmd.name}", cmd.help_text, origin)

    cmd_table.add_row("exit / quit", "安全退出 Kapsel 终端胶囊，无痕返回宿主原生 Shell", "Core 核心")
    con.print(cmd_table)
    con.print()

    # 4. 快捷键指南
    key_table = Table(title="⌨️ 常用快捷键与灵敏交互", box=None, title_justify="left", padding=(0, 2))
    key_table.add_column("按键", style="bold #38bdf8", width=18)
    key_table.add_column("功能说明", style="#e4e4e7")

    key_table.add_row("Tab", "触发自动补全候选菜单")
    key_table.add_row("↑ (方向键上)", "按时间线反向漫游浏览执行历史")
    key_table.add_row("↓ (方向键下)", "在自动补全候选菜单或软件子命令间切换轮询")
    key_table.add_row("→ (轻按一次)", "逐词 (Word-by-word) 采纳灰色行内预测内容")
    key_table.add_row("→ (连续长按)", "一键采纳整行完整命令")
    key_table.add_row("Ctrl + C", "取消当前输入行")
    key_table.add_row("Ctrl + D", "安全退出终端胶囊")
    con.print(key_table)
    con.print()
    return 0
