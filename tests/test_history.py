import asyncio
import pytest
from prompt_toolkit.application import Application
from prompt_toolkit.application.current import set_app
from prompt_toolkit.output import DummyOutput
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.completion import WordCompleter
from kapsel.ui.prompt import HistoryEditTracker, is_at_origin_history


def test_history_navigation_without_modification():
    """Verify standard backward and forward navigation in history without modification."""
    async def _test():
        hist = InMemoryHistory()
        hist.append_string("cmd1")
        hist.append_string("cmd2")

        app = Application(output=DummyOutput())
        set_app(app)
        buf = Buffer(history=hist)
        buf.load_history_if_not_yet_loaded()
        await asyncio.sleep(0.05)

        tracker = HistoryEditTracker()
        buf.on_text_changed += tracker.on_text_changed

        assert is_at_origin_history(buf)
        assert buf.text == ""

        # Navigate backward (Up)
        tracker.navigate_backward(buf)
        assert buf.text == "cmd2"
        assert not is_at_origin_history(buf)

        tracker.navigate_backward(buf)
        assert buf.text == "cmd1"
        assert not is_at_origin_history(buf)

        # Navigate forward (Down)
        tracker.navigate_forward(buf)
        assert buf.text == "cmd2"

        tracker.navigate_forward(buf)
        assert is_at_origin_history(buf)
        assert buf.text == ""

    asyncio.run(_test())


def test_history_modification_promotion_and_completion():
    """
    Verify that modifying recalled history promotes the line to origin
    and preserves original history while enabling down-arrow completion.
    """
    async def _test():
        hist = InMemoryHistory()
        hist.append_string("git status")
        hist.append_string("git checkout")

        app = Application(output=DummyOutput())
        set_app(app)
        completer = WordCompleter(["--branch", "-b", "--force"])
        buf = Buffer(history=hist, completer=completer, complete_while_typing=False)
        buf.load_history_if_not_yet_loaded()
        await asyncio.sleep(0.05)

        tracker = HistoryEditTracker()
        buf.on_text_changed += tracker.on_text_changed

        # Recall 'git checkout'
        tracker.navigate_backward(buf)
        assert buf.text == "git checkout"
        assert not is_at_origin_history(buf)

        # Modify recalled history line: append ' -'
        buf.insert_text(" -")

        # Should immediately be promoted to origin (active line)
        assert is_at_origin_history(buf)
        assert buf.text == "git checkout -"
        # Historical entry in history working lines must be preserved intact
        assert buf._working_lines[1] == "git checkout"

        # Simulate pressing Down arrow to trigger completion
        if tracker.promote_if_modified(buf):
            if buf.complete_state:
                buf.complete_next()
            else:
                buf.start_completion(select_first=True)
        elif not is_at_origin_history(buf):
            tracker.navigate_forward(buf)
        else:
            if buf.complete_state:
                buf.complete_next()
            else:
                buf.start_completion(select_first=True)

        await asyncio.sleep(0.05)
        assert buf.complete_state is not None
        assert buf.complete_state.current_completion.text in ["--branch", "-b", "--force"]

    asyncio.run(_test())


def test_history_multi_step_navigation_and_reset():
    """Verify deep history traversal, promotion of deep history item, and prompt reset."""
    async def _test():
        hist = InMemoryHistory()
        for cmd in ["echo 1", "echo 2", "echo 3", "echo 4"]:
            hist.append_string(cmd)

        app = Application(output=DummyOutput())
        set_app(app)
        buf = Buffer(history=hist)
        buf.load_history_if_not_yet_loaded()
        await asyncio.sleep(0.05)

        tracker = HistoryEditTracker()
        buf.on_text_changed += tracker.on_text_changed

        # Up 3 times to 'echo 2'
        tracker.navigate_backward(buf)  # echo 4
        tracker.navigate_backward(buf)  # echo 3
        tracker.navigate_backward(buf)  # echo 2
        assert buf.text == "echo 2"
        assert not is_at_origin_history(buf)

        # Down 1 time to 'echo 3'
        tracker.navigate_forward(buf)
        assert buf.text == "echo 3"
        assert not is_at_origin_history(buf)

        # Edit 'echo 3' -> 'echo 33'
        buf.insert_text("3")
        assert is_at_origin_history(buf)
        assert buf.text == "echo 33"

        # Verify historical line 'echo 3' was not overwritten in history
        assert buf._working_lines[2] == "echo 3"

        # Next prompt reset
        tracker.reset_prompt()
        assert tracker.recalled_history_index is None
        assert tracker.recalled_history_text is None
        assert not tracker.is_navigating
        assert not tracker.is_promoting

    asyncio.run(_test())


def test_ctrl_keybindings():
    """Verify that custom keybindings do not hijack Backspace / c-h, and navigation/word rubout handlers work."""
    from kapsel.storage.config import load_config
    from kapsel.ui.prompt import create_key_bindings

    cfg = load_config()
    kb = create_key_bindings(cfg)

    # 1. Verify custom keybindings do NOT hijack backspace or c-h
    assert kb.get_bindings_for_keys(("backspace",)) == []
    assert kb.get_bindings_for_keys(("c-h",)) == []

    buf = Buffer()
    buf.insert_text("git checkout -b feature")
    assert buf.cursor_position == 23

    class DummyEvent:
        def __init__(self, buffer):
            self.current_buffer = buffer

    event = DummyEvent(buf)

    # 2. Test Ctrl+Left (c-left) moves backward by word
    c_left = kb.get_bindings_for_keys(("c-left",))[0]
    c_left.handler(event)
    assert buf.cursor_position == 16

    # 3. Test Ctrl+Right (c-right) moves forward by word
    c_right = kb.get_bindings_for_keys(("c-right",))[0]
    c_right.handler(event)
    assert buf.cursor_position == 23

    # 4. Test Ctrl+W (word rubout backward)
    c_w = kb.get_bindings_for_keys(("c-w",))[0]
    c_w.handler(event)
    assert buf.text == "git checkout -b "

    # 5. Test Ctrl+U (c-u) clears line before cursor
    c_u = kb.get_bindings_for_keys(("c-u",))[0]
    c_u.handler(event)
    assert buf.text == ""
