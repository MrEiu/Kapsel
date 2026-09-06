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
from kapsel.completion.kps.registry import KpsCommandRegistry, get_kps_registry
from kapsel.core.i18n import _


class DualStateCompleter(Completer):
    """
    Dual-State Carapace-Powered Completer:
    - Native Mode: Deep multi-level context-aware autocompletion powered by Carapace
                   (1,000+ tools: git branches/tags, docker flags/containers, npm scripts, etc.).
    - Kapsel Mode ('kapsel <cmd>' / 'kps <cmd>'): Unified capsule commands (help, status, config,
                   datadir, add, toggle, and plugin extensions).
    """

    def __init__(
        self,
        carapace_engine: Optional[CarapaceEngine] = None,
        kps_registry: Optional[KpsCommandRegistry] = None,
        current_shell: str = "pwsh",
        plugin_manager: Optional[Any] = None,
    ):
        self.carapace_engine = carapace_engine or get_carapace_engine()
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

        # Multi-line awareness: extract active line where cursor is situated
        curr_line = document.current_line_before_cursor
        stripped_line = curr_line.lstrip()

        # 1. User is typing 'kapsel', 'kps', or 'kp' (offer transition without trailing space)
        if stripped in ("k", "ka", "kap", "kaps", "kapse", "kapsel"):
            yield Completion(
                text="kapsel",
                start_position=-len(stripped),
                display="kapsel",
                display_meta="Kapsel command (help, status, config, add, ...)",
            )
            yield Completion(
                text="kps",
                start_position=-len(stripped),
                display="kps",
                display_meta="Kapsel command alias (kps)",
            )
            yield Completion(
                text="kp",
                start_position=-len(stripped),
                display="kp",
                display_meta="⚡ Kapsel block & parallel runner (kp [-c])",
            )
            return
        if stripped in ("kp", "kps"):
            yield Completion(
                text="kp",
                start_position=-len(stripped),
                display="kp",
                display_meta="⚡ Kapsel block & parallel runner (kp [-c])",
            )
            yield Completion(
                text="kps",
                start_position=-len(stripped),
                display="kps",
                display_meta="Kapsel command alias (kps)",
            )
            return

        # 2. Block execution mode ('kp [-c] <commands...>')
        if stripped_line.startswith("kp ") or stripped_line.startswith("kp\t"):
            sub = stripped_line[3:]
            yield from self._complete_kp_mode(sub, document, complete_event)
            return

        # Multi-line subsequent lines in a block starting with kp:
        if "\n" in text_before and stripped.startswith("kp"):
            sub_doc = Document(text=stripped_line, cursor_position=len(stripped_line))
            yield from self._complete_native_mode(stripped_line, sub_doc, complete_event)
            return

        # 3. Command Modes: 'kapsel <cmd>' (System) or 'kps <cmd>' (Tools)
        if stripped.startswith("kapsel "):
            sub = stripped[7:]
            yield from self._complete_kapsel_mode(sub, mode="kapsel")
            return

        if stripped.startswith("kps "):
            sub = stripped[4:]
            yield from self._complete_kapsel_mode(sub, mode="kps")
            return

        # 4. Native Mode: Carapace (1000+ tools), Fig fallback, builtins, & paths
        yield from self._complete_native_mode(stripped, document, complete_event)

    def _complete_kapsel_mode(self, query: str, mode: str = "kps") -> Iterable[Completion]:
        """Completes commands under scoped 'kapsel ' (system) or 'kps ' (tools) pipeline."""
        ends_with_space = query.endswith(" ")
        words = query.split()

        # 1. Primary: Carapace root tree completion for 'kapsel <query>' or 'kps <query>'
        root_cmd = "kapsel" if mode == "kapsel" else "kps"
        if self.carapace_engine.is_available() and self.carapace_engine.has_completer_for(root_cmd):
            # If user ran a native tool prefixed with kapsel/kps
            if words:
                first_tool = words[0].lower()
                target_cmd = (
                    self.kps_registry.get_system_command(first_tool)
                    if mode == "kapsel"
                    else self.kps_registry.get_feature_command(first_tool)
                )
                if not target_cmd and self.carapace_engine.has_completer_for(first_tool):
                    yield from self._yield_carapace_completions(query)
                    return

            cands = list(self._yield_carapace_completions(f"{root_cmd} {query}"))
            if cands:
                yield from cands
                return

        # 2. In-Memory fallback (when Carapace is unavailable or has no results)
        if ends_with_space:
            prefix = ""
        else:
            prefix = words[-1] if words else ""

        if mode == "kapsel":
            available_cmds = self.kps_registry.list_system_commands()
        else:
            available_cmds = self.kps_registry.list_feature_commands()

        # A. Completing primary command name
        if len(words) == 0 or (len(words) == 1 and not ends_with_space):
            for cmd in available_cmds:
                if cmd.name.startswith(prefix.lower()):
                    icon = "⚙️ " if mode == "kapsel" else "🚀 "
                    yield Completion(
                        text=cmd.name,
                        start_position=-len(prefix),
                        display=cmd.name,
                        display_meta=f"{icon}{cmd.help_text}",
                    )

        # B. Completing subcommands (e.g. 'kapsel config [edit|path|get|set]')
        elif len(words) >= 1:
            first_cmd_name = words[0].lower()
            cmd = self.kps_registry.get_system_command(first_cmd_name) if mode == "kapsel" else self.kps_registry.get_feature_command(first_cmd_name)

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

        # C. Plugin-provided dynamic completions (e.g. tldr cheat sheet caching)
        if self.plugin_manager:
            plugin_cands = self.plugin_manager.get_plugin_completions("kps " + query)
            for cand in plugin_cands:
                yield Completion(
                    text=cand.get("text", ""),
                    start_position=cand.get("start_position", -len(prefix)),
                    display=cand.get("display", cand.get("text", "")),
                    display_meta=cand.get("display_meta", "Plugin"),
                )

    def _complete_kp_mode(
        self, kp_body: str, document: Document, complete_event: CompleteEvent
    ) -> Iterable[Completion]:
        """
        Transparently proxies autocompletion for 'kp [-c] <commands...>'
        to Carapace native completions, tool builtins, and path completer.
        """
        stripped_body = kp_body.lstrip()

        # A. User just typed 'kp ' (empty body)
        if not stripped_body:
            # Suggest '-c' / '--concurrent' flag for parallel execution
            yield Completion(
                text="-c",
                start_position=0,
                display="-c",
                display_meta="⚡ 并发执行所有子任务 (kp -c)",
            )
            yield Completion(
                text="--concurrent",
                start_position=0,
                display="--concurrent",
                display_meta="⚡ 并发执行所有子任务 (kp -c)",
            )
            # Also suggest primary native tools
            native_builtins = [
                ("git", _("Git version control")),
                ("docker", _("Docker container platform")),
                ("npm", _("Node.js package manager")),
                ("pnpm", _("Fast disk space efficient package manager")),
                ("cargo", _("Rust package manager")),
                ("python", _("Python interpreter")),
                ("cd", _("Change directory")),
            ]
            for cmd, desc in native_builtins:
                yield Completion(
                    text=cmd,
                    start_position=0,
                    display=cmd,
                    display_meta=desc,
                )
            return

        # B. User is typing flags: 'kp -' or 'kp --'
        if stripped_body.startswith("-") and not stripped_body.startswith("-c ") and not stripped_body.startswith("--concurrent "):
            if "-c".startswith(stripped_body):
                yield Completion(
                    text="-c",
                    start_position=-len(stripped_body),
                    display="-c",
                    display_meta="⚡ 并发执行所有子任务 (kp -c)",
                )
            if "--concurrent".startswith(stripped_body):
                yield Completion(
                    text="--concurrent",
                    start_position=-len(stripped_body),
                    display="--concurrent",
                    display_meta="⚡ 并发执行所有子任务 (kp -c)",
                )
            if not stripped_body.endswith(" "):
                return

        # C. User typed 'kp -c ...' or 'kp --concurrent ...'
        inner_cmd = stripped_body
        if stripped_body.startswith("-c "):
            inner_cmd = stripped_body[3:].lstrip()
        elif stripped_body.startswith("--concurrent "):
            inner_cmd = stripped_body[13:].lstrip()

        if not inner_cmd:
            # Just typed 'kp -c ' -> suggest primary native tools
            native_builtins = [
                ("git", _("Git version control")),
                ("docker", _("Docker container platform")),
                ("npm", _("Node.js package manager")),
                ("pnpm", _("Fast disk space efficient package manager")),
                ("cargo", _("Rust package manager")),
                ("python", _("Python interpreter")),
            ]
            for cmd, desc in native_builtins:
                yield Completion(
                    text=cmd,
                    start_position=0,
                    display=cmd,
                    display_meta=desc,
                )
            return

        # D. Transparently proxy inner_cmd to native completion mode
        sub_doc = Document(text=inner_cmd, cursor_position=len(inner_cmd))
        yield from self._complete_native_mode(inner_cmd, sub_doc, complete_event)

    def _complete_native_mode(
        self, stripped: str, document: Document, complete_event: CompleteEvent
    ) -> Iterable[Completion]:
        parts = stripped.split()
        first_tool = parts[0].lower() if parts else ""
        if first_tool.endswith(".exe"):
            first_tool = first_tool[:-4]

        # A. Primary: Carapace Dynamic Completion (1,000+ commands with live context)
        if parts and self.carapace_engine.is_available():
            if self.carapace_engine.has_completer_for(first_tool):
                yield from self._yield_carapace_completions(stripped)
                return
            # In-Process Kapsel Mode Fallback:
            # If user typed an internal Kapsel command in REPL mode without 'kps ' prefix
            # (e.g. 'alias list', 'config edit', 'status'), route to Carapace 'kps <stripped>'!
            if self.kps_registry.get(first_tool) is not None:
                yield from self._yield_carapace_completions("kps " + stripped)
                return

        # B. Native Top-Level Builtins & High-Frequency Tools (when starting command line)
        if len(parts) <= 1 and not stripped.endswith(" "):
            curr_word = parts[0] if parts else ""
            native_builtins = [
                ("cd", _("Change directory")),
                ("clear", _("Clear terminal screen")),
                ("exit", _("Exit session")),
                ("git", _("Git version control")),
                ("docker", _("Docker container platform")),
                ("scoop", _("Windows command-line installer")),
                ("npm", _("Node.js package manager")),
                ("cargo", _("Rust package manager")),
                ("python", _("Python interpreter")),
                ("kubectl", _("Kubernetes cluster CLI")),
                ("pnpm", _("Fast disk space efficient package manager")),
                ("yarn", _("Node.js package manager")),
            ]
            for cmd, desc in native_builtins:
                if cmd.startswith(curr_word.lower()):
                    yield Completion(
                        text=cmd,
                        start_position=-len(curr_word),
                        display=cmd,
                        display_meta=desc,
                    )

        # C. Plugin-provided completions for native mode (e.g. mapping plugins)
        if self.plugin_manager:
            plugin_cands = self.plugin_manager.get_plugin_completions(stripped)
            curr_word = "" if stripped.endswith(" ") else (parts[-1] if parts else "")
            for cand in plugin_cands:
                yield Completion(
                    text=cand.get("text", ""),
                    start_position=cand.get("start_position", -len(curr_word)),
                    display=cand.get("display", cand.get("text", "")),
                    display_meta=cand.get("display_meta", "🔌 插件提供"),
                )

        # D. Filesystem Path Completion fallback
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
