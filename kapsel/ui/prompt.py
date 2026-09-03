"""
Kapsel interactive PromptSession manager.
Integrates dual-state completer, SQLite history, autosuggestion, and rich keyboard bindings.
"""

from typing import Optional

from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.filters import has_suggestion
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.key_processor import KeyPressEvent

from kapsel.core.engine import DualStateEngine
from kapsel.storage.config import KapselConfig
from kapsel.storage.history import KapselPromptHistory
from kapsel.ui.card import get_prompt_tokens
from kapsel.ui.completer import DualStateCompleter
from kapsel.ui.theme import PT_STYLE


def create_key_bindings() -> KeyBindings:
    """Configures modern terminal hotkeys."""
    kb = KeyBindings()

    # Right arrow accepts auto-suggestion when cursor is at the end of input
    @kb.add("right", filter=has_suggestion)
    def _(event: KeyPressEvent) -> None:
        buffer = event.current_buffer
        if buffer.cursor_position == len(buffer.text):
            suggestion = buffer.suggestion
            if suggestion:
                buffer.insert_text(suggestion.text)
        else:
            buffer.cursor_right()

    return kb


def get_safe_output():
    """Provides a safe output backend, falling back gracefully if no console buffer exists."""
    try:
        from prompt_toolkit.output.defaults import create_output
        return create_output()
    except Exception:
        from prompt_toolkit.output import DummyOutput
        return DummyOutput()


class KapselPrompt:
    """Manages the terminal prompt session lifecycle."""

    def __init__(self, engine: DualStateEngine):
        self.engine = engine
        self.config = engine.config
        self.history = KapselPromptHistory(engine.history_mgr)
        self.completer = DualStateCompleter(
            registry=engine.registry,
            history_mgr=engine.history_mgr,
            current_shell=engine.shell_name,
        )
        self.key_bindings = create_key_bindings()

        self.session: PromptSession = PromptSession(
            history=self.history,
            completer=self.completer,
            auto_suggest=AutoSuggestFromHistory() if self.config.enable_autosuggest else None,
            key_bindings=self.key_bindings,
            style=PT_STYLE,
            complete_while_typing=True,
            bottom_toolbar=self._get_bottom_toolbar,
            output=get_safe_output(),
        )

    def _get_bottom_toolbar(self):
        """Dynamically renders real-time state badge based on current input buffer."""
        from prompt_toolkit.application.current import get_app
        from prompt_toolkit.formatted_text import FormattedText

        try:
            app = get_app()
            text = app.current_buffer.text.lstrip()
        except Exception:
            text = ""

        shell = self.engine.shell_name

        if text.startswith("kps ") or text == "kps":
            return FormattedText([
                ("class:toolbar.kps", " 💊 胶囊映射态 (Kapsel Mode) "),
                ("class:toolbar.kps_info", f" Linux记忆 ➜ 自动转义至 {shell} | [Tab] 映射候选 | [Enter] 执行 "),
            ])
        else:
            return FormattedText([
                ("class:toolbar.native", f" ⚡ 原生透传态 (Native: {shell}) "),
                ("class:toolbar.native_info", " 原生命令直通 | [Tab] 路径补全 | [→] 采纳历史 | 输入 'kps ' 激活胶囊 "),
            ])

    def prompt(self) -> str:
        """Prompts the user for the next command line."""
        formatted_message = get_prompt_tokens(self.config, self.engine.shell_name)
        return self.session.prompt(formatted_message)
