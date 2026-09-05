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
from kapsel.completion import DualStateCompleter
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


def is_at_origin_history(buf) -> bool:
    """True if the buffer is at the origin (the active line currently being typed)."""
    return buf.working_index >= len(buf._working_lines) - 1


class HistoryEditTracker:
    """
    Tracks navigation into history and promotes modified historical commands
    to the origin buffer state, enabling immediate completion with the down arrow.
    """

    def __init__(self):
        self.recalled_history_index: Optional[int] = None
        self.recalled_history_text: Optional[str] = None
        self.is_navigating: bool = False
        self.is_promoting: bool = False

    def navigate_backward(self, buffer) -> None:
        """Navigates backward into history while tracking the recalled line."""
        self.is_navigating = True
        try:
            buffer.history_backward()
            origin_index = len(buffer._working_lines) - 1
            if buffer.working_index < origin_index:
                self.recalled_history_index = buffer.working_index
                self.recalled_history_text = buffer.text
            else:
                self.recalled_history_index = None
                self.recalled_history_text = None
        finally:
            self.is_navigating = False

    def navigate_forward(self, buffer) -> None:
        """Navigates forward through history towards the origin."""
        self.is_navigating = True
        try:
            buffer.history_forward()
            origin_index = len(buffer._working_lines) - 1
            if buffer.working_index < origin_index:
                self.recalled_history_index = buffer.working_index
                self.recalled_history_text = buffer.text
            else:
                self.recalled_history_index = None
                self.recalled_history_text = None
        finally:
            self.is_navigating = False

    def on_text_changed(self, buffer) -> None:
        """
        Called on any text edit. If the user modified a recalled history entry,
        promote the modified text to the origin (current buffer state) and
        restore the original history entry.
        """
        if self.is_navigating or self.is_promoting:
            return

        origin_index = len(buffer._working_lines) - 1
        if buffer.working_index < origin_index:
            if self.recalled_history_text is not None and buffer.text != self.recalled_history_text:
                try:
                    self.is_promoting = True
                    edited_text = buffer.text
                    cursor_pos = buffer.cursor_position
                    old_idx = self.recalled_history_index
                    orig_text = self.recalled_history_text

                    # Restore unmodified historical line in history buffer
                    if old_idx is not None and 0 <= old_idx < len(buffer._working_lines):
                        buffer._working_lines[old_idx] = orig_text

                    # Set edited text as the current origin state
                    buffer._working_lines[origin_index] = edited_text
                    buffer.working_index = origin_index
                    buffer.cursor_position = cursor_pos

                    self.recalled_history_index = None
                    self.recalled_history_text = None
                finally:
                    self.is_promoting = False

    def promote_if_modified(self, buffer) -> bool:
        """Explicitly checks and promotes if text was modified while in history."""
        origin_index = len(buffer._working_lines) - 1
        if buffer.working_index < origin_index:
            if self.recalled_history_text is not None and buffer.text != self.recalled_history_text:
                self.on_text_changed(buffer)
                return True
        return False

    def reset_prompt(self) -> None:
        """Resets tracking state at the beginning of each prompt cycle."""
        self.recalled_history_index = None
        self.recalled_history_text = None
        self.is_navigating = False
        self.is_promoting = False


