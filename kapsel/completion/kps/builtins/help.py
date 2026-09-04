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
    header.append("核心架构: kapsel (系统管理指令)  │  kps (插件扩展与功能指令)\n", style="italic #9ca3af")
    con.print(header)

    # 1. 核心交互机制
    mode_table = Table(title="🚀 核心交互双态", box=None, title_justify="left", padding=(0, 2))
    mode_table.add_column("模式", style="bold #00f0ff", width=18)
    mode_table.add_column("触发方式", style="#e4e4e7", width=22)
    mode_table.add_column("行为描述", style="dim #9ca3af")

    mode_table.add_row(
        "默认态 (Native Mode)",
        "直接输入原生系统命令",
        "100% 原生命令透传执行（git, npm, vim, python 等）；Tab 补全本地路径与原生工具",
    )
    mode_table.add_row(
        "系统态 (System Mode)",
        "输入 'kapsel '",
        "管理胶囊自身环境与配置（help, status, config, datadir）；Tab 展开管理指令",
    )
    mode_table.add_row(
        "功能态 (Feature Mode)",
        "输入 'kps '",
        "执行插件扩展功能与工具（install, update, search, sync 等）；Tab 展开功能指令",
    )
    con.print(mode_table)
    con.print()

    registry = get_kps_registry()
    system_cmds = registry.list_system_commands()
    feature_cmds = registry.list_feature_commands()

    # 2. 系统管理指令 (kapsel <cmd>)
    sys_table = Table(title="⚙️ kapsel 系统管理指令 (System Commands)", box=None, title_justify="left", padding=(0, 2))
    sys_table.add_column("指令", style="bold #00f0ff", width=22)
    sys_table.add_column("功能说明", style="#e4e4e7")
    sys_table.add_column("类型", style="dim #9ca3af", width=12)

    for cmd in system_cmds:
        sys_table.add_row(f"kapsel {cmd.name}", cmd.help_text, "Core 核心")

    sys_table.add_row("exit / quit", "安全退出 Kapsel 终端胶囊，无痕返回宿主原生 Shell", "Core 核心")
    con.print(sys_table)
    con.print()

    # 3. 扩展功能指令 (kps <cmd>)
    if feature_cmds:
        feat_table = Table(title="🚀 kps 扩展功能指令 (Feature & Plugin Commands)", box=None, title_justify="left", padding=(0, 2))
        feat_table.add_column("指令", style="bold #a855f7", width=22)
        feat_table.add_column("功能说明", style="#e4e4e7")
        feat_table.add_column("提供插件", style="dim #9ca3af", width=12)

        for cmd in feature_cmds:
            origin = f"[{cmd.plugin_id}]" if cmd.plugin_id else "[builtin]"
            feat_table.add_row(f"kps {cmd.name}", cmd.help_text, origin)

        con.print(feat_table)
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
