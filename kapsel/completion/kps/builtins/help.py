"""
Kapsel Help Command.
Provides comprehensive manual and quick-reference cheatsheets.
"""

from typing import List, Optional

from rich.console import Console
from rich.table import Table
from rich.text import Text

from kapsel import __version__
from kapsel.ui.banner import ensure_utf8_io


def handle_help(args: Optional[List[str]] = None, console: Optional[Console] = None) -> int:
    """Renders the comprehensive Kapsel help manual."""
    ensure_utf8_io()
    con = console or Console(legacy_windows=False)

    con.print()

    # Header
    header = Text()
    header.append("💊 KAPSEL  ", style="bold #00f0ff")
    header.append(f"v{__version__}  ·  使用指南与命令速查手册\n", style="dim #6b7280")
    header.append("核心哲学: 包裹复杂，暴露极简。统一交互体验，极简微内核与插件化扩展。\n", style="italic #9ca3af")
    con.print(header)

    # 1. 核心交互机制
    mode_table = Table(title="🚀 核心交互机制", box=None, title_justify="left", padding=(0, 2))
    mode_table.add_column("模式", style="bold #00f0ff", width=18)
    mode_table.add_column("触发方式", style="#e4e4e7", width=22)
    mode_table.add_column("行为描述", style="dim #9ca3af")

    mode_table.add_row(
        "默认态 (Native Mode)",
        "直接输入任何系统命令",
        "100% 原生命令无感透传执行（git, npm, vim, python 等）；Tab 补全本地路径与工具",
    )
    mode_table.add_row(
        "胶囊态 (Kapsel Mode)",
        "输入 'kps ' 加空格",
        "唤起统一控制台指令或插件注册扩展；Tab 唤起富文本补全候选菜单",
    )
    con.print(mode_table)
    con.print()

    # 2. 核心控制台指令 (从注册表获取)
    from kapsel.completion.kps.registry import get_kps_registry
    registry = get_kps_registry()
    commands = registry.list_commands()

    builtin_table = Table(title="🛠️ 控制台指令集 (Core & Plugins)", box=None, title_justify="left", padding=(0, 2))
    builtin_table.add_column("指令", style="bold #a855f7", width=18)
    builtin_table.add_column("功能说明", style="#e4e4e7")
    builtin_table.add_column("归属", style="dim #9ca3af", width=12)

    for cmd in commands:
        origin = f"插件:{cmd.plugin_id}" if cmd.plugin_id else "Core 核心"
        builtin_table.add_row(f"kps {cmd.name}", cmd.help_text, origin)

    builtin_table.add_row("exit / quit", "安全退出 Kapsel 终端胶囊，无痕返回宿主原生 Shell", "Core 核心")
    con.print(builtin_table)
    con.print()

    # 3. 插件化机制说明
    plugin_info = Text()
    plugin_info.append("🔌 插件化扩展体系\n", style="bold #10b981")
    plugin_info.append("Kapsel 采用微内核设计，映射、云服务及第三方功能均可通过插件无缝挂载。\n", style="dim #9ca3af")
    plugin_info.append("插件可通过实现 KapselPlugin 并放置于 ./plugins 目录即刻生效。\n", style="dim #6b7280")
    con.print(plugin_info)
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
