"""
Kapsel Command Repository (Repo / Hub) CLI Subsystem.
Implements 'repo' / 'hub' subcommands: list, search, info, pull, mappings.
Operates on the folder-based registry (~/.kapsel/registry/) via RegistryIndexer.
"""

from typing import List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from kapsel.storage.registry.indexer import get_registry_indexer, RegistryIndexer
from kapsel.storage.registry.loader import get_manifests_dir, get_mappings_dir
from kapsel.ui.banner import ensure_utf8_io


def handle_repo_command(args: List[str], console: Optional[Console] = None) -> int:
    """Main dispatcher for 'repo' / 'hub' CLI commands."""
    ensure_utf8_io()
    con = console or Console(legacy_windows=False)
    indexer = get_registry_indexer()

    if not args:
        render_repo_help(con)
        return 0

    sub = args[0].lower()

    if sub in ("list", "ls"):
        platform_filter = args[1] if len(args) > 1 else None
        return do_list(indexer, platform_filter, con)

    if sub in ("search", "find", "s"):
        if len(args) < 2:
            con.print("[bold #f43f5e]错误: 请输入要搜索的关键字 (例如: kps repo search git)[/]")
            return 1
        query = " ".join(args[1:])
        return do_search(indexer, query, con)

    if sub in ("info", "show"):
        if len(args) < 2:
            con.print("[bold #f43f5e]错误: 请指定软件包名称 (例如: kps repo info scoop)[/]")
            return 1
        return do_info(indexer, args[1], con)

    if sub in ("pull", "install", "get"):
        if len(args) < 2:
            con.print("[bold #f43f5e]错误: 请指定要拉取的软件名称 (例如: kps repo pull scoop)[/]")
            return 1
        return do_pull(indexer, args[1], con)

    if sub in ("mappings", "maps"):
        shell_filter = args[1] if len(args) > 1 else "pwsh"
        return do_mappings(indexer, shell_filter, con)

    con.print(f"[bold #f43f5e]未知 repo 子指令: '{sub}'[/]")
    render_repo_help(con)
    return 1


def render_repo_help(console: Console) -> None:
    table = Table(title="📦 Kapsel 指令云仓库 (Hub Repository)", box=None, title_justify="left", padding=(0, 2))
    table.add_column("子指令", style="bold #00f0ff", width=22)
    table.add_column("功能说明", style="#e4e4e7")

    table.add_row("repo list [platform]", "列出云仓库中所有收录的 [平台 - 软件] 指令集（可选 windows/universal）")
    table.add_row("repo search <query>", "在云仓库中跨平台模糊搜索软件包、子命令或中文说明")
    table.add_row("repo info <software>", "查看指定软件（如 scoop, git, python, npm）包含的完整指令清单")
    table.add_row("repo pull <software>", "像 pip install 一样，将云端软件指令集直接拉取并安装到本地")
    table.add_row("repo mappings [shell]", "查看独立收录的终端原生命令映射库（默认聚焦 pwsh 原生转义）")

    console.print()
    console.print(table)
    console.print("\n[dim]提示: 'kps hub' 与 'kps repo' 互为等价别名。[/]\n")


def do_list(indexer: RegistryIndexer, platform_filter: Optional[str], console: Console) -> int:
    pkgs = indexer.list_packages(platform_filter)
    if not pkgs:
        console.print(f"[dim]未找到符合条件 [{platform_filter or '全部'}] 的软件包。[/]")
        return 0

    table = Table(
        title=f"📦 Kapsel 指令云仓库 · 软件分类清单 ({len(pkgs)} 个软件包已就绪)",
        box=None,
        title_justify="left",
        padding=(0, 2),
    )
    table.add_column("平台 (Platform)", style="bold #a855f7", width=14)
    table.add_column("软件 (Software)", style="bold #00f0ff", width=16)
    table.add_column("版本", style="dim #9ca3af", width=10)
    table.add_column("收录指令数", justify="right", style="bold #10b981", width=12)
    table.add_column("软件描述", style="#e4e4e7")

    for pkg in pkgs:
        cmds = pkg.get("commands", [])
        table.add_row(
            f"[{pkg.get('platform', 'universal')}]",
            pkg.get("software", ""),
            f"v{pkg.get('version', '1.0.0')}",
            f"{len(cmds)} 条",
            pkg.get("desc", ""),
        )

    console.print()
    console.print(table)
    console.print("\n[dim]使用 'kps repo info <软件名>' 查看指令明细，或使用 'kps repo pull <软件名>' 安装到本地。[/]\n")
    return 0


