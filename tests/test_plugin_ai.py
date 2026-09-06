"""
Unit tests for Kapsel native AI copilot plugin (powered by OpenAI Python SDK).
All comments and test descriptions are in English.
"""

from io import StringIO
import os
from pathlib import Path
import sys
from unittest.mock import MagicMock, patch
import pytest
from rich.console import Console

from plugins.ai.plugin import AiPlugin
from plugins.ai.config import save_ai_config, load_ai_config, get_ai_config_file
from plugins.ai.client import AiClient
from plugins.ai.actions import (
    action_do,
    action_fix,
    action_explain,
    action_pipe,
    action_scout,
    action_commit,
)
from kapsel.core.block.model import CommandBlock
from kapsel.core.block.registry import get_block_registry


@pytest.fixture
def temp_ai_config(tmp_path, monkeypatch):
    """Isolates AI configuration file to a temporary directory."""
    test_cfg_file = tmp_path / "config.yaml"
    monkeypatch.setattr("plugins.ai.config.get_ai_config_file", lambda: test_cfg_file)
    monkeypatch.setattr("plugins.ai.plugin.get_ai_config_file", lambda: test_cfg_file)
    monkeypatch.setattr("plugins.ai.wizard.get_ai_config_file", lambda: test_cfg_file)
    return test_cfg_file


def test_ai_plugin_manifest():
    """Manifest must specify version 0.1.1 and zero external binary dependencies."""
    plugin = AiPlugin()
    assert plugin.manifest.id == "ai"
    assert plugin.manifest.version == "0.1.1"
    assert plugin.manifest.dependencies == []


def test_ai_plugin_registration():
    """Plugin must register 'ai' command under kps scope."""
    plugin = AiPlugin()
    mock_context = MagicMock()
    plugin.on_load(mock_context)
    mock_context.register_kps_command.assert_called_once()
    args, kwargs = mock_context.register_kps_command.call_args
    assert kwargs["name"] == "ai"
    assert kwargs["scope"] == "feature"


def test_ai_bare_and_help(temp_ai_config):
    """Bare invocation and help flags must show help and return 0 without hanging in REPL."""
    plugin = AiPlugin()
    con = Console(file=StringIO(), legacy_windows=False)

    assert plugin.handle_ai([], console=con) == 0
    assert plugin.handle_ai(["--help"], console=con) == 0
    assert plugin.handle_ai(["help"], console=con) == 0


def test_ai_config_status_uninitialized(temp_ai_config):
    """Config status should warn if uninitialized."""
    plugin = AiPlugin()
    out = StringIO()
    con = Console(file=out, legacy_windows=False)

    code = plugin.handle_ai(["config", "status"], console=con)
    assert code == 1
    assert "not been initialized" in out.getvalue()


def test_ai_config_save_and_status(temp_ai_config):
    """Saved configuration should be loaded and accurately displayed in status."""
    cfg = {
        "provider": "deepseek",
        "provider_name": "DeepSeek Official",
        "api_base": "https://api.deepseek.com/v1",
        "api_key": "sk-testkey123456",
        "model": "deepseek-chat",
    }
    save_ai_config(cfg)
    loaded = load_ai_config()
    assert loaded is not None
    assert loaded["model"] == "deepseek-chat"

    plugin = AiPlugin()
    out = StringIO()
    con = Console(file=out, legacy_windows=False)

    code = plugin.handle_ai(["config", "status"], console=con)
    assert code == 0
    output_text = out.getvalue()
    assert "deepseek-chat" in output_text
    assert "DeepSeek Official" in output_text


def test_ai_config_switch_model(temp_ai_config):
    """'kps ai config model <name>' should update active model."""
    save_ai_config({
        "provider": "openai",
        "api_base": "https://api.openai.com/v1",
        "api_key": "sk-mock",
        "model": "gpt-4o-mini",
    })

    plugin = AiPlugin()
    con = Console(file=StringIO(), legacy_windows=False)

    code = plugin.handle_ai(["config", "model", "gpt-4o"], console=con)
    assert code == 0

    loaded = load_ai_config()
    assert loaded["model"] == "gpt-4o"


def test_action_do_run(monkeypatch):
    """action_do generates command and executes on user confirmation."""
    mock_client = MagicMock()
    mock_client.chat_completion.return_value = "git status\n# info: Check working directory"

    con = Console(file=StringIO(), legacy_windows=False)
    # Simulate user pressing Enter (empty string = run)
    monkeypatch.setattr("builtins.input", lambda prompt="": "")

    mock_executor = MagicMock()
    mock_executor.execute.return_value = MagicMock(exit_code=0)

    code = action_do("show status", con, mock_client, executor=mock_executor)
    assert code == 0
    mock_executor.execute.assert_called_once_with("git status")


def test_action_do_copy(monkeypatch):
    """action_do copies to clipboard when user selects copy."""
    mock_client = MagicMock()
    mock_client.chat_completion.return_value = "docker ps\n# info: List containers"

    con = Console(file=StringIO(), legacy_windows=False)
    monkeypatch.setattr("builtins.input", lambda prompt="": "tab")

    with patch("plugins.ai.actions.copy_to_clipboard") as mock_clip:
        mock_clip.return_value = True
        code = action_do("list docker", con, mock_client)
        assert code == 0
        mock_clip.assert_called_once_with("docker ps")


def test_action_fix_with_failed_block(monkeypatch):
    """action_fix diagnoses the last failed block in BlockRegistry and prompts fix."""
    reg = get_block_registry()
    reg.add_block(
        command="npm run build",
        exit_code=1,
        duration_ms=120,
        cwd="C:/test",
        output_text="Error: missing module 'react'",
    )

    mock_client = MagicMock()
    mock_client.chat_completion.return_value = "Missing dependency react.\nFIX_CMD: npm install react"

    con = Console(file=StringIO(), legacy_windows=False)
    # Simulate user pressing enter to run fix
    monkeypatch.setattr("builtins.input", lambda prompt="": "")

    mock_executor = MagicMock()
    mock_executor.execute.return_value = MagicMock(exit_code=0)

    code = action_fix(con, mock_client, executor=mock_executor)
    assert code == 0
    mock_executor.execute.assert_called_once_with("npm install react")


def test_action_explain():
    """action_explain streams explanation for provided command."""
    mock_client = MagicMock()
    mock_client.chat_completion.return_value = "Dissecting tar: -c creates archive, -z compresses."

    out = StringIO()
    con = Console(file=out, legacy_windows=False)

    code = action_explain("tar -czvf test.tar.gz ./src", con, mock_client)
    assert code == 0
    mock_client.chat_completion.assert_called_once()


def test_action_pipe():
    """action_pipe summarizes stdin piped content."""
    mock_client = MagicMock()
    mock_client.chat_completion.return_value = "Summary: All tests passed."

    con = Console(file=StringIO(), legacy_windows=False)
    code = action_pipe("summarize", "test output line 1\ntest output line 2", con, mock_client)
    assert code == 0
    mock_client.chat_completion.assert_called_once()


def test_action_scout(tmp_path, monkeypatch):
    """action_scout reads manifests in cwd and summarizes."""
    (tmp_path / "package.json").write_text('{"name": "demo-app", "scripts": {"test": "jest"}}', encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    mock_client = MagicMock()
    mock_client.chat_completion.return_value = "Node.js app using Jest."

    con = Console(file=StringIO(), legacy_windows=False)
    code = action_scout(con, mock_client)
    assert code == 0
    mock_client.chat_completion.assert_called_once()
