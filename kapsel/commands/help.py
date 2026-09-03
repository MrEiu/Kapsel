"""
Kapsel Help Command.
Provides comprehensive manual and quick-reference cheatsheets.
"""

from typing import List, Optional

from rich.console import Console
from rich.table import Table
from rich.text import Text

from kapsel import __version__
from kapsel.core.detector import detector
from kapsel.storage.registry.indexer import get_registry_indexer
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
    header.append("核心哲学: 包裹复杂，暴露极简。统一 Linux 肌肉记忆，零侵入原生 Shell。\n", style="italic #9ca3af")
    con.print(header)

    # 1. 核心交互机制
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
    con.print(mode_table)
    con.print()

    # 2. 内置控制台指令
    builtin_table = Table(title="🛠️ 内置控制台指令", box=None, title_justify="left", padding=(0, 2))
    builtin_table.add_column("指令", style="bold #a855f7", width=18)
    builtin_table.add_column("功能说明", style="#e4e4e7")

    builtin_table.add_row("help", "显示本帮助指南与指令速查表")
    builtin_table.add_row("status / info", "查看当前宿主 Shell、运行权限、数据沙箱与系统详细状态")
    builtin_table.add_row("config [subcmd]", "查看/修改核心配置（支持 config path, config edit, config set, config reload）")
    builtin_table.add_row("datadir [path]", "📂 查看或自定义迁移数据存储位置 (自动将旧数据完整搬迁，不留旧痕)")
    builtin_table.add_row("repo [subcmd]", "📦 访问指令云仓库 (支持 repo list, search, info, pull, fig, mappings)")
    builtin_table.add_row("register [user]", "注册胶囊用户身份，为跨端云同步做准备")
    builtin_table.add_row("whoami / user", "查看当前设备登录的胶囊用户与设备秘钥")
    builtin_table.add_row("cd [path]", "切换当前目录（支持 cd ~ 家目录、cd - 返回上一目录、cd .. 上级目录）")
    builtin_table.add_row("clear / cls", "清除终端屏幕并重绘胶囊徽标")
    builtin_table.add_row("exit / quit", "安全退出 Kapsel 终端胶囊，无痕返回宿主原生 Shell")
    con.print(builtin_table)
    con.print()

    # 3. 常用 Linux 映射速查
    indexer = get_registry_indexer()
    all_cmds = indexer.list_all_commands()
    linux_table = Table(title=f"📋 常用 Linux-First 跨平台映射速查 ({len(all_cmds)} 条指令已就绪)", box=None, title_justify="left", padding=(0, 2))
    linux_table.add_column("Linux 指令 (kps)", style="bold #00f0ff", width=20)
    linux_table.add_column("功能说明", style="#e4e4e7", width=30)
    linux_table.add_column("当前终端自动转义示例", style="italic #a855f7")

    shell_name, _ = detector.detect_shell()
    samples = ["rm -rf", "rm", "ls -la", "cat", "touch", "cp -r", "mv", "mkdir -p", "ps", "kill -9", "grep", "find", "which", "df -h", "free -m", "clear"]
    for alias in samples:
        entry, _ = indexer.find_best_match(alias) or (None, "")
        if entry:
            tmpl = entry.get_template_for_shell(shell_name) or ""
            clean_tmpl = tmpl.replace("{{args}}", "...").strip()
            linux_table.add_row(f"kps {alias}", entry.desc, clean_tmpl)

    con.print(linux_table)
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