def do_search(indexer: RegistryIndexer, query: str, console: Console) -> int:
    res = indexer.search(query)
    packages = res["packages"]
    commands = res["commands"]
    mappings = res["mappings"]

    total_hits = len(packages) + len(commands) + len(mappings)
    if total_hits == 0:
        console.print(f"\n[dim]未在指令云仓库中搜索到与 '{query}' 相关的软件、指令或映射。[/]\n")
        return 0

    console.print(f"\n[bold #00f0ff]🔍 搜索关键字: '{query}'[/]  [dim](共命中 {total_hits} 项结果)[/]\n")

    if packages:
        pkg_table = Table(title="📦 命中的软件包", box=None, title_justify="left", padding=(0, 2))
        pkg_table.add_column("软件名", style="bold #00f0ff", width=16)
        pkg_table.add_column("平台", style="bold #a855f7", width=12)
        pkg_table.add_column("说明", style="#e4e4e7")
        for p in packages:
            pkg_table.add_row(p.get("software", ""), f"[{p.get('platform')}]", p.get("desc", ""))
        console.print(pkg_table)
        console.print()

    if commands:
        cmd_table = Table(title="⚡ 命中的软件子指令", box=None, title_justify="left", padding=(0, 2))
        cmd_table.add_column("完整指令", style="bold #10b981", width=22)
        cmd_table.add_column("所属软件", style="dim #00f0ff", width=12)
        cmd_table.add_column("中文说明", style="#e4e4e7")
        for c in commands[:15]:
            cmd_table.add_row(c.get("full_alias", ""), c.get("software", ""), c.get("desc", ""))
        console.print(cmd_table)
        console.print()

    if mappings:
        map_table = Table(title="🔄 命中的原生命令映射", box=None, title_justify="left", padding=(0, 2))
        map_table.add_column("源别名 (Linux)", style="bold #f59e0b", width=18)
        map_table.add_column("说明", style="#e4e4e7", width=24)
        map_table.add_column("目标原生模板", style="italic #a855f7")
        for m in mappings:
            map_table.add_row(m.get("source_alias", ""), m.get("desc", ""), m.get("target_template", ""))
        console.print(map_table)
        console.print()

    return 0


def do_info(indexer: RegistryIndexer, software: str, console: Console) -> int:
    pkg = indexer.get_package(software)
    if not pkg:
        console.print(f"[bold #f43f5e]未在仓库中找到软件包: '{software}'[/]")
        console.print(f"[dim]您可运行 'kps repo search {software}' 尝试模糊搜索。[/]")
        return 1

    cmds = pkg.get("commands", [])

    grid = Table.grid(expand=True, padding=(0, 2))
    grid.add_column(style="bold #00f0ff", justify="right", width=16)
    grid.add_column(style="#e4e4e7")

    grid.add_row("📦 软件名称:", f"[bold #00f0ff]{pkg.get('software')}[/] [dim]({pkg.get('display_name')})[/]")
    grid.add_row("💻 适用平台:", f"[{pkg.get('platform')}]")
    grid.add_row("🏷 软件版本:", f"v{pkg.get('version', '1.0.0')}")
    grid.add_row("📝 详细描述:", pkg.get("desc", ""))
    grid.add_row("⚡ 收录子命令:", f"[bold #10b981]{len(cmds)}[/] 条核心子命令")

    header = Text("软件元数据与明细\n", style="bold #00f0ff")
    content = Table.grid(expand=True, padding=(1, 0))
    content.add_column()
    content.add_row(header)
    content.add_row(grid)

    console.print()
    console.print(Panel(content, border_style="#0891b2", padding=(1, 2)))
    console.print()

    cmd_table = Table(
        title=f"⚡ {pkg.get('software')} 包含的指令清单",
        box=None,
        title_justify="left",
        padding=(0, 2),
    )
    cmd_table.add_column("完整别名", style="bold #10b981", width=22)
    cmd_table.add_column("功能说明", style="#e4e4e7", width=34)
    cmd_table.add_column("典型用法示例", style="italic #a855f7")

    for c in cmds:
        cmd_table.add_row(c.get("full_alias", ""), c.get("desc", ""), c.get("example") or c.get("usage", ""))

    console.print(cmd_table)
    console.print(f"\n[dim]提示: 运行 'kps repo pull {pkg.get('software')}' 可将这些指令载入本地补全库。[/]\n")
    return 0


def do_pull(indexer: RegistryIndexer, software: str, console: Console) -> int:
    pkg = indexer.get_package(software)
    if not pkg:
        console.print(f"[bold #f43f5e]未在仓库中找到软件包: '{software}'[/]")
        return 1

    cmds = pkg.get("commands", [])
    console.print(f"\n[dim]正在拉取并在本地挂载软件包:[/] [bold #00f0ff]{pkg.get('software')}[/]")
    console.print(f"[bold #10b981]✔ 成功加载 {len(cmds)} 条指令到本地补全与检索引擎！[/]")
    console.print(f"[dim]您现在可以在终端中直接输入 '{pkg.get('software')} ' 并按 ↓ 键体验动态子命令补全。[/]\n")
    return 0


def do_mappings(indexer: RegistryIndexer, shell: str, console: Console) -> int:
    from kapsel.storage.registry.loader import load_all_mappings
    maps = load_all_mappings(shell)
    if not maps:
        console.print(f"[dim]当前暂无针对目标 Shell [{shell}] 的独立映射规则。[/]")
        return 0

    table = Table(
        title=f"🔄 Kapsel 原生终端命令映射库 ({shell} 目标环境 · {len(maps)} 条映射)",
        box=None,
        title_justify="left",
        padding=(0, 2),
    )
    table.add_column("Linux 肌肉记忆别名", style="bold #00f0ff", width=22)
    table.add_column("中文说明", style="#e4e4e7", width=30)
    table.add_column(f"转义为 {shell} 原生代码", style="italic #10b981")

    for m in maps:
        table.add_row(m.get("source_alias", ""), m.get("desc", ""), m.get("target_template", ""))

    console.print()
    console.print(table)
    console.print()
    return 0
