"""
Kapsel Dual-State Completer (Fig.Spec Powered).
Seamlessly fuses with Fig AST completion with Kapsel's core command subsystem and plugin hooks.
"""

from typing import Any, Dict, Iterable, List, Optional, Tuple

from prompt_toolkit.completion import CompleteEvent, Completer, Completion, PathCompleter
from prompt_toolkit.document import Document

from kapsel.completion.fig_engine import FigCandidate, FigEngine, get_fig_engine
from kapsel.completion.kps.registry import KpsCommandRegistry, get_kps_registry


class DualStateCompleter(Completer):
    """
    Dual-State Fig-Powered Completer:
    - Native Mode: Deep multi-level Fig subcommands (e.g. 'docker compose up'),
                   flag/option perception ('git commit -m'), builtins, and paths.
    - Kapsel Mode ('kps '): Dynamic kps commands (built-ins & plugin registered),
                            subcommand hints, plus plugin-provided candidates.
    """

    def __init__(
        self,
        fig_engine: Optional[FigEngine] = None,
        kps_registry: Optional[KpsCommandRegistry] = None,
        current_shell: str = "pwsh",
        plugin_manager: Optional[Any] = None,
    ):
        self.fig_engine = fig_engine or get_fig_engine()
        self.kps_registry = kps_registry or get_kps_registry()
        self.current_shell = current_shell
        self.plugin_manager = plugin_manager
        self.path_completer = PathCompleter(expanduser=True)

    def set_shell(self, shell: str) -> None:
        self.current_shell = shell

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
            yield from self._complete_kapsel_mode(sub, document, complete_event)
            return

        # 3. Native Mode: Fig.Spec multi-level subcommands, flags, builtins & paths
        yield from self._complete_native_mode(stripped, document, complete_event)

    def _complete_kapsel_mode(
        self, query: str, document: Document, complete_event: CompleteEvent
    ) -> Iterable[Completion]:
        words = query.split()
        first_word = words[0] if words else ""

        # A. If typing the primary kps command name (e.g. 'kps st' -> 'kps status')
        if len(words) <= 1 and not query.endswith(" "):
            for cmd in self.kps_registry.list_commands():
                if cmd.name.startswith(first_word.lower()):
                    icon = "🔌 " if cmd.plugin_id else "⚙️ "
                    yield Completion(
                        text=cmd.name,
                        start_position=-len(first_word),
                        display=cmd.name,
                        display_meta=f"{icon}{cmd.help_text}",
                    )

        # B. If command is typed and user is typing subarguments (e.g. 'kps config ed')
        elif len(words) >= 1:
            cmd = self.kps_registry.get(first_word.lower())
            if cmd and cmd.subcommands:
                sub_query = words[1] if len(words) > 1 and not query.endswith(" ") else ""
                if len(words) == 1 and query.endswith(" "):
                    sub_query = ""
                for subcmd, subdesc in cmd.subcommands.items():
                    if subcmd.startswith(sub_query.lower()):
                        yield Completion(
                            text=subcmd,
                            start_position=-len(sub_query),
                            display=subcmd,
                            display_meta=f"🔹 {subdesc}",
                        )

        # C. Plugin-provided completions for kps mode
        if self.plugin_manager:
            plugin_cands = self.plugin_manager.get_plugin_completions("kps " + query)
            for cand in plugin_cands:
                yield Completion(
                    text=cand.get("text", ""),
                    start_position=cand.get("start_position", -len(query)),
                    display=cand.get("display", cand.get("text", "")),
                    display_meta=cand.get("display_meta", "🔌 插件提供"),
                )

        # D. If user is entering a tool under kps (e.g. 'kps git commit'), also offer Fig completions
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
                ("datadir", "查看或自定义迁移数据存储位置"),
                ("clear", "清除终端屏幕"),
                ("exit", "退出胶囊会话"),
                ("git", "Git 分布式版本控制 (Fig感知就绪)"),
                ("docker", "Docker 容器生命周期管理 (Fig感知就绪)"),
                ("scoop", "Windows 命令行包管理器 (Fig感知就绪)"),
                ("npm", "Node.js 包管理器 (Fig感知就绪)"),
                ("python", "Python 解释器 (Fig感知就绪)"),
                ("cargo", "Rust 包与编译管理 (Fig感知就绪)"),
            ]
            for cmd, desc in native_builtins:
                if cmd.startswith(curr_word.lower()):
                    yield Completion(
                        text=cmd,
                        start_position=-len(curr_word),
                        display=cmd,
                        display_meta=desc,
                    )

        # C. Plugin-provided completions for native mode
        if self.plugin_manager:
            plugin_cands = self.plugin_manager.get_plugin_completions(stripped)
            for cand in plugin_cands:
                yield Completion(
                    text=cand.get("text", ""),
                    start_position=cand.get("start_position", -len(parts[-1]) if parts else 0),
                    display=cand.get("display", cand.get("text", "")),
                    display_meta=cand.get("display_meta", "🔌 插件提供"),
                )

        # D. Filesystem Path Completion fallback
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
