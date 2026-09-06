"""
Unit tests for Kapsel Command Block subsystem:
BlockRegistry, BlockRunner (kp sequential & parallel execution),
and BlockRoamingController (Ctrl+Shift+B roaming mode).
All comments and docstrings are in English.
"""

from unittest.mock import MagicMock, patch
import pytest

from kapsel.core.block.model import BlockStatus, CommandBlock
from kapsel.core.block.registry import BlockRegistry, get_block_registry
from kapsel.core.block.runner import (
    execute_parallel_block,
    execute_sequential_block,
    split_commands,
)
from kapsel.completion.kps.dispatcher import dispatch_kps
from kapsel.ui.prompt import BlockRoamingController


def test_command_block_model():
    """Verify CommandBlock properties."""
    block = CommandBlock(
        id=1,
        command="echo test",
        exit_code=0,
        duration_ms=10,
        status=BlockStatus.SUCCESS,
    )
    assert block.success is True
    assert block.exit_code == 0

    failed_block = CommandBlock(
        id=2,
        command="exit 1",
        exit_code=1,
        duration_ms=5,
        status=BlockStatus.FAILED,
    )
    assert failed_block.success is False


def test_block_registry_operations():
    """Verify BlockRegistry addition, limits, and lookups."""
    reg = BlockRegistry(max_blocks=5)
    assert reg.count() == 0

    # Add blocks
    for i in range(1, 8):
        reg.add_block(command=f"cmd{i}", exit_code=0, duration_ms=i * 10)

    # Max blocks limit respected
    assert reg.count() == 5
    blocks = reg.get_blocks()
    assert blocks[0].command == "cmd3"
    assert blocks[-1].command == "cmd7"

    # Latest block
    assert reg.latest().command == "cmd7"

    # Index lookups
    assert reg.get_block_by_index(0).command == "cmd3"
    assert reg.get_block_by_index(4).command == "cmd7"
    assert reg.get_block_by_index(10) is None


def test_block_registry_preload_from_history():
    """Verify BlockRegistry can preload from SQLite HistoryManager."""
    reg = BlockRegistry()
    mock_history = MagicMock()
    mock_history.get_recent_records.return_value = [
        {"command": "git status", "cwd": "/repo", "exit_code": 0, "duration_ms": 12},
        {"command": "pnpm build", "cwd": "/repo", "exit_code": 0, "duration_ms": 350},
    ]

    reg.preload_from_history(mock_history)
    assert reg.count() == 2
    assert reg.get_blocks()[0].command == "git status"
    assert reg.get_blocks()[1].command == "pnpm build"

    # Second preload should be a no-op since registry is already populated
    reg.preload_from_history(mock_history)
    assert reg.count() == 2


def test_split_commands():
    """Verify multi-line parsing ignores blank lines and comments."""
    raw = """
    # Setup repository
    git clone https://github.com/demo/app
    
    cd app
    # Run installation
    pnpm install
    pnpm test
    """
    cmds = split_commands(raw)
    assert cmds == [
        "git clone https://github.com/demo/app",
        "cd app",
        "pnpm install",
        "pnpm test",
    ]


def test_execute_sequential_block_success():
    """Verify sequential execution runs commands in order."""
    mock_executor = MagicMock()
    mock_executor.execute.side_effect = [
        MagicMock(exit_code=0),
        MagicMock(exit_code=0),
    ]

    commands = ["echo A", "echo B"]
    exit_code, output = execute_sequential_block(commands, executor=mock_executor)

    assert exit_code == 0
    assert mock_executor.execute.call_count == 2
    assert "$ echo A (exit 0)" in output
    assert "$ echo B (exit 0)" in output


def test_execute_sequential_block_atomic_abort_on_failure():
    """Verify that failure in an atomic block halts subsequent commands."""
    mock_executor = MagicMock()
    mock_executor.execute.side_effect = [
        MagicMock(exit_code=0),
        MagicMock(exit_code=1),  # Fails here
        MagicMock(exit_code=0),
    ]

    commands = ["echo step1", "failing_cmd", "should_not_run"]
    exit_code, output = execute_sequential_block(commands, executor=mock_executor)

    assert exit_code == 1
    # Third command was never executed
    assert mock_executor.execute.call_count == 2
    assert "should_not_run" not in output


def test_execute_parallel_block():
    """Verify parallel execution runs tasks concurrently."""
    with patch(
        "kapsel.core.block.runner._run_single_command_process",
        side_effect=[
            (0, "output 1", 20),
            (0, "output 2", 15),
        ],
    ):
        commands = ["task1", "task2"]
        exit_code, output = execute_parallel_block(commands, max_workers=2)

        assert exit_code == 0
        assert "task1" in output
        assert "task2" in output


def test_dispatch_kps_kp_routing():
    """Verify 'kp' and 'kp -c' commands are routed properly by dispatch_kps."""
    mock_executor = MagicMock()
    mock_executor.execute.return_value = MagicMock(exit_code=0)

    # 1. kp help
    code = dispatch_kps("kp help")
    assert code == 0

    # 2. kp sequential
    with patch("kapsel.core.block.runner.execute_sequential_block", return_value=(0, "ok")) as mock_seq:
        code = dispatch_kps("kp echo 1\necho 2", executor=mock_executor)
        assert code == 0
        assert mock_seq.called
        assert mock_seq.call_args[0][0] == ["echo 1", "echo 2"]

    # 3. kp -c concurrent
    with patch("kapsel.core.block.runner.execute_parallel_block", return_value=(0, "parallel ok")) as mock_par:
        code = dispatch_kps("kp -c echo A\necho B", executor=mock_executor)
        assert code == 0
        assert mock_par.called
        assert mock_par.call_args[0][0] == ["echo A", "echo B"]


