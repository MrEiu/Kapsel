import sys
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

# Ensure root directory is in sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from plugins.init.plugin import InitPlugin, _resolve_mise_executable, _run_mise_command
from kapsel.core.plugin.context import PluginContext
from rich.console import Console


def test_init_plugin_manifest():
    """Verify plugin manifest fields."""
    plugin = InitPlugin()
    assert plugin.manifest.id == "init"
    assert plugin.manifest.name == "Init"
    assert "mise" in plugin.manifest.dependencies


def test_resolve_mise_executable():
    """Verify that mise executable can be resolved if installed in PATH or system."""
    with patch("shutil.which", return_value="/usr/local/bin/mise"):
        path = _resolve_mise_executable()
        assert path == "/usr/local/bin/mise"


def test_handle_init_default_install():
    """Verify bare 'kps init' maps directly to 'mise install'."""
    plugin = InitPlugin()
    con = Console(record=True)
    with patch("plugins.init.plugin._run_mise_command") as mock_run:
        mock_run.return_value = 0
        ret = plugin.handle_init([], con)
        assert ret == 0
        mock_run.assert_called_once_with(["install"], con)


def test_handle_init_specific_tool_install():
    """Verify 'kps init node@22' maps to 'mise install node@22'."""
    plugin = InitPlugin()
    con = Console(record=True)
    with patch("plugins.init.plugin._run_mise_command") as mock_run:
        mock_run.return_value = 0
        ret = plugin.handle_init(["node@22"], con)
        assert ret == 0
        mock_run.assert_called_once_with(["install", "node@22"], con)


def test_handle_init_subcommands():
    """Verify subcommands (use, ls, list, current, doctor, upgrade) are forwarded properly."""
    plugin = InitPlugin()
    con = Console(record=True)

    # 1. 'kps init use python@3.12'
    with patch("plugins.init.plugin._run_mise_command") as mock_run:
        mock_run.return_value = 0
        ret = plugin.handle_init(["use", "python@3.12"], con)
        assert ret == 0
        mock_run.assert_called_once_with(["use", "python@3.12"], con)

    # 2. 'kps init list' aliases to 'mise ls'
    with patch("plugins.init.plugin._run_mise_command") as mock_run:
        mock_run.return_value = 0
        ret = plugin.handle_init(["list"], con)
        assert ret == 0
        mock_run.assert_called_once_with(["ls"], con)

    # 3. 'kps init current'
    with patch("plugins.init.plugin._run_mise_command") as mock_run:
        mock_run.return_value = 0
        ret = plugin.handle_init(["current"], con)
        assert ret == 0
        mock_run.assert_called_once_with(["current"], con)

    # 4. 'kps init doctor'
    with patch("plugins.init.plugin._run_mise_command") as mock_run:
        mock_run.return_value = 0
        ret = plugin.handle_init(["doctor"], con)
        assert ret == 0
        mock_run.assert_called_once_with(["doctor"], con)


def test_handle_init_help():
    """Verify 'kps init --help' renders usage instructions without executing mise."""
    plugin = InitPlugin()
    con = Console(record=True)
    with patch("plugins.init.plugin._run_mise_command") as mock_run:
        ret = plugin.handle_init(["--help"], con)
        assert ret == 0
        assert not mock_run.called
        output = con.export_text()
        assert "Kapsel Project Environment Initializer" in output
        assert "mise install" in output


def test_provide_completions():
    """Verify auto-completions offer subcommands and popular tools."""
    plugin = InitPlugin()
    # 1. 'kps init ' offers use, ls, node, python, etc.
    cands = plugin.provide_completions("kps init ")
    texts = [c["text"] for c in cands]
    assert "use" in texts
    assert "ls" in texts
    assert "node" in texts
    assert "python" in texts

    # 2. 'kps init no' filters to node
    cands_prefix = plugin.provide_completions("kps init no")
    texts_prefix = [c["text"] for c in cands_prefix]
    assert "node" in texts_prefix
    assert "python" not in texts_prefix
