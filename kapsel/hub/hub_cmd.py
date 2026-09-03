"""
CLI command handlers for Kapsel Cloud Hub & Command Repository.
Implements 'repo' / 'hub' commands: list, search, info, pull/install, mappings.
"""

from typing import List, Optional
import yaml

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from kapsel.hub.db import HubRepository
from kapsel.hub.seed import seed_hub_database
from kapsel.storage.commands import get_commands_path, load_commands
from kapsel.ui.banner import ensure_utf8_io


def get_initialized_repo() -> HubRepository:
    """Returns an initialized HubRepository instance, seeding it if empty."""
    repo = HubRepository()
    pkgs = repo.list_packages()
    if not pkgs:
        seed_hub_database(repo)
    return repo


def handle_repo_command(args: List[str], console: Optional[Console] = None) -> int:
    """
    Main dispatcher for 'repo' / 'hub' CLI commands.
    Supported subcommands:
      - list [platform]
      - search <query>
      - info <software>
      - pull / install <software>
      - mappings [shell]
    """
    ensure_utf8_io()
    if console is None:
        console = Console(legacy_windows=False)

    repo = get_initialized_repo()

    if not args or args[0] in ("help", "-h", "--help"):
        render_repo_help(console)
        return 0

    sub = args[0].lower()

    if sub == "list":
        platform_filter = args[1] if len(args) > 1 else None
        return do_list(repo, platform_filter, console)

    if sub == "search":
        if len(args) < 2:
            console.print("[bold #f43f5e]✘ 请提供搜索关键词[/]: 例如 'kps repo search scoop' 或 'kps repo search git'")
            return 1
        query = " ".join(args[1:])
        return do_search(repo, query, console)

    if sub in ("info", "show"):
        if len(args) < 2:
            console.print("[bold #f43f5e]✘ 请提供软件名称[/]: 例如 'kps repo info scoop' 或 'kps repo info git'")
            return 1
        software = args[1].lower()
        return do_info(repo, software, console)

    if sub in ("pull", "install", "add"):
        if len(args) < 2:
            console.print("[bold #f43f5e]✘ 请提供软件名称[/]: 例如 'kps repo pull scoop' 或 'kps repo pull git'")
            return 1
        software = args[1].lower()
        return do_pull(repo, software, console)

    if sub in ("mappings", "maps"):
        shell_filter = args[1] if len(args) > 1 else "pwsh"
        return do_mappings(repo, shell_filter, console)

    if sub in ("admin", "manage"):
        from kapsel.hub.admin import main as admin_main
        return admin_main(args[1:])

    console.print(f"[bold #f43f5e]未知 repo 子指令: '{sub}'[/]")
    render_repo_help(console)
    return 1


def render_repo_help(console: Console) -> None:
    """Prints the help manual for repo/hub."""
    table = Table(title="📦 Kapsel 指令云仓库 (Hub Repository)", box=None, title_justify="left", padding=(0, 2))
    table.add_column("子指令", style="bold #00f0ff", width=22)
    table.add_column("功能说明", style="#e4e4e7")

    table.add_row("repo list [platform]", "列出云仓库中所有收录的 [平台 - 软件] 指令集（可选 windows/universal）")
    table.add_row("repo search <query>", "在云仓库中跨平台模糊搜索软件包、子命令或中文说明")
    table.add_row("repo info <software>", "查看指定软件（如 scoop, git, python, npm）包含的完整指令清单")
    table.add_row("repo pull <software>", "像 pip install 一样，将云端软件指令集直接拉取并安装到本地 commands.yaml")
    table.add_row("repo mappings [shell]", "查看独立收录的终端原生命令映射库（默认聚焦 pwsh 原生转义）")
    table.add_row("repo admin [subcmd]", "🛠️ 启动独立云仓库 CRUD 管理终端 (支持 pkg/cmd/map 的增删改查与导入导出)")

    console.print()
    console.print(table)
    console.print("\n[dim]提示: 也可直接在终端运行独立命令 'kps-hub' 进行仓库全量管理。[/]\n")


