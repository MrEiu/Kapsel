"""
Kapsel Dual-State Completer (Fig.Spec Powered).
Seamlessly fuses withfig/autocomplete AST perception with Kapsel's core Linux mapping engine.
"""

from typing import Dict, Iterable, List, Optional, Tuple

from prompt_toolkit.completion import CompleteEvent, Completer, Completion, PathCompleter
from prompt_toolkit.document import Document

from kapsel.core.completion.fig_engine import FigCandidate, FigEngine, get_fig_engine
from kapsel.storage.registry.indexer import CommandEntry, RegistryIndexer, get_registry_indexer
from kapsel.storage.user_db import get_user_db


class DualStateCompleter(Completer):
    """
    Dual-State Fig-Powered Completer:
    - Native Mode: Deep multi-level Fig subcommands (e.g. 'docker compose up'),
                   flag/option perception ('git commit -m'), builtins, and paths.
    - Kapsel Mode ('kps '): Linux-First mappings with live native Shell code preview
                            ('rm -rf' ➔ 'Remove-Item -Recurse -Force').
    """

    def __init__(
        self,
        indexer: Optional[RegistryIndexer] = None,
        fig_engine: Optional[FigEngine] = None,
        current_shell: str = "pwsh",
    ):
        self.indexer = indexer or get_registry_indexer(current_shell)
        self.fig_engine = fig_engine or get_fig_engine()
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
                display_meta="💊 进入跨平台智能胶囊模式 (Linux肌肉记忆转义)",
            )
            return

        # 2. Kapsel Mode: Active when line starts with 'kps '
        if stripped.startswith("kps "):
            sub = stripped[4:]
            yield from self._complete_kapsel_mode(sub, document, complete_event)
            return

        # 3. Native Mode: Fig.Spec multi-level subcommands, flags, builtins & paths
        yield from self._complete_native_mode(stripped, document, complete_event)

    def _complete_kapsel_mode(
        self, query: str, document: Document, complete_event: CompleteEvent
    ) -> Iterable[Completion]:
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

        if len(words) <= 1 and not query.endswith(" "):
            # Complete builtins
            for subcmd, desc in builtin_kps_cmds:
                if subcmd.startswith(first_word.lower()):
                    yield Completion(
                        text=subcmd,
                        start_position=-len(first_word),
                        display=subcmd,
                        display_meta=f"⚙️ {desc}",
                    )

        # Linux-First command alias mappings with live native Shell translation preview
        command_entries = self.indexer.list_all_commands()
        for entry in command_entries:
            if query == "" or entry.alias.startswith(query):
                template = entry.get_template_for_shell(self.current_shell) or ""
                preview = template.replace("{{args}}", "").strip()
                if len(preview) > 35:
                    preview = preview[:32] + "…"

                # Preview shows translated command live!
                meta = f"➔ {preview} | {entry.desc}" if preview else entry.desc
                yield Completion(
                    text=entry.alias,
                    start_position=-len(query),
                    display=entry.alias,
                    display_meta=meta,
                )

        # If user is entering a tool under kps (e.g. 'kps git commit'), also offer Fig completions!
        if words and self.fig_engine.has_spec_for_tool(first_word):
            yield from self._yield_fig_completions(query)

    def _complete_native_mode(
        self, stripped: str, document: Document, complete_event: CompleteEvent
    ) -> Iterable[Completion]:
        parts = stripped.split()

        # A. Fig.Spec Context Completion (git, docker, scoop, npm, python, cargo, etc.)
        if parts:
            first_tool = parts[0].lower()
            if self.fig_engine.has_spec_for_tool(first_tool):
                yield from self._yield_fig_completions(stripped)
                return

        # B. Native Top-Level Builtins & High-Frequency Tools
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
                ("git", "Git 分布式版本控制 (Fig感知就绪)"),
                ("docker", "Docker 容器生命周期管理 (Fig感知就绪)"),
                ("scoop", "Windows 命令行包管理器 (Fig感知就绪)"),
                ("npm", "Node.js 包管理器 (Fig感知就绪)"),
                ("python", "Python 解释器 (Fig感知就绪)"),
                ("cargo", "Rust 包与编译管理 (Fig感知就绪)"),
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

    def _yield_fig_completions(self, text_line: str) -> Iterable[Completion]:
        """Evaluates Fig AST context and yields styled completions."""
        completed, partial = self.fig_engine.tokenize_line(text_line)
        candidates = self.fig_engine.get_completions(text_line)

        start_pos = -len(partial) if partial else 0

        for cand in candidates:
            icon = "🚩 " if cand.kind == "option" else "📦 "
            yield Completion(
                text=cand.insert_text,
                start_position=start_pos,
                display=cand.display_text,
                display_meta=f"{icon}{cand.description}",
            )
