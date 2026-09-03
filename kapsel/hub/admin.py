"""
Kapsel Cloud Command Hub & Mapping Repository Administration Tool.
Independent CLI utility for managing packages, software commands, and pwsh mappings (CRUD).
Can be executed via 'kps-hub' or 'kps repo admin'.
"""

import argparse
import json
import sys
from typing import List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from kapsel.hub.db import HubRepository, get_hub_db_path
from kapsel.hub.seed import seed_hub_database
from kapsel.ui.banner import ensure_utf8_io


def main(argv: Optional[List[str]] = None) -> int:
    """CLI entry point for kps-hub / kapsel-hub admin tool."""
    ensure_utf8_io()
    console = Console(legacy_windows=False)
    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(
        prog="kps-hub",
        description="💊 Kapsel 指令云仓库管理工具 (Hub Repository CRUD Admin CLI)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="subcommand", help="管理模块子指令")

    # 1. Status
    subparsers.add_parser("status", help="查看云仓库数据库状态与统计指标")

    # 2. Seed / Reset
    subparsers.add_parser("seed", help="重新载入内置官方默认指令集与 pwsh 映射")

    # 3. Package Management (pkg)
    pkg_parser = subparsers.add_parser("pkg", help="管理软件包 (Platform -> Software 维度)")
    pkg_subs = pkg_parser.add_subparsers(dest="action")

    pkg_list_p = pkg_subs.add_parser("list", help="列出所有软件包")
    pkg_list_p.add_argument("--platform", "-p", default=None, help="按平台过滤 (windows/universal/linux)")

    pkg_add_p = pkg_subs.add_parser("add", help="新增或更新软件包")
    pkg_add_p.add_argument("software", help="软件唯一标识 (如 docker, scoop, git)")
    pkg_add_p.add_argument("--desc", "-d", required=True, help="软件简要说明")
    pkg_add_p.add_argument("--platform", "-p", default="universal", help="支持平台 (默认 universal)")
    pkg_add_p.add_argument("--name", "-n", default=None, help="软件显示全名")
    pkg_add_p.add_argument("--version", "-v", default="1.0.0", help="版本号 (默认 1.0.0)")
    pkg_add_p.add_argument("--category", "-c", default="general", help="分类标签 (如 vcs, runtime, package_manager)")
    pkg_add_p.add_argument("--author", "-a", default="Community", help="原作者/维护者")

    pkg_del_p = pkg_subs.add_parser("del", help="删除指定软件包及其所有子命令")
    pkg_del_p.add_argument("software", help="待删除的软件标识")
    pkg_del_p.add_argument("--platform", "-p", default=None, help="可选限定平台")

    # 4. Command Management (cmd)
    cmd_parser = subparsers.add_parser("cmd", help="管理具体软件的子指令集")
    cmd_subs = cmd_parser.add_subparsers(dest="action")

    cmd_list_p = cmd_subs.add_parser("list", help="列出某个软件收录的所有指令")
    cmd_list_p.add_argument("software", help="软件标识 (如 git, scoop)")

    cmd_add_p = cmd_subs.add_parser("add", help="添加新指令到软件")
    cmd_add_p.add_argument("software", help="所属软件 (如 scoop, git)")
    cmd_add_p.add_argument("name", help="子命令简称 (如 install, status)")
    cmd_add_p.add_argument("alias", help="完整指令别名 (如 scoop install, git status)")
    cmd_add_p.add_argument("--desc", "-d", required=True, help="指令功能说明")
    cmd_add_p.add_argument("--usage", "-u", default="", help="参数用法说明")
    cmd_add_p.add_argument("--example", "-e", default="", help="典型使用示例")
    cmd_add_p.add_argument("--platform", "-p", default="universal", help="所属平台")

    cmd_del_p = cmd_subs.add_parser("del", help="从软件中删除指定指令")
    cmd_del_p.add_argument("software", help="所属软件")
    cmd_del_p.add_argument("name", help="子命令简称")

    # 5. Mapping Management (map)
    map_parser = subparsers.add_parser("map", help="管理独立终端转义映射库 (优先聚焦 pwsh)")
    map_subs = map_parser.add_subparsers(dest="action")

    map_list_p = map_subs.add_parser("list", help="查看已收录的终端原生映射")
    map_list_p.add_argument("--shell", "-s", default="pwsh", help="目标 Shell (默认 pwsh)")

    map_add_p = map_subs.add_parser("add", help="新增或修改原生映射规则")
    map_add_p.add_argument("source", help="源指令别名 (如 rm -rf, cat, grep)")
    map_add_p.add_argument("template", help="原生命令模板 (如 Remove-Item -Recurse -Force {{args}})")
    map_add_p.add_argument("--desc", "-d", required=True, help="映射功能说明")
    map_add_p.add_argument("--shell", "-s", default="pwsh", help="目标 Shell (默认 pwsh)")

    map_del_p = map_subs.add_parser("del", help="删除指定映射规则")
    map_del_p.add_argument("source", help="源指令别名")
    map_del_p.add_argument("--shell", "-s", default="pwsh", help="目标 Shell")

    # 6. Export / Import
    exp_p = subparsers.add_parser("export", help="导出整个云仓库为 JSON 文件")
    exp_p.add_argument("--output", "-o", default=None, help="导出目标文件路径")

    imp_p = subparsers.add_parser("import", help="从 JSON 文件批量导入数据")
    imp_p.add_argument("file", help="待导入的 JSON 文件路径")

    # If no args, show dashboard and help
    if not argv:
        render_dashboard(console)
        parser.print_help()
        return 0

    args = parser.parse_args(argv)
    repo = HubRepository()

    # Route subcommands
    if args.subcommand == "status":
        return show_status(repo, console)

    if args.subcommand == "seed":
        seed_hub_database(repo)
        console.print("[bold #10b981]✔ 成功重置并初始化云仓库默认数据！[/]")
        return show_status(repo, console)

    if args.subcommand == "pkg":
        return handle_pkg_action(repo, args, console)

    if args.subcommand == "cmd":
        return handle_cmd_action(repo, args, console)

    if args.subcommand == "map":
        return handle_map_action(repo, args, console)

    if args.subcommand == "export":
        return handle_export(repo, args.output, console)

    if args.subcommand == "import":
        return handle_import(repo, args.file, console)

    parser.print_help()
    return 0


def render_dashboard(console: Console) -> None:
    """Renders the top banner of the hub admin tool."""
    repo = HubRepository()
    stats = repo.get_stats()

    grid = Table.grid(expand=True, padding=(0, 2))
    grid.add_column(style="bold #00f0ff", justify="right", width=18)
    grid.add_column(style="#e4e4e7")
    grid.add_column(style="bold #a855f7", justify="right", width=18)
    grid.add_column(style="#e4e4e7")

    grid.add_row(
        "🗄️ 仓库物理路径:",
        f"[dim]{stats['db_path']}[/]",
        "📦 收录软件包数:",
        f"[bold #10b981]{stats['packages_count']} 个[/]",
    )
    grid.add_row(
        "⚡ 总指令收录数:",
        f"[bold #00f0ff]{stats['commands_count']} 条指令[/]",
        "🎯 PWSH 映射条数:",
        f"[bold #a855f7]{stats['mappings_count']} 条原生转义[/]",
    )

    panel = Panel(
        grid,
        title="🛠️ KAPSEL 指令云仓库独立管理工具 (Hub Admin)",
        border_style="#0891b2",
        padding=(1, 2),
    )
    console.print()
    console.print(panel)
    console.print()


def show_status(repo: HubRepository, console: Console) -> int:
    render_dashboard(console)
    return 0


def handle_pkg_action(repo: HubRepository, args: argparse.Namespace, console: Console) -> int:
    if not args.action or args.action == "list":
        pkgs = repo.list_packages(getattr(args, "platform", None))
        table = Table(title=f"📦 软件包清单 ({len(pkgs)} 个)", box=None, padding=(0, 2))
        table.add_column("平台", style="bold #a855f7", width=12)
        table.add_column("软件标识", style="bold #00f0ff", width=14)
        table.add_column("版本", style="dim", width=8)
        table.add_column("分类", style="italic #38bdf8", width=16)
        table.add_column("描述", style="#e4e4e7")
        for p in pkgs:
            table.add_row(p["platform"], p["software"], p["version"], p["category"], p["desc"])
        console.print(table)
        return 0

    if args.action == "add":
        repo.add_package(
            platform=args.platform,
            software=args.software,
            display_name=args.name or args.software.title(),
            desc=args.desc,
            version=args.version,
            category=args.category,
            author=args.author,
        )
        console.print(f"[bold #10b981]✔ 成功添加/更新软件包:[/] [bold #00f0ff]{args.software}[/] (平台: {args.platform})")
        return 0

    if args.action == "del":
        success = repo.delete_package(args.software, getattr(args, "platform", None))
        if success:
            console.print(f"[bold #10b981]✔ 成功删除软件包:[/] [bold #f43f5e]{args.software}[/]")
        else:
            console.print(f"[bold #f43f5e]✘ 未找到待删除的软件包:[/] {args.software}")
        return 0
    return 0


def handle_cmd_action(repo: HubRepository, args: argparse.Namespace, console: Console) -> int:
    if not args.action or args.action == "list":
        cmds = repo.get_commands_for_software(args.software)
        if not cmds:
            console.print(f"[dim]软件 '{args.software}' 暂无收录指令。[/]")
            return 0
        table = Table(title=f"⚡ 软件 '{args.software}' 指令列表 ({len(cmds)} 条)", box=None, padding=(0, 2))
        table.add_column("子命令", style="bold #00f0ff", width=14)
        table.add_column("完整别名", style="bold #38bdf8", width=22)
        table.add_column("功能说明", style="#e4e4e7")
        table.add_column("用例", style="dim italic")
        for c in cmds:
            table.add_row(c["command_name"], c["full_alias"], c["desc"], c["example"])
        console.print(table)
        return 0

    if args.action == "add":
        repo.add_command(
            software=args.software,
            command_name=args.name,
            full_alias=args.alias,
            desc=args.desc,
            platform=args.platform,
            usage=args.usage,
            example=args.example,
        )
        console.print(f"[bold #10b981]✔ 成功添加指令:[/] [bold #00f0ff]{args.alias}[/] ➔ 软件 '{args.software}'")
        return 0

    if args.action == "del":
        success = repo.delete_command(args.software, args.name)
        if success:
            console.print(f"[bold #10b981]✔ 成功删除指令:[/] {args.name} (软件: {args.software})")
        else:
            console.print(f"[bold #f43f5e]✘ 未找到待删除的指令:[/] {args.name}")
        return 0
    return 0


def handle_map_action(repo: HubRepository, args: argparse.Namespace, console: Console) -> int:
    if not args.action or args.action == "list":
        maps = repo.list_mappings(args.shell)
        table = Table(title=f"🎯 [{args.shell}] 原生映射库 ({len(maps)} 条)", box=None, padding=(0, 2))
        table.add_column("源指令别名", style="bold #00f0ff", width=18)
        table.add_column("目标终端", style="bold #a855f7", width=10)
        table.add_column("转义模板", style="#10b981", width=36)
        table.add_column("说明", style="#e4e4e7")
        for m in maps:
            table.add_row(m["source_alias"], m["target_shell"], m["target_template"], m["desc"])
        console.print(table)
        return 0

    if args.action == "add":
        repo.add_mapping(
            source_alias=args.source,
            target_template=args.template,
            desc=args.desc,
            target_shell=args.shell,
        )
        console.print(f"[bold #10b981]✔ 成功保存映射:[/] [bold #00f0ff]{args.source}[/] ➔ [bold #10b981]{args.template}[/] ([{args.shell}])")
        return 0

    if args.action == "del":
        success = repo.delete_mapping(args.source, args.shell)
        if success:
            console.print(f"[bold #10b981]✔ 成功删除映射:[/] {args.source} ([{args.shell}])")
        else:
            console.print(f"[bold #f43f5e]✘ 未找到映射:[/] {args.source}")
        return 0
    return 0


def handle_export(repo: HubRepository, output_path: Optional[str], console: Console) -> int:
    data = repo.export_all()
    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        console.print(f"[bold #10b981]✔ 云仓库数据已成功导出至:[/] [bold #00f0ff]{output_path}[/]")
    else:
        print(json.dumps(data, indent=2, ensure_ascii=False))
    return 0


def handle_import(repo: HubRepository, file_path: str, console: Console) -> int:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        counts = repo.import_all(data)
        console.print(f"[bold #10b981]🎉 导入完成！[/]")
        console.print(f"  • 软件包: {counts['packages']} 个")
        console.print(f"  • 指令数: {counts['commands']} 条")
        console.print(f"  • 映射数: {counts['mappings']} 条")
        return 0
    except Exception as e:
        console.print(f"[bold #f43f5e]导入失败: {e}[/]")
        return 1


if __name__ == "__main__":
    sys.exit(main())
