import time
from typing import Optional

from prompt_toolkit import PromptSession
from prompt_toolkit.application import get_app
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.filters import Condition, has_suggestion
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


def copy_to_clipboard(text: str) -> bool:
    """Copies text to system clipboard using native platform utilities."""
    if not text:
        return False
    try:
        import subprocess
        import sys
        if sys.platform == "win32":
            p = subprocess.Popen(["clip.exe"], stdin=subprocess.PIPE, text=True)
            p.communicate(text)
            return p.returncode == 0
        elif sys.platform == "darwin":
            p = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE, text=True)
            p.communicate(text)
            return p.returncode == 0
        else:
            p = subprocess.Popen(["xclip", "-selection", "clipboard"], stdin=subprocess.PIPE, text=True)
            p.communicate(text)
            return p.returncode == 0
    except Exception:
        return False


class BlockRoamingController:
    """
    Manages Block Roaming Mode state and navigation.
    Triggered by Ctrl+Shift+B (or Ctrl+B).
    Allows navigating through previous command blocks using Up/Down arrows,
    and copying/re-executing them.
    """

    def __init__(self):
        self.is_active: bool = False
        self.current_index: int = -1
        self.saved_buffer_text: str = ""
        self.status_msg: str = ""

    def get_blocks(self) -> list:
        from kapsel.core.block.registry import get_block_registry
        return get_block_registry().get_blocks()

    def toggle(self, buffer) -> None:
        if self.is_active:
            self.exit_roaming(buffer, restore=True)
        else:
            self.enter_roaming(buffer)

    def enter_roaming(self, buffer) -> None:
        blocks = self.get_blocks()
        if not blocks:
            self.status_msg = "No command blocks in session history."
            return

        self.is_active = True
        self.saved_buffer_text = buffer.text
        self.current_index = len(blocks) - 1
        self.status_msg = ""
        self._sync_buffer_to_block(buffer)

    def exit_roaming(self, buffer, restore: bool = False) -> None:
        self.is_active = False
        self.status_msg = ""
        if restore:
            buffer.text = self.saved_buffer_text
            buffer.cursor_position = len(buffer.text)

    def _sync_buffer_to_block(self, buffer) -> None:
        blocks = self.get_blocks()
        if 0 <= self.current_index < len(blocks):
            block = blocks[self.current_index]
            buffer.text = block.command
            buffer.cursor_position = len(buffer.text)

    def move_up(self, buffer) -> None:
        blocks = self.get_blocks()
        if not blocks:
            return
        if self.current_index > 0:
            self.current_index -= 1
            self._sync_buffer_to_block(buffer)
            self.status_msg = ""

    def move_down(self, buffer) -> None:
        blocks = self.get_blocks()
        if not blocks:
            return
        if self.current_index < len(blocks) - 1:
            self.current_index += 1
            self._sync_buffer_to_block(buffer)
            self.status_msg = ""
        else:
            # Reached the end, exit roaming and restore original buffer text
            self.exit_roaming(buffer, restore=True)

    def copy_output(self) -> str:
        blocks = self.get_blocks()
        if 0 <= self.current_index < len(blocks):
            block = blocks[self.current_index]
            text = block.output_text or f"$ {block.command}\n(Exit: {block.exit_code})"
            if copy_to_clipboard(text):
                self.status_msg = f"✔ Block #{block.id} output copied to clipboard!"
            else:
                self.status_msg = "✖ Failed to copy output."
            return self.status_msg
        return ""

    def copy_command(self) -> str:
        blocks = self.get_blocks()
        if 0 <= self.current_index < len(blocks):
            block = blocks[self.current_index]
            if copy_to_clipboard(block.command):
                self.status_msg = f"✔ Block #{block.id} command copied to clipboard!"
            else:
                self.status_msg = "✖ Failed to copy command."
            return self.status_msg
        return ""

    def get_toolbar_tokens(self) -> list:
        if not self.is_active:
            return []

        blocks = self.get_blocks()
        if not (0 <= self.current_index < len(blocks)):
            return [("class:roaming.bar", " [块漫游模式] 暂无历史块 (按 Esc 退出) ")]

        block = blocks[self.current_index]
        idx_str = f"[{self.current_index + 1}/{len(blocks)}]"
        status_icon = "✔" if block.exit_code == 0 else "✖"
        status_class = "class:roaming.success" if block.exit_code == 0 else "class:roaming.failed"
        meta_str = f"{status_icon} {block.exit_code} ({block.duration_ms}ms)"

        extra = f" | {self.status_msg}" if self.status_msg else ""

        return [
            ("class:roaming.badge", " [块漫游模式] "),
            ("class:roaming.index", f" {idx_str} "),
            (status_class, f" {meta_str} "),
            ("class:roaming.help", f" ↑/↓ 移动 · Enter 填入 · y 复制输出 · c 复制指令 · r 重跑 · Esc 退出{extra} "),
        ]