def do_list(repo: HubRepository, platform_filter: Optional[str], console: Console) -> int:
    """Lists packages grouped by platform."""
    pkgs = repo.list_packages(platform_filter)
    if not pkgs:
        console.print(f"[dim]云仓库中未找到匹配平台 '{platform_filter}' 的软件包。[/]")
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
        cmds = repo.get_commands_for_software(pkg["software"], pkg["platform"])
        table.add_row(
            f"[{pkg['platform']}]",
            pkg["software"],
            f"v{pkg['version']}",
            f"{len(cmds)} 条",
            pkg["desc"],
        )

    console.print()
    console.print(table)
    console.print("\n[dim]使用 'kps repo info <软件名>' 查看指令明细，或使用 'kps repo pull <软件名>' 安装到本地。[/]\n")
    return 0


def do_search(repo: HubRepository, query: str, console: Console) -> int:
    """Searches packages, commands, and mappings."""
    res = repo.search(query)
    packages = res["packages"]
    commands = res["commands"]
    mappings = res["mappings"]

    total = len(packages) + len(commands) + len(mappings)
    if total == 0:
        console.print(f"[dim]云仓库中未搜索到与 '{query}' 相关的软件包或指令。[/]")
        return 0

    console.print(f"\n[bold #00f0ff]🔍 搜索结果: '{query}' (共命中 {total} 项)[/]\n")

    if packages:
        pkg_table = Table(title="📦 匹配的软件包 (Packages)", box=None, padding=(0, 2))
        pkg_table.add_column("软件", style="bold #00f0ff", width=14)
        pkg_table.add_column("平台", style="bold #a855f7", width=12)
        pkg_table.add_column("描述", style="#e4e4e7")
        for p in packages:
            pkg_table.add_row(p["software"], f"[{p['platform']}]", p["desc"])
        console.print(pkg_table)
        console.print()

    if commands:
        cmd_table = Table(title="⚡ 匹配的指令集 (Commands)", box=None, padding=(0, 2))
        cmd_table.add_column("所属软件", style="bold #a855f7", width=12)
        cmd_table.add_column("指令别名", style="bold #00f0ff", width=20)
        cmd_table.add_column("功能说明", style="#e4e4e7")
        cmd_table.add_column("示例用例", style="dim italic #9ca3af")
        for c in commands:
            cmd_table.add_row(c["software"], c["full_alias"], c["desc"], c["example"])
        console.print(cmd_table)
        console.print()

    if mappings:
        map_table = Table(title="🎯 匹配的原生映射 (PWSH Mappings)", box=None, padding=(0, 2))
        map_table.add_column("源指令", style="bold #00f0ff", width=16)
        map_table.add_column("目标终端", style="bold #a855f7", width=10)
        map_table.add_column("原生转义模板", style="#10b981", width=32)
        map_table.add_column("说明", style="#e4e4e7")
        for m in mappings:
            map_table.add_row(m["source_alias"], m["target_shell"], m["target_template"], m["desc"])
        console.print(map_table)
        console.print()

    return 0


def do_info(repo: HubRepository, software: str, console: Console) -> int:
    """Shows detailed information for a software package."""
    pkg = repo.get_package(software)
    if not pkg:
        console.print(f"[bold #f43f5e]未在云仓库中找到软件: '{software}'[/]")
        console.print("[dim]提示: 运行 'kps repo list' 查看当前所有可用软件包。[/]")
        return 1

    cmds = repo.get_commands_for_software(pkg["software"], pkg["platform"])

    # Header Card
    grid = Table.grid(expand=True, padding=(0, 2))
    grid.add_column(style="bold #00f0ff", justify="right", width=14)
    grid.add_column(style="#e4e4e7")
    grid.add_column(style="bold #a855f7", justify="right", width=14)
    grid.add_column(style="#e4e4e7")

    grid.add_row("软件标识:", f"[bold #00f0ff]{pkg['software']}[/]", "支持平台:", f"[bold #a855f7]{pkg['platform']}[/]")
    grid.add_row("软件全名:", pkg["display_name"], "版本编号:", f"v{pkg['version']}")
    grid.add_row("软件类别:", pkg["category"], "原作者/维护者:", pkg["author"])
    grid.add_row("软件描述:", pkg["desc"], "收录指令数:", f"[bold #10b981]{len(cmds)} 条指令[/]")

    panel = Panel(
        grid,
        title=f"📦 软件包详情 · {pkg['software']}",
        border_style="#0891b2",
        padding=(1, 2),
    )
    console.print()
    console.print(panel)
    console.print()

    # Commands Table
    cmd_table = Table(title=f"📋 '{pkg['software']}' 收录的核心指令列表", box=None, padding=(0, 2))
    cmd_table.add_column("子命令", style="bold #00f0ff", width=16)
    cmd_table.add_column("完整指令别名", style="bold #38bdf8", width=22)
    cmd_table.add_column("功能说明", style="#e4e4e7", width=30)
    cmd_table.add_column("语法 / 示例用例", style="italic #a855f7")

    for c in cmds:
        cmd_table.add_row(c["command_name"], c["full_alias"], c["desc"], c["example"])

    console.print(cmd_table)
    console.print(f"\n[bold #10b981]✔ 提示:[/] 输入 [bold #00f0ff]'kps repo pull {pkg['software']}'[/] 可一键导入并激活上述指令！\n")
    return 0