def test_block_roaming_controller():
    """Verify BlockRoamingController navigation, entering, and exiting."""
    reg = get_block_registry()
    reg.clear()
    reg.add_block(command="cmd1", exit_code=0, duration_ms=10)
    reg.add_block(command="cmd2", exit_code=1, duration_ms=25)
    reg.add_block(command="cmd3", exit_code=0, duration_ms=5)

    controller = BlockRoamingController()
    mock_buffer = MagicMock()
    mock_buffer.text = "typing something"

    # 1. Enter roaming mode
    controller.enter_roaming(mock_buffer)
    assert controller.is_active is True
    # Focuses latest block (index 2: cmd3)
    assert controller.current_index == 2
    assert mock_buffer.text == "cmd3"

    # 2. Move up (focus index 1: cmd2)
    controller.move_up(mock_buffer)
    assert controller.current_index == 1
    assert mock_buffer.text == "cmd2"

    # 3. Move up again (focus index 0: cmd1)
    controller.move_up(mock_buffer)
    assert controller.current_index == 0
    assert mock_buffer.text == "cmd1"

    # 4. Cannot move up past 0
    controller.move_up(mock_buffer)
    assert controller.current_index == 0

    # 5. Move down (focus index 1: cmd2)
    controller.move_down(mock_buffer)
    assert controller.current_index == 1
    assert mock_buffer.text == "cmd2"

    # 6. Toolbar tokens generated
    tokens = controller.get_toolbar_tokens()
    assert len(tokens) > 0
    assert any("块漫游模式" in t[1] for t in tokens)

    # 7. Exit roaming mode with restore=True
    controller.exit_roaming(mock_buffer, restore=True)
    assert controller.is_active is False
    assert mock_buffer.text == "typing something"


def test_kp_autocompletion_proxy():
    """Verify that 'kp' and 'kp -c' transparently proxy autocompletions to native engines."""
    from prompt_toolkit.document import Document
    from prompt_toolkit.completion import CompleteEvent
    from kapsel.completion.completer import DualStateCompleter

    completer = DualStateCompleter()

    # 1. 'kp ' (empty body) -> suggests -c flag and native builtins (git, docker, npm...)
    kp_empty_cands = list(completer.get_completions(Document("kp "), CompleteEvent()))
    texts_empty = [c.text for c in kp_empty_cands]
    assert "-c" in texts_empty
    assert "--concurrent" in texts_empty
    assert "git" in texts_empty
    assert "npm" in texts_empty
    # start_position must be 0 (no characters eaten)
    minus_c_comp = [c for c in kp_empty_cands if c.text == "-c"][0]
    assert minus_c_comp.start_position == 0

    # 2. 'kp -' (typing flags) -> suggests -c and --concurrent
    kp_flag_cands = list(completer.get_completions(Document("kp -"), CompleteEvent()))
    flag_texts = [c.text for c in kp_flag_cands]
    assert "-c" in flag_texts
    assert "--concurrent" in flag_texts
    minus_c_flag = [c for c in kp_flag_cands if c.text == "-c"][0]
    assert minus_c_flag.start_position == -1

    # 3. 'kp git' or 'kp g' -> suggests git
    kp_g_cands = list(completer.get_completions(Document("kp g"), CompleteEvent()))
    assert any(c.text == "git" for c in kp_g_cands)

    # 4. 'kp -c git' or 'kp -c g' -> suggests git
    kp_c_g_cands = list(completer.get_completions(Document("kp -c g"), CompleteEvent()))
    assert any(c.text == "git" for c in kp_c_g_cands)

    # 5. Multi-line: line 1 is 'kp', line 2 is 'g' -> suggests git on line 2
    multi_doc = Document("kp\ng", cursor_position=4)
    multi_cands = list(completer.get_completions(multi_doc, CompleteEvent()))
    assert any(c.text == "git" for c in multi_cands)


def test_ctrl_enter_block_execution_keybinding():
    """Verify Ctrl+Enter (c-j) automatically wraps input with 'kp ' and executes as a block."""
    from kapsel.ui.prompt import create_key_bindings
    from kapsel.storage.config import KapselConfig

    cfg = KapselConfig()
    kb = create_key_bindings(cfg)

    # Check that 'c-j' handler is bound
    c_j_bindings = kb.get_bindings_for_keys(("c-j",))
    assert len(c_j_bindings) > 0

    handler = c_j_bindings[0].handler

    # 1. User typed 'git status' (without kp)
    mock_event = MagicMock()
    mock_buffer = MagicMock()
    mock_buffer.complete_state = None
    mock_buffer.text = "git status"
    mock_event.current_buffer = mock_buffer

    handler(mock_event)
    assert mock_buffer.text == "kp git status"
    mock_buffer.validate_and_handle.assert_called_once()

    # 2. User typed 'kp echo 1' (already has kp)
    mock_event2 = MagicMock()
    mock_buffer2 = MagicMock()
    mock_buffer2.complete_state = None
    mock_buffer2.text = "kp echo 1"
    mock_event2.current_buffer = mock_buffer2

    handler(mock_event2)
    assert mock_buffer2.text == "kp echo 1"
    mock_buffer2.validate_and_handle.assert_called_once()
