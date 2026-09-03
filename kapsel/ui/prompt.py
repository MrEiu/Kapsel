import time
from typing import Optional

from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.filters import has_suggestion
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.key_processor import KeyPressEvent

from kapsel.core.engine import DualStateEngine
from kapsel.storage.config import KapselConfig
from kapsel.storage.history import KapselPromptHistory
from kapsel.core.completion import DualStateCompleter
from kapsel.ui.card import get_prompt_tokens
from kapsel.ui.theme import PT_STYLE


def extract_next_word(text: str) -> str:
    """
    Extracts the next token/word from suggestion text.
    Handles leading whitespace followed by word characters or symbols.
    e.g. 'commit -m fix' -> 'commit'
         ' -m fix' -> ' -m'
    """
    if not text:
        return ""
    idx = 0
    while idx < len(text) and text[idx].isspace():
        idx += 1
    if idx >= len(text):
        return text
    while idx < len(text) and not text[idx].isspace():
        idx += 1
    return text[:idx]


def create_key_bindings(config: KapselConfig) -> KeyBindings:
    """Configures modern terminal hotkeys with sensitivity-based right arrow tap vs hold."""
    kb = KeyBindings()
    last_press_time = 0.0
    consecutive_presses = 0

    # Right arrow accepts auto-suggestion when cursor is at the end of input
    @kb.add("right", filter=has_suggestion)
    def _(event: KeyPressEvent) -> None:
        nonlocal last_press_time, consecutive_presses
        buffer = event.current_buffer

        if buffer.cursor_position == len(buffer.text):
            suggestion = buffer.suggestion
            if not suggestion or not suggestion.text:
                buffer.cursor_right()
                return

            now = time.time()
            sensitivity = config.autosuggest_sensitivity
            threshold = config.consecutive_press_threshold

            dt = now - last_press_time
            last_press_time = now

            if dt <= sensitivity:
                consecutive_presses += 1
            else:
                consecutive_presses = 1

            # Check if this is continuous / long press (连按或长按)
            if consecutive_presses >= threshold:
                # 长按/连续按: 直接一键采纳整行完整建议
                buffer.insert_text(suggestion.text)
                consecutive_presses = 0
            else:
                # 单次间断按 (Tap): 根据配置逐词或整行采纳
                tap_mode = config.autosuggest_tap_mode
                if tap_mode == "word":
                    next_word = extract_next_word(suggestion.text)
                    buffer.insert_text(next_word)
                else:
                    buffer.insert_text(suggestion.text)
        else:
            buffer.cursor_right()

    def is_at_origin_history(buf) -> bool:
        """True if the buffer is at the origin (the line currently being typed)."""
        return buf.working_index >= len(buf._working_lines) - 1

    # Up arrow (↑):
    # - In completion: browse UP through candidates until index 0 -> return to origin (unselect)
    # - At origin: cancel completion and navigate BACKWARD into history
    # - In history: continue moving backward to older commands
    @kb.add("up")
    def _(event: KeyPressEvent) -> None:
        buffer = event.current_buffer

        # 1. If currently inside completion selection
        if buffer.complete_state and buffer.complete_state.complete_index is not None:
            curr_idx = buffer.complete_state.complete_index
            if curr_idx == 0:
                # Returned all the way to top -> go to origin (unselect, restoring original input)
                buffer.go_to_completion(None)
            else:
                buffer.complete_previous()
            return

        # 2. At Origin (or completion not actively selected) -> enter/continue History backward
        if buffer.complete_state:
            buffer.cancel_completion()
        buffer.history_backward()

    # Down arrow (↓):
    # - In history: browse DOWN through history until returning to origin (newest line)
    # - At origin: enter completion mode (select first candidate)
    # - In completion: browse DOWN through candidates
    @kb.add("down")
    def _(event: KeyPressEvent) -> None:
        buffer = event.current_buffer

        # 1. If currently browsing older history -> move forward towards origin
        if not is_at_origin_history(buffer):
            buffer.history_forward()
            # If this step returns the buffer to the origin, the user is back at center!
            # The next 'down' press will smoothly transition into completion.
            return

        # 2. At Origin (or already in completion mode) -> browse DOWN into completions
        if buffer.complete_state:
            buffer.complete_next()
        else:
            buffer.start_completion(select_first=True)

    # Shift-Tab: 在补全菜单中向上回退前一个候选词
    @kb.add("s-tab")
    def _(event: KeyPressEvent) -> None:
        buffer = event.current_buffer
        if buffer.complete_state:
            buffer.complete_previous()

    # Enter (回车键):
    # - 若处于候选词选中状态 (向下选定指令后): 确认采纳该词条并自动追加空格，光标停在行尾供继续追加参数 (不直接执行!)
    # - 若未在选词状态: 正常提交整行命令执行
    @kb.add("enter")
    def _(event: KeyPressEvent) -> None:
        buffer = event.current_buffer
        if buffer.complete_state and buffer.complete_state.complete_index is not None:
            buffer.complete_state = None
            if not buffer.text.endswith(" "):
                buffer.insert_text(" ")
            return

        buffer.validate_and_handle()

    # Tab (制表键): 选定候选词时同样一键采纳并补空格留待追加输入；未在选词时唤起或循环
    @kb.add("tab")
    def _(event: KeyPressEvent) -> None:
        buffer = event.current_buffer
        if buffer.complete_state and buffer.complete_state.complete_index is not None:
            buffer.complete_state = None
            if not buffer.text.endswith(" "):
                buffer.insert_text(" ")
            return

        if buffer.complete_state:
            buffer.complete_next()
        else:
            buffer.start_completion(select_first=True)

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
        self.history = KapselPromptHistory(
            manager=engine.history_mgr,
            limit=self.config.history_entries,
        )
        self.completer = DualStateCompleter(
            current_shell=engine.shell_name,
        )
        self.key_bindings = create_key_bindings(self.config)

        self.session: PromptSession = PromptSession(
            history=self.history,
            completer=self.completer,
            auto_suggest=AutoSuggestFromHistory() if self.config.enable_autosuggest else None,
            key_bindings=self.key_bindings,
            style=PT_STYLE,
            complete_while_typing=True,
            output=get_safe_output(),
        )

    def prompt(self) -> str:
        """Prompts the user for the next command line."""
        formatted_message = get_prompt_tokens(self.config, self.engine.shell_name)
        return self.session.prompt(formatted_message)
