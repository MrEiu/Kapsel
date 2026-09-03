"""
KPS-Hub Standalone Server Administration CLI.
Directly manages the server-side registry.db without depending on the client library.
"""

import argparse
import json
import sys
from typing import List, Optional

from db import HubRepository
from seed import seed_database


def main(argv: Optional[List[str]] = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(
        prog="kps-hub-admin",
        description="🛠️ KPS-Hub 独立云仓库服务端管理工具 (Standalone Server Admin CLI)",
    )
    subparsers = parser.add_subparsers(dest="subcommand", help="管理模块子指令")

    # 1. Status
    subparsers.add_parser("status", help="查看服务端数据库运行指标与统计数据")

    # 2. Seed
    subparsers.add_parser("seed", help="为服务端数据库载入官方基线软件包与 pwsh 映射")

    # 3. Pkg
    pkg_p = subparsers.add_parser("pkg", help="软件包管理 (平台-软件维度)")
    pkg_sub = pkg_p.add_subparsers(dest="action")
    pkg_list = pkg_sub.add_parser("list", help="列出所有软件包")
    pkg_list.add_argument("--platform", "-p", default=None)
    pkg_add = pkg_sub.add_parser("add", help="新增软件包")
    pkg_add.add_argument("software")
    pkg_add.add_argument("--desc", "-d", required=True)
    pkg_add.add_argument("--platform", "-p", default="universal")
    pkg_add.add_argument("--name", "-n", default=None)
    pkg_add.add_argument("--version", "-v", default="1.0.0")
    pkg_add.add_argument("--category", "-c", default="general")
    pkg_del = pkg_sub.add_parser("del", help="删除软件包")
    pkg_del.add_argument("software")
    pkg_del.add_argument("--platform", "-p", default=None)

    # 4. Cmd
    cmd_p = subparsers.add_parser("cmd", help="软件子指令管理")
    cmd_sub = cmd_p.add_subparsers(dest="action")
    cmd_list = cmd_sub.add_parser("list", help="查看某软件指令")
    cmd_list.add_argument("software")
    cmd_add = cmd_sub.add_parser("add", help="添加新子指令")
    cmd_add.add_argument("software")
    cmd_add.add_argument("name")
    cmd_add.add_argument("alias")
    cmd_add.add_argument("--desc", "-d", required=True)
    cmd_add.add_argument("--usage", "-u", default="")
    cmd_add.add_argument("--example", "-e", default="")
    cmd_del = cmd_sub.add_parser("del", help="删除子指令")
    cmd_del.add_argument("software")
    cmd_del.add_argument("name")

    # 5. Map
    map_p = subparsers.add_parser("map", help="终端映射管理")
    map_sub = map_p.add_subparsers(dest="action")
    map_list = map_sub.add_parser("list", help="查看映射")
    map_list.add_argument("--shell", "-s", default="pwsh")
    map_add = map_sub.add_parser("add", help="新增映射")
    map_add.add_argument("source")
    map_add.add_argument("template")
    map_add.add_argument("--desc", "-d", required=True)
    map_add.add_argument("--shell", "-s", default="pwsh")
    map_del = map_sub.add_parser("del", help="删除映射")
    map_del.add_argument("source")
    map_del.add_argument("--shell", "-s", default="pwsh")

    # 6. Export / Import
    exp_p = subparsers.add_parser("export", help="导出 JSON 备份")
    exp_p.add_argument("--output", "-o", default=None)
    imp_p = subparsers.add_parser("import", help="导入 JSON 文件")
    imp_p.add_argument("file")

    if not argv:
        parser.print_help()
        return 0

    args = parser.parse_args(argv)
    repo = HubRepository()

    if args.subcommand == "status":
        stats = repo.get_stats()
        print(json.dumps(stats, indent=2, ensure_ascii=False))
        return 0

    if args.subcommand == "seed":
        seed_database(repo)
        print("✔ 成功初始化服务端云仓库基线数据！")
        return 0

    if args.subcommand == "pkg":
        if not args.action or args.action == "list":
            pkgs = repo.list_packages(getattr(args, "platform", None))
            for p in pkgs:
                print(f"[{p['platform']}] {p['software']} (v{p['version']}): {p['desc']}")
            return 0
        if args.action == "add":
            repo.add_package(args.platform, args.software, args.name or args.software.title(), args.desc, args.version, args.category)
            print(f"✔ 成功添加软件包: {args.software}")
            return 0
        if args.action == "del":
            repo.delete_package(args.software, getattr(args, "platform", None))
            print(f"✔ 成功删除软件包: {args.software}")
            return 0

    if args.subcommand == "cmd":
        if not args.action or args.action == "list":
            cmds = repo.get_commands_for_software(args.software)
            for c in cmds:
                print(f"  • {c['full_alias']} -> {c['desc']} (示例: {c['example']})")
            return 0
        if args.action == "add":
            repo.add_command(args.software, args.name, args.alias, args.desc, usage=args.usage, example=args.example)
            print(f"✔ 成功添加指令: {args.alias}")
            return 0
        if args.action == "del":
            repo.delete_command(args.software, args.name)
            print(f"✔ 成功删除指令: {args.name}")
            return 0

    if args.subcommand == "map":
        if not args.action or args.action == "list":
            maps = repo.list_mappings(args.shell)
            for m in maps:
                print(f"  • {m['source_alias']} -> {m['target_template']} ({m['desc']})")
            return 0
        if args.action == "add":
            repo.add_mapping(args.source, args.template, args.desc, target_shell=args.shell)
            print(f"✔ 成功添加映射: {args.source} -> {args.template}")
            return 0
        if args.action == "del":
            repo.delete_mapping(args.source, args.shell)
            print(f"✔ 成功删除映射: {args.source}")
            return 0

    if args.subcommand == "export":
        data = repo.export_all()
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"✔ 已成功导出至 {args.output}")
        else:
            print(json.dumps(data, indent=2, ensure_ascii=False))
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
