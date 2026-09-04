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

        # 1. User is typing 'kapsel' or 'kps' (offer transition)
        if stripped in ("k", "ka", "kap", "kaps", "kapse", "kapsel"):
            yield Completion(
                text="kapsel ",
                start_position=-len(stripped),
                display="kapsel ",
                display_meta="⚙️ 胶囊系统管理 (help, status, config, datadir)",
            )
            yield Completion(
                text="kps ",
                start_position=-len(stripped),
                display="kps ",
                display_meta="🚀 胶囊功能扩展 (install, add, update, search, sync)",
            )
            return
        if stripped in ("kp", "kps"):
            yield Completion(
                text="kps ",
                start_position=-len(stripped),
                display="kps ",
                display_meta="🚀 胶囊功能扩展 (install, add, update, search, sync)",
            )
            return

        # 2. System Management Mode: 'kapsel <cmd>'
        if stripped.startswith("kapsel "):
            sub = stripped[7:]
            yield from self._complete_scoped_mode(sub, scope="system")
            return

        # 3. Feature/Plugin Mode: 'kps <cmd>'
        if stripped.startswith("kps "):
            sub = stripped[4:]
            yield from self._complete_scoped_mode(sub, scope="feature")
            return

        # 4. Native Mode: Fig.Spec multi-level subcommands, flags, builtins & paths
        yield from self._complete_native_mode(stripped, document, complete_event)

    def _complete_scoped_mode(
        self, query: str, scope: str
    ) -> Iterable[Completion]:
        words = query.split()
        first_word = words[0] if words else ""

        # Filter commands matching the requested scope ('system' or 'feature')
        if scope == "system":
            available_cmds = self.kps_registry.list_system_commands()
        else:
            available_cmds = self.kps_registry.list_feature_commands()

        # A. Completing the primary command name
        if len(words) <= 1 and not query.endswith(" "):
            for cmd in available_cmds:
                if cmd.name.startswith(first_word.lower()):
                    icon = "⚙️ " if scope == "system" else "🚀 "
                    yield Completion(
                        text=cmd.name,
                        start_position=-len(first_word),
                        display=cmd.name,
                        display_meta=f"{icon}{cmd.help_text}",
                    )

        # B. Completing subarguments
        elif len(words) >= 1:
            cmd = self.kps_registry.get(first_word.lower(), scope=scope)
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

        # C. Plugin-provided completions (for feature scope)
        if scope == "feature" and self.plugin_manager:
            plugin_cands = self.plugin_manager.get_plugin_completions("kps " + query)
            for cand in plugin_cands:
                yield Completion(
                    text=cand.get("text", ""),
                    start_position=cand.get("start_position", -len(query)),
                    display=cand.get("display", cand.get("text", "")),
                    display_meta=cand.get("display_meta", "🔌 插件提供"),
                )

        # D. Fig completions for tools entered under kps
        if scope == "feature" and words and self.fig_engine.has_spec_for_tool(first_word):
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
