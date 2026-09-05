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

        # 1. User is typing 'kapsel' or 'kps' (offer transition without trailing space)
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
            return
        if stripped in ("kp", "kps"):
            yield Completion(
                text="kps",
                start_position=-len(stripped),
                display="kps",
                display_meta="Kapsel command alias (kps)",
            )
            return

        # 2. Unified Kapsel Command Mode: 'kapsel <cmd>' or 'kps <cmd>'
        if stripped.startswith("kapsel "):
            sub = stripped[7:]
            yield from self._complete_kapsel_mode(sub)
            return

        if stripped.startswith("kps "):
            sub = stripped[4:]
            yield from self._complete_kapsel_mode(sub)
            return

        # 3. Native Mode: Carapace (1000+ tools), Fig fallback, builtins, & paths
        yield from self._complete_native_mode(stripped, document, complete_event)

    def _complete_kapsel_mode(self, query: str) -> Iterable[Completion]:
        """Completes commands under unified 'kapsel ' and 'kps ' pipeline."""
        ends_with_space = query.endswith(" ")
        words = query.split()

        # 1. Primary: Carapace unified root tree completion for 'kps <query>'
        if self.carapace_engine.is_available() and self.carapace_engine.has_completer_for("kps"):
            # If user ran a native tool prefixed with kapsel/kps (e.g. 'kps git checkout')
            if words and not self.kps_registry.get(words[0].lower()):
                first_tool = words[0].lower()
                if self.carapace_engine.has_completer_for(first_tool):
                    yield from self._yield_carapace_completions(query)
                    return

            cands = list(self._yield_carapace_completions("kps " + query))
            if cands:
                yield from cands
                return

        # 2. In-Memory fallback (when Carapace is unavailable or has no results)
        if ends_with_space:
            prefix = ""
        else:
            prefix = words[-1] if words else ""

        available_cmds = self.kps_registry.list_commands()

        # A. Completing primary command name (e.g. 'kapsel conf', 'kps ai', etc.)
        if len(words) == 0 or (len(words) == 1 and not ends_with_space):
            for cmd in available_cmds:
                if cmd.name.startswith(prefix.lower()):
                    icon = "🚀 " if cmd.plugin_id else "⚙️ "
                    yield Completion(
                        text=cmd.name,
                        start_position=-len(prefix),
                        display=cmd.name,
                        display_meta=f"{icon}{cmd.help_text}",
                    )

        # B. Completing subcommands (e.g. 'kapsel config [edit|path|get|set]')
        elif len(words) >= 1:
            first_cmd_name = words[0].lower()
            cmd = self.kps_registry.get(first_cmd_name)
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
            for cand in plugin_cands:
                yield Completion(
                    text=cand.get("text", ""),
                    start_position=cand.get("start_position", -len(parts[-1]) if parts else 0),
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