def create_key_bindings(
    config: KapselConfig,
    tracker: Optional[HistoryEditTracker] = None,
    roaming: Optional[BlockRoamingController] = None,
) -> KeyBindings:
    """Configures modern terminal hotkeys with sensitivity-based right arrow tap vs hold."""
    kb = KeyBindings()
    hist_tracker = tracker or HistoryEditTracker()
    roam_ctrl = roaming or BlockRoamingController()
    last_press_time = 0.0
    consecutive_presses = 0

    is_roaming = Condition(lambda: roam_ctrl.is_active)
    is_not_roaming = Condition(lambda: not roam_ctrl.is_active)

    def _is_single_completion_active() -> bool:
        """True when the current completion dropdown contains exactly one candidate."""
        try:
            buf = get_app().current_buffer
            return bool(buf.complete_state and len(buf.complete_state.completions) == 1)
        except Exception:
            return False

    has_single_completion = Condition(_is_single_completion_active)

    # Right arrow accepts single completion or auto-suggestion when cursor is at the end of input
    @kb.add("right", filter=has_suggestion | has_single_completion)
    def _(event: KeyPressEvent) -> None:
        nonlocal last_press_time, consecutive_presses
        buffer = event.current_buffer

        if buffer.cursor_position == len(buffer.text):
            # 1. Higher priority: If exactly one completion candidate is recommended, accept it
            if buffer.complete_state and len(buffer.complete_state.completions) == 1:
                comp = buffer.complete_state.current_completion or buffer.complete_state.completions[0]
                buffer.apply_completion(comp)
                return

            # 2. Secondary priority: Accept historical ghost text auto-suggestion
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

    # -------------------------------------------------------------------------
    # Block Roaming Mode Controls (Ctrl+Shift+B / Ctrl+B)
    # -------------------------------------------------------------------------
    @kb.add("c-b")
    def _(event: KeyPressEvent) -> None:
        roam_ctrl.toggle(event.current_buffer)

    @kb.add("up", filter=is_roaming)
    @kb.add("k", filter=is_roaming)
    def _(event: KeyPressEvent) -> None:
        roam_ctrl.move_up(event.current_buffer)

    @kb.add("down", filter=is_roaming)
    @kb.add("j", filter=is_roaming)
    def _(event: KeyPressEvent) -> None:
        roam_ctrl.move_down(event.current_buffer)

    @kb.add("enter", filter=is_roaming)
    def _(event: KeyPressEvent) -> None:
        roam_ctrl.exit_roaming(event.current_buffer, restore=False)

    @kb.add("y", filter=is_roaming)
    def _(event: KeyPressEvent) -> None:
        roam_ctrl.copy_output()

    @kb.add("c", filter=is_roaming)
    def _(event: KeyPressEvent) -> None:
        roam_ctrl.copy_command()

    @kb.add("r", filter=is_roaming)
    def _(event: KeyPressEvent) -> None:
        roam_ctrl.exit_roaming(event.current_buffer, restore=False)
        event.current_buffer.validate_and_handle()

    @kb.add("escape", filter=is_roaming)
    @kb.add("q", filter=is_roaming)
    def _(event: KeyPressEvent) -> None:
        roam_ctrl.exit_roaming(event.current_buffer, restore=True)

    # Up arrow (↑):
    # - In completion: browse UP through candidates until index 0 -> return to origin (unselect)
    # - At origin: cancel completion and navigate BACKWARD into history
    # - In history: continue moving backward to older commands
    @kb.add("up", filter=is_not_roaming)
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
    @kb.add("down", filter=is_not_roaming)
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

    # Enter:
    # - If selecting a completion candidate: accept candidate via official apply_completion()
    # - Otherwise: submit current command line for execution
    @kb.add("enter", filter=is_not_roaming)
    def _(event: KeyPressEvent) -> None:
        buffer = event.current_buffer
        if buffer.complete_state and buffer.complete_state.complete_index is not None:
            buffer.apply_completion(buffer.complete_state.current_completion)
            return

        buffer.validate_and_handle()

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

    # Ctrl+C in prompt line: Completely ignore (no reaction, prevent spawning duplicate prompt cards)
    # Running commands will still be terminated by Ctrl+C via OS SIGINT once executed.
    @kb.add("c-c")
    def _(event: KeyPressEvent) -> None:
        pass

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
        self.roaming_controller = BlockRoamingController()
        self.key_bindings = create_key_bindings(
            self.config, tracker=self.history_tracker, roaming=self.roaming_controller
        )

        self.session: PromptSession = PromptSession(
            history=self.history,
            completer=self.completer,
            auto_suggest=AutoSuggestFromHistory() if self.config.enable_autosuggest else None,
            key_bindings=self.key_bindings,
            style=PT_STYLE,
            complete_while_typing=True,
            bottom_toolbar=self.roaming_controller.get_toolbar_tokens,
            output=get_safe_output(),
        )
        self.session.default_buffer.on_text_changed += self.history_tracker.on_text_changed

    def prompt(self) -> str:
        """Prompts the user for the next command line."""
        self.history_tracker.reset_prompt()
        from kapsel.core.block.registry import get_block_registry
        get_block_registry().preload_from_history(self.engine.history_mgr)

        formatted_message = get_prompt_tokens(self.config, self.engine.shell_name)
        return self.session.prompt(formatted_message)
