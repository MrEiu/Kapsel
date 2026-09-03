"""
Kapsel Dual-State Completer (Core Engine).
Seamlessly transitions between Native path completion, dynamic tool subcommands,
and Kapsel rich Linux-First mapping perceptions.
"""

from typing import Dict, Iterable, List, Optional, Tuple

from prompt_toolkit.completion import CompleteEvent, Completer, Completion, PathCompleter
from prompt_toolkit.document import Document

from kapsel.core.completion.dynamic_subcmds import get_subcommands_for_tool
from kapsel.storage.registry.indexer import CommandEntry, RegistryIndexer, get_registry_indexer
from kapsel.storage.user_db import get_user_db


class DualStateCompleter(Completer):
    """
    Dual-State Completer:
    - Native Mode: Builtins, CLI subcommands (git/npm/docker/scoop), and filesystem paths.
    - Kapsel Mode ('kps '): Rich perception menu with Chinese description and native preview.
    """

    def __init__(
        self,
        indexer: Optional[RegistryIndexer] = None,
        current_shell: str = "pwsh",
    ):
        self.indexer = indexer or get_registry_indexer(current_shell)
        self.current_shell = current_shell
        self.path_completer = PathCompleter(expanduser=True)

    def set_shell(self, shell: str) -> None:
        self.current_shell = shell
        self.indexer.target_shell = shell

    def get_completions(
        self, document: Document, complete_event: CompleteEvent
    ) -> Iterable[Completion]:
        text_before = document.text_before_cursor
        stripped = text_before.lstrip()

        # 1. User is typing 'kps' (offer transition to Kapsel Mode)
        if stripped in ("k", "kp", "kps"):
            yield Completion(
                text="kps ",
                start_position=-len(stripped),
                display="kps ",
                display_meta="💊 进入跨平台智能胶囊模式",
            )
            return

        # 2. Kapsel Mode: Active when line starts with 'kps '
        if stripped.startswith("kps "):
            sub = stripped[4:]
            yield from self._complete_kapsel_mode(sub)
            return

        # 3. Native Mode: Complete subcommands, builtins, and file paths
        yield from self._complete_native_mode(stripped, document, complete_event)

    def _complete_kapsel_mode(self, query: str) -> Iterable[Completion]:
        words = query.split()
        first_word = words[0] if words else ""

        # Rich built-in subcommands under 'kps <subcmd>'
        builtin_kps_cmds = [
            ("help", "查阅 Kapsel 终端胶囊使用手册与双态体系"),
            ("status", "查看操作系统环境、宿主 Shell 与沙箱配置"),
            ("config", "查看或交互式修改全局配置 config.yaml"),
            ("repo", "浏览、搜索与拉取云仓库工具指令集"),
            ("register", "注册胶囊漫游账号并生成设备指纹"),
            ("whoami", "查看当前登录的漫游身份凭据"),
            ("logout", "退出当前登录的漫游账号"),
        ]

        if len(words) <= 1:
            # Complete subcommands
            for subcmd, desc in builtin_kps_cmds:
                if subcmd.startswith(first_word.lower()):
                    yield Completion(
                        text=subcmd,
                        start_position=-len(first_word),
                        display=subcmd,
                        display_meta=f"⚙️ {desc}",
                    )

        # Linux-First command alias mappings from folder-based registry
        command_entries = self.indexer.list_all_commands()
        for entry in command_entries:
            if query == "" or entry.alias.startswith(query):
                template = entry.get_template_for_shell(self.current_shell) or ""
                preview = template.replace("{{args}}", "").strip()
                if len(preview) > 35:
                    preview = preview[:32] + "…"

                meta = f"➔ {preview} | {entry.desc}" if preview else entry.desc
                yield Completion(
                    text=entry.alias,
                    start_position=-len(query),
                    display=entry.alias,
                    display_meta=meta,
                )

    def _complete_native_mode(
        self, stripped: str, document: Document, complete_event: CompleteEvent
    ) -> Iterable[Completion]:
        parts = stripped.split()

        # A. Tool Subcommands (git, scoop, npm, docker, etc.)
        if len(parts) >= 1:
            tool = parts[0].lower()
            subcmds = get_subcommands_for_tool(tool)
            if subcmds:
                if len(parts) == 1 and not stripped.endswith(" "):
                    pass
                else:
                    curr_arg = parts[-1] if not stripped.endswith(" ") else ""
                    for cmd_name, desc in subcmds:
                        if cmd_name.startswith(curr_arg.lower()):
                            yield Completion(
                                text=cmd_name,
                                start_position=-len(curr_arg),
                                display=cmd_name,
                                display_meta=f"📦 {desc}",
                            )
                    return

        # B. Native Top-Level Builtins & High-Frequency History
        if len(parts) <= 1 and not stripped.endswith(" "):
            curr_word = parts[0] if parts else ""
            native_builtins = [
                ("cd", "切换工作目录 (支持 cd ~, cd -)"),
                ("help", "查看帮助手册"),
                ("status", "查看终端环境与沙箱运行状态"),
                ("config", "查看与修改全局配置文件"),
                ("repo", "指令云仓库管理 (list/search/pull)"),
                ("clear", "清除终端屏幕"),
                ("exit", "退出胶囊会话"),
                ("git", "Git 分布式版本控制"),
                ("scoop", "Windows 命令行包管理器"),
                ("npm", "Node.js 包管理器"),
                ("docker", "容器引擎与生命周期管理"),
                ("python", "Python 交互解释器与脚本运行"),
            ]
            weights = get_user_db().get_command_weights()
            sorted_builtins = sorted(
                native_builtins,
                key=lambda x: weights.get(x[0], 0),
                reverse=True,
            )
            for cmd, desc in sorted_builtins:
                if cmd.startswith(curr_word.lower()):
                    yield Completion(
                        text=cmd,
                        start_position=-len(curr_word),
                        display=cmd,
                        display_meta=desc,
                    )

        # C. Filesystem Path Completion fallback
        yield from self.path_completer.get_completions(document, complete_event)
