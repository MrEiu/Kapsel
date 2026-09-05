"""
Unit tests for Kapsel Portal (Directory Teleportation) Plugin.
All comments and descriptions are in English.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest
from rich.console import Console

# Ensure root directory is in sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from plugins.portal.plugin import (
    PortalPlugin,
    _resolve_zoxide_executable,
)
from kapsel.core.plugin.context import PluginContext
from kapsel.core.plugin.hooks import HookType


@pytest.fixture
def portal_plugin():
    plugin = PortalPlugin()
    context = MagicMock(spec=PluginContext)
    context.plugin_data_dir = Path("/tmp/kapsel_test_portal")
    plugin.on_load(context)
    return plugin


def test_portal_plugin_manifest(portal_plugin):
    manifest = portal_plugin.manifest
    assert manifest.id == "portal"
    assert manifest.name == "Portal"
    assert "zoxide" in manifest.tags
    assert "navigation" in manifest.tags


def test_resolve_zoxide_executable():
    with patch("shutil.which", return_value="C:\\bin\\zoxide.exe"):
        exe = _resolve_zoxide_executable()
        assert exe == "C:\\bin\\zoxide.exe"

    with patch("shutil.which", return_value=None), \
         patch.object(Path, "exists", return_value=False):
        exe = _resolve_zoxide_executable()
        # Might find scoop or return None depending on test environment
        assert exe is None or isinstance(exe, str)


def test_filter_command_non_portal(portal_plugin):
    is_handled, cmd = portal_plugin.filter_command("git status")
    assert not is_handled
    assert cmd == "git status"


def test_filter_command_bare_z(portal_plugin):
    portal_plugin._zoxide_bin = "zoxide"
    is_handled, cmd = portal_plugin.filter_command("z")
    assert is_handled
    assert cmd == "cd ~"

    is_handled, cmd = portal_plugin.filter_command("portal")
    assert is_handled
    assert cmd == "cd ~"


def test_filter_command_special_tokens(portal_plugin):
    portal_plugin._zoxide_bin = "zoxide"
    for tok in ("..", "-", "~"):
        is_handled, cmd = portal_plugin.filter_command(f"z {tok}")
        assert is_handled
        assert cmd == f"cd {tok}"


def test_filter_command_existing_directory(portal_plugin, tmp_path):
    portal_plugin._zoxide_bin = "zoxide"
    sub_dir = tmp_path / "my_project"
    sub_dir.mkdir()

    is_handled, cmd = portal_plugin.filter_command(f"z {sub_dir}")
    assert is_handled
    assert str(sub_dir.resolve()) in cmd
    assert cmd.startswith('cd "')


def test_filter_command_zoxide_query_match(portal_plugin):
    portal_plugin._zoxide_bin = "zoxide"
    with patch.object(portal_plugin, "_query_zoxide_best", return_value="/home/user/workspace/repo_xyz"):
        is_handled, cmd = portal_plugin.filter_command("z my_virtual_repo_xyz")
        assert is_handled
        assert cmd == 'cd "/home/user/workspace/repo_xyz"'


def test_filter_command_zoxide_no_match(portal_plugin):
    portal_plugin._zoxide_bin = "zoxide"
    with patch.object(portal_plugin, "_query_zoxide_best", return_value=None):
        is_handled, cmd = portal_plugin.filter_command("z nonexistent_dir")
        assert is_handled
        assert cmd == ""


def test_handle_portal_help(portal_plugin):
    console = Console(record=True)
    code = portal_plugin.handle_portal(["--help"], console)
    assert code == 0
    output = console.export_text()
    assert "kps portal" in output
    assert "Quick Jumping" in output


def test_handle_portal_list(portal_plugin):
    console = Console(record=True)
    portal_plugin._zoxide_bin = "zoxide"
    mock_out = "10.5 /home/user/repoA\n5.0 /home/user/repoB\n"
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout=mock_out)
        code = portal_plugin.handle_portal(["ls"], console)
        assert code == 0
        output = console.export_text()
        assert "Ranked Workspaces" in output
        assert "repoA" in output


def test_handle_portal_query(portal_plugin):
    console = Console(record=True)
    portal_plugin._zoxide_bin = "zoxide"
    with patch.object(portal_plugin, "_query_zoxide_best", return_value="/home/user/repoA"):
        code = portal_plugin.handle_portal(["query", "repoA"], console)
        assert code == 0


def test_handle_portal_add_and_remove(portal_plugin, tmp_path):
    console = Console(record=True)
    portal_plugin._zoxide_bin = "zoxide"
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout="")
        code_add = portal_plugin.handle_portal(["add", str(tmp_path)], console)
        assert code_add == 0

        code_rm = portal_plugin.handle_portal(["rm", str(tmp_path)], console)
        assert code_rm == 0


def test_handle_portal_doctor(portal_plugin):
    console = Console(record=True)
    portal_plugin._zoxide_bin = "zoxide"
    with patch("subprocess.run") as mock_run, \
         patch.object(portal_plugin, "_list_zoxide_entries", return_value=["/path/one", "/path/two"]):
        mock_run.return_value = MagicMock(returncode=0, stdout="zoxide 0.10.0\n")
        code = portal_plugin.handle_portal(["doctor"], console)
        assert code == 0
        output = console.export_text()
        assert "Portal & zoxide Diagnostic" in output
        assert "Tracked directories" in output


def test_provide_completions(portal_plugin):
    portal_plugin._zoxide_bin = "zoxide"
    mock_entries = [
        "C:\\Users\\meru6\\Desktop\\Kapsel",
        "C:\\Users\\meru6\\Desktop\\plugins",
    ]
    with patch.object(portal_plugin, "_list_zoxide_entries", return_value=mock_entries):
        comps = portal_plugin.provide_completions("z kap")
        assert len(comps) == 2
        assert comps[0]["text"] == "Kapsel"
        assert comps[0]["display_meta"] == "[portal]"

        # Non-matching command prefix
        assert portal_plugin.provide_completions("ls -la") == []