def create_key_bindings(
    config: KapselConfig, tracker: Optional[HistoryEditTracker] = None
) -> KeyBindings:
    """Configures modern terminal hotkeys with sensitivity-based right arrow tap vs hold."""
    kb = KeyBindings()
    hist_tracker = tracker or HistoryEditTracker()
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

            # Check if this is continuous / long press
            if consecutive_presses >= threshold:
                # Continuous press: accept entire suggestion line
                buffer.insert_text(suggestion.text)
                consecutive_presses = 0
            else:
                # Single tap: word-by-word or full line per config
                tap_mode = config.autosuggest_tap_mode
                if tap_mode == "word":
                    next_word = extract_next_word(suggestion.text)
                    buffer.insert_text(next_word)
                else:
                    buffer.insert_text(suggestion.text)
        else:
            buffer.cursor_right()

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
        hist_tracker.navigate_backward(buffer)

    # Down arrow (↓):
    # - If modified history: immediately promotes to origin and enters completion mode!
    # - In history: browse DOWN through history until returning to origin (newest line)
    # - At origin: enter completion mode (select first candidate)
    # - In completion: browse DOWN through candidates
    @kb.add("down")
    def _(event: KeyPressEvent) -> None:
        buffer = event.current_buffer

        # 1. If currently browsing older history but user modified it -> promote to origin!
        if hist_tracker.promote_if_modified(buffer):
            if buffer.complete_state:
                buffer.complete_next()
            else:
                buffer.start_completion(select_first=True)
            return

        # 2. If currently browsing older history -> move forward towards origin
        if not is_at_origin_history(buffer):
            hist_tracker.navigate_forward(buffer)
            return

        # 3. At Origin (or already in completion mode) -> browse DOWN into completions
        if buffer.complete_state:
            buffer.complete_next()
        else:
            buffer.start_completion(select_first=True)

    # Shift-Tab: cycle backwards in completion menu
    @kb.add("s-tab")
    def _(event: KeyPressEvent) -> None:
        buffer = event.current_buffer
        if buffer.complete_state:
            buffer.complete_previous()



    # Tab: accept completion candidate if selected; otherwise trigger/cycle completions
    @kb.add("tab")
    def _(event: KeyPressEvent) -> None:
        buffer = event.current_buffer
        if buffer.complete_state and buffer.complete_state.complete_index is not None:
            buffer.apply_completion(buffer.complete_state.current_completion)
            return

        if buffer.complete_state:
            buffer.complete_next()
        else:
            buffer.start_completion(select_first=True)

    # -------------------------------------------------------------------------
    # Standard Hotkeys & Navigation
    # -------------------------------------------------------------------------

    # Ctrl+C: Cancel current line
    @kb.add("c-c")
    def _(event: KeyPressEvent) -> None:
        event.app.exit(exception=KeyboardInterrupt)

    # Word rubout backward: Ctrl+W, Alt+Backspace, and Esc+Backspace
    # Note: Do NOT bind 'c-h' or 'backspace' here. In prompt_toolkit, 'backspace'
    # is aliased to 'c-h'. Binding either would hijack single-character backspace.
    @kb.add("c-w")
    @kb.add("escape", "backspace")
    @kb.add("escape", "c-h")
    def _(event: KeyPressEvent) -> None:
        buffer = event.current_buffer
        pos = buffer.document.find_previous_word_beginning(count=1)
        if pos is not None:
            buffer.delete_before_cursor(count=-pos)
        elif buffer.cursor_position > 0:
            buffer.delete_before_cursor(count=buffer.cursor_position)

    # Word navigation: Ctrl+Left / Ctrl+Right / Alt+B / Alt+F
    @kb.add("c-left")
    @kb.add("escape", "b")
    def _(event: KeyPressEvent) -> None:
        buffer = event.current_buffer
        pos = buffer.document.find_previous_word_beginning(count=1)
        buffer.cursor_position = buffer.cursor_position + pos if pos is not None else 0

    @kb.add("c-right")
    @kb.add("escape", "f")
    def _(event: KeyPressEvent) -> None:
        buffer = event.current_buffer
        pos = buffer.document.find_next_word_ending(count=1)
        buffer.cursor_position = buffer.cursor_position + pos if pos is not None else len(buffer.text)

    # Ctrl+U: Clear line before cursor
    @kb.add("c-u")
    def _(event: KeyPressEvent) -> None:
        buffer = event.current_buffer
        if buffer.cursor_position > 0:
            buffer.delete_before_cursor(count=buffer.cursor_position)

    # Ctrl+K: Clear line after cursor
    @kb.add("c-k")
    def _(event: KeyPressEvent) -> None:
        buffer = event.current_buffer
        remaining = len(buffer.text) - buffer.cursor_position
        if remaining > 0:
            buffer.delete(count=remaining)

    # Ctrl+A / Ctrl+E: Jump to start / end of line
    @kb.add("c-a")
    def _(event: KeyPressEvent) -> None:
        event.current_buffer.cursor_position = 0

    @kb.add("c-e")
    def _(event: KeyPressEvent) -> None:
        event.current_buffer.cursor_position = len(event.current_buffer.text)

    # Ctrl+Delete / Alt+D: Delete word forward
    @kb.add("c-delete")
    @kb.add("escape", "d")
    def _(event: KeyPressEvent) -> None:
        buffer = event.current_buffer
        pos = buffer.document.find_next_word_ending(count=1)
        if pos is not None:
            buffer.delete(count=pos)
        else:
            buffer.delete(count=len(buffer.text) - buffer.cursor_position)

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
        from prompt_toolkit.completion import ThreadedCompleter

        self.engine = engine
        self.config = engine.config
        self.history = KapselPromptHistory(
            manager=engine.history_mgr,
            limit=self.config.history_entries,
        )
        self.raw_completer = DualStateCompleter(
            current_shell=engine.shell_name,
            plugin_manager=getattr(engine, "plugin_manager", None),
        )
        # ThreadedCompleter runs Carapace subprocesses in worker threads
        # preventing any keystroke freezing or UI latency during typing
        self.completer = ThreadedCompleter(self.raw_completer)
        self.history_tracker = HistoryEditTracker()
        self.key_bindings = create_key_bindings(self.config, tracker=self.history_tracker)

        self.session: PromptSession = PromptSession(
            history=self.history,
            completer=self.completer,
            auto_suggest=AutoSuggestFromHistory() if self.config.enable_autosuggest else None,
            key_bindings=self.key_bindings,
            style=PT_STYLE,
            complete_while_typing=True,
            output=get_safe_output(),
        )
        self.session.default_buffer.on_text_changed += self.history_tracker.on_text_changed

    def prompt(self) -> str:
        """Prompts the user for the next command line."""
        self.history_tracker.reset_prompt()
        formatted_message = get_prompt_tokens(self.config, self.engine.shell_name)
        return self.session.prompt(formatted_message)
