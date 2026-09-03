"""
Kapsel Dual-State Completer.
Seamlessly transitions between Native path completion and Kapsel rich Linux-First mappings.
"""

from pathlib import Path
from typing import Iterable, Optional

from prompt_toolkit.completion import CompleteEvent, Completer, Completion, PathCompleter
from prompt_toolkit.document import Document
from prompt_toolkit.formatted_text import HTML

from kapsel.storage.commands import CommandEntry, CommandRegistry
from kapsel.storage.history import HistoryManager


class DualStateCompleter(Completer):
    """
    Dual-State Completer:
    - Native Mode: Filesystem paths and directory completion.
    - Kapsel Mode ('kps '): Rich perception menu with Chinese description and native preview.
    """

    def __init__(
        self,
        registry: CommandRegistry,
        history_mgr: HistoryManager,
        current_shell: str = "pwsh",
    ):
        self.registry = registry
        self.history_mgr = history_mgr
        self.current_shell = current_shell
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

        # 2. Kapsel Mode: starts with 'kps '
        if stripped.startswith("kps "):
            sub = stripped[4:]  # Text after 'kps '

            # Check if an existing alias already fully matches and there are trailing arguments
            # e.g., 'kps rm -rf n' -> complete paths for 'n'
            match = self.registry.find_best_match(sub)
            if match and " " in sub:
                entry, raw_args = match
                # If the alias is followed by space, complete filesystem paths for args
                if sub.startswith(entry.alias + " "):
                    for c in self.path_completer.get_completions(document, complete_event):
                        yield Completion(
                            text=c.text,
                            start_position=c.start_position,
                            display=c.display,
                            display_meta="📁 [参数路径]",
                        )
                    return

            # Otherwise, offer Kapsel command menu
            weights = self.history_mgr.get_command_weights()
            query = sub.lower()

            # Filter matching entries
            candidates = []
            for entry in self.registry.list_all():
                if query in entry.alias.lower() or not query:
                    score = weights.get(entry.alias, 0)
                    # Exact prefix match gets priority bonus
                    if entry.alias.lower().startswith(query):
                        score += 100
                    candidates.append((score, entry))

            # Sort descending by score, then ascending by alias length
            candidates.sort(key=lambda item: (item[0], -len(item[1].alias)), reverse=True)

            for _, entry in candidates:
                template = entry.get_template_for_shell(self.current_shell) or ""
                # Clean up template preview
                clean_preview = template.replace("{{args}}", "").strip()

                meta_text = f"💊 [胶囊] {entry.desc}  ➜  {clean_preview}"
                yield Completion(
                    text=entry.alias,
                    start_position=-len(sub),
                    display=entry.alias,
                    display_meta=meta_text,
                )
            return

        # 3. Native Mode: Delegate to native filesystem path completion
        for c in self.path_completer.get_completions(document, complete_event):
            yield Completion(
                text=c.text,
                start_position=c.start_position,
                display=c.display,
                display_meta="📁 [原生路径]",
            )
