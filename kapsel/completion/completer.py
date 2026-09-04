"""
Kapsel Dual-State Completer (Carapace-Powered).
Seamlessly fuses Carapace dynamic multi-shell completion (1,000+ commands)
with Kapsel's core system management and plugin ecosystem.
All comments and descriptions are in English.
"""

from typing import Any, Dict, Iterable, List, Optional, Tuple

from prompt_toolkit.completion import CompleteEvent, Completer, Completion, PathCompleter
from prompt_toolkit.document import Document

from kapsel.completion.carapace_engine import CarapaceEngine, get_carapace_engine
from kapsel.completion.fig_engine import FigEngine, get_fig_engine
from kapsel.completion.kps.registry import KpsCommandRegistry, get_kps_registry


class DualStateCompleter(Completer):
    """
    Dual-State Carapace-Powered Completer:
    - Native Mode: Deep multi-level context-aware autocompletion powered by Carapace
                   (1,000+ tools: git branches/tags, docker flags/containers, npm scripts, etc.).
    - System Mode ('kapsel <cmd>'): System management commands (help, status, config, datadir, add, toggle).
    - Feature Mode ('kps <cmd>'): Functional plugin commands (ai, alias, fuck, help, install, profile, rec, etc.).
    """

    def __init__(
        self,
        carapace_engine: Optional[CarapaceEngine] = None,
        fig_engine: Optional[FigEngine] = None,
        kps_registry: Optional[KpsCommandRegistry] = None,
        current_shell: str = "pwsh",
        plugin_manager: Optional[Any] = None,
    ):
        self.carapace_engine = carapace_engine or get_carapace_engine()
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
                display_meta="⚙️ 胶囊系统管理 (help, status, config, datadir, add, toggle)",
            )
            yield Completion(
                text="kps ",
                start_position=-len(stripped),
                display="kps ",
                display_meta="🚀 胶囊功能扩展 (ai, alias, fuck, help, install, profile, rec)",
            )
            return
        if stripped in ("kp", "kps"):
            yield Completion(
                text="kps ",
                start_position=-len(stripped),
                display="kps ",
                display_meta="🚀 胶囊功能扩展 (ai, alias, fuck, help, install, profile, rec)",
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

        # 4. Native Mode: Carapace (1000+ tools), Fig fallback, builtins, & paths
        yield from self._complete_native_mode(stripped, document, complete_event)

    def _complete_scoped_mode(
        self, query: str, scope: str
    ) -> Iterable[Completion]:
        """Completes commands under 'kapsel ' (system) or 'kps ' (feature) scope."""
        ends_with_space = query.endswith(" ")
        words = query.split()

        if ends_with_space:
            prefix = ""
        else:
            prefix = words[-1] if words else ""

        # Filter commands matching the requested scope ('system' or 'feature')
        if scope == "system":
            available_cmds = self.kps_registry.list_system_commands()
        else:
            available_cmds = self.kps_registry.list_feature_commands()

        # A. Completing the primary command name (e.g. 'kapsel conf' or 'kps rec')
        if len(words) == 0 or (len(words) == 1 and not ends_with_space):
            for cmd in available_cmds:
                if cmd.name.startswith(prefix.lower()):
                    icon = "⚙️ " if scope == "system" else "🚀 "
                    yield Completion(
                        text=cmd.name,
                        start_position=-len(prefix),
                        display=cmd.name,
                        display_meta=f"{icon}{cmd.help_text}",
                    )

        # B. Completing subcommands (e.g. 'kapsel config [edit|path|get|set]')
        elif len(words) >= 1:
            first_cmd_name = words[0].lower()
            cmd = self.kps_registry.get(first_cmd_name, scope=scope)
            if cmd and cmd.subcommands:
                if len(words) == 1 and ends_with_space:
                    sub_prefix = ""
                elif len(words) == 2 and not ends_with_space:
                    sub_prefix = words[1]
                else:
                    sub_prefix = ""

                for subcmd, subdesc in cmd.subcommands.items():
                    if subcmd.startswith(sub_prefix.lower()):
                        yield Completion(
                            text=subcmd,
                            start_position=-len(sub_prefix),
                            display=subcmd,
                            display_meta=f"🔹 {subdesc}",
                        )

        # C. Plugin-provided dynamic completions (for feature scope, e.g. tldr cheat sheet caching)
        if scope == "feature" and self.plugin_manager:
            plugin_cands = self.plugin_manager.get_plugin_completions("kps " + query)
            for cand in plugin_cands:
                yield Completion(
                    text=cand.get("text", ""),
                    start_position=cand.get("start_position", -len(prefix)),
                    display=cand.get("display", cand.get("text", "")),
                    display_meta=cand.get("display_meta", "🔌 插件提供"),
                )

        # D. If user ran a native tool prefixed with kps (e.g. 'kps git checkout')
        if scope == "feature" and words:
            first_tool = words[0].lower()
            if self.carapace_engine.is_available() and self.carapace_engine.has_completer_for(first_tool):
                yield from self._yield_carapace_completions(query)

    def _complete_native_mode(
        self, stripped: str, document: Document, complete_event: CompleteEvent
    ) -> Iterable[Completion]:
        parts = stripped.split()
        first_tool = parts[0].lower() if parts else ""
        if first_tool.endswith(".exe"):
            first_tool = first_tool[:-4]

        # A. Primary: Carapace Dynamic Completion (1,000+ commands with live context)
        if parts and self.carapace_engine.is_available() and self.carapace_engine.has_completer_for(first_tool):
            yield from self._yield_carapace_completions(stripped)
            return

        # B. Secondary: Fig.Spec fallback if tool was defined in Fig
        if parts and self.fig_engine.has_spec_for_tool(first_tool):
            yield from self._yield_fig_completions(stripped)
            return

        # C. Native Top-Level Builtins & High-Frequency Tools (when starting command line)
        if len(parts) <= 1 and not stripped.endswith(" "):
            curr_word = parts[0] if parts else ""
            native_builtins = [
                ("cd", "切换工作目录 (支持 cd ~, cd -)"),
                ("clear", "清除终端屏幕"),
                ("exit", "退出胶囊会话"),
                ("git", "Git 分布式版本控制 (Carapace 动态感知就绪)"),
                ("docker", "Docker 容器生命周期管理 (Carapace 动态感知就绪)"),
                ("scoop", "Windows 命令行包管理器 (Carapace 动态感知就绪)"),
                ("npm", "Node.js 包管理器 (Carapace 动态感知就绪)"),
                ("cargo", "Rust 包与编译管理 (Carapace 动态感知就绪)"),
                ("python", "Python 解释器 (Carapace 动态感知就绪)"),
                ("kubectl", "Kubernetes 集群控制 CLI (Carapace 就绪)"),
                ("pnpm", "快速高效的磁盘节约型包管理器"),
                ("yarn", "Node 依赖管理工具"),
            ]
            for cmd, desc in native_builtins:
                if cmd.startswith(curr_word.lower()):
                    yield Completion(
                        text=cmd,
                        start_position=-len(curr_word),
                        display=cmd,
                        display_meta=desc,
                    )

        # D. Plugin-provided completions for native mode (e.g. mapping plugins)
        if self.plugin_manager:
            plugin_cands = self.plugin_manager.get_plugin_completions(stripped)
            for cand in plugin_cands:
                yield Completion(
                    text=cand.get("text", ""),
                    start_position=cand.get("start_position", -len(parts[-1]) if parts else 0),
                    display=cand.get("display", cand.get("text", "")),
                    display_meta=cand.get("display_meta", "🔌 插件提供"),
                )

        # E. Filesystem Path Completion fallback
        yield from self.path_completer.get_completions(document, complete_event)

    def _yield_carapace_completions(self, text_line: str) -> Iterable[Completion]:
        """Queries CarapaceEngine and yields structured, styled prompt_toolkit completions."""
        candidates, prefix = self.carapace_engine.get_completions(text_line)
        start_pos = -len(prefix)

        for cand in candidates:
            # Determine suitable icon based on argument type
            if cand.value.startswith("-"):
                icon = "🚩 "
            elif "/" in cand.value or "\\" in cand.value:
                icon = "📁 "
            elif cand.tag in ("heads", "local branches", "remote branches", "tags"):
                icon = "🌿 "
            elif cand.tag in ("containers", "images", "volumes", "networks"):
                icon = "🐳 "
            else:
                icon = "📦 "

            tag_part = f"[{cand.tag}] " if cand.tag else ""
            desc = f"{icon}{tag_part}{cand.description}".strip() if cand.description or cand.tag else f"{icon}{cand.value}"

            yield Completion(
                text=cand.value,
                start_position=start_pos,
                display=cand.display or cand.value,
                display_meta=desc,
            )

    def _yield_fig_completions(self, text_line: str) -> Iterable[Completion]:
        """Evaluates legacy Fig AST context and yields styled completions."""
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