def do_pull(repo: HubRepository, software: str, console: Console) -> int:
    """
    Pulls command definitions from the Hub into local commands.yaml (like pip install).
    """
    pkg = repo.get_package(software)
    if not pkg:
        console.print(f"[bold #f43f5e]未在云仓库中找到软件: '{software}'[/]")
        return 1

    cmds = repo.get_commands_for_software(pkg["software"], pkg["platform"])
    if not cmds:
        console.print(f"[dim]软件 '{software}' 暂无可用指令可导入。[/]")
        return 0

    commands_path = get_commands_path()
    local_data = {}
    raw_list = []
    if commands_path.exists():
        try:
            with open(commands_path, "r", encoding="utf-8") as f:
                local_data = yaml.safe_load(f) or {}
                raw_list = local_data.get("commands", [])
        except Exception:
            raw_list = []

    existing_aliases = {item.get("alias") for item in raw_list if isinstance(item, dict)}

    imported_count = 0
    for c in cmds:
        alias = c["full_alias"]
        if alias not in existing_aliases:
            raw_list.append({
                "alias": alias,
                "desc": c["desc"],
                "mapping": {
                    "powershell": f"{alias} {{{{args}}}}",
                    "pwsh": f"{alias} {{{{args}}}}",
                    "unix": f"{alias} {{{{args}}}}",
                },
            })
            existing_aliases.add(alias)
            imported_count += 1

    try:
        with open(commands_path, "w", encoding="utf-8") as f:
            yaml.dump({"commands": raw_list}, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        console.print(f"\n[bold #10b981]🎉 成功拉取并安装 '{pkg['software']}' 指令集！[/]")
        console.print(f"  • 新导入指令: [bold #00f0ff]{imported_count}[/] 条")
        console.print(f"  • 本地总指令数: [bold #00f0ff]{len(raw_list)}[/] 条")
        console.print(f"  • 写入文件: [dim]{commands_path}[/]")
        console.print("[dim]已自动写入本地 commands.yaml，您现在可以在终端中直接使用或使用 'kps' 补全这些命令！[/]\n")
        return 0
    except Exception as e:
        console.print(f"[bold #f43f5e]写入本地 commands.yaml 失败: {e}[/]")
        return 1


def do_mappings(repo: HubRepository, shell_filter: str, console: Console) -> int:
    """Lists the dedicated mapping repository (pwsh-focused)."""
    maps = repo.list_mappings(shell_filter)
    if not maps:
        console.print(f"[dim]未找到针对目标终端 '{shell_filter}' 的独立映射数据。[/]")
        return 0

    table = Table(
        title=f"🎯 Kapsel 独立终端映射仓库 · 目标终端: [{shell_filter}] (共收录 {len(maps)} 条映射)",
        box=None,
        title_justify="left",
        padding=(0, 2),
    )
    table.add_column("源指令 (Linux/统一别名)", style="bold #00f0ff", width=22)
    table.add_column("目标终端", style="bold #a855f7", width=12)
    table.add_column("转义为原生指令模板 (PWSH Template)", style="#10b981", width=36)
    table.add_column("功能说明", style="#e4e4e7")

    for m in maps:
        table.add_row(
            m["source_alias"],
            m["target_shell"],
            m["target_template"],
            m["desc"],
        )

    console.print()
    console.print(table)
    console.print("\n[dim]提示: 当前已完整收录 32+ 条面向 pwsh 的 Linux-First 原生 Cmdlet 映射。[/]\n")
    return 0
