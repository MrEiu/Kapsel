"""
Unit tests for Kapsel Alias Plugin.
Validates:
- Direct interactive shell command translation (rm, cat, touch, ll, etc.)
- Strict preservation of the `kps` / `kapsel` namespace (never intercepting kps commands)
- Multi-platform alias template resolution and storage
- Progressive modern tool engine enhancement (bat, eza, rg, etc.) with host shell fallback
- CLI subcommands (list, add, remove, reset, ultra)
"""

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

# Ensure root directory is in sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from plugins.alias.plugin import AliasPlugin
from plugins.alias.defaults import get_default_aliases, ULTRA_TOOLS
from kapsel.core.plugin.context import PluginContext


@pytest.fixture
def temp_alias_plugin(tmp_path):
    plugin = AliasPlugin()
    context = MagicMock()
    context.plugin_data_dir = tmp_path / "alias_test_data"
    context.environment.current_shell = "pwsh"
    plugin.on_load(context)
    return plugin


def test_alias_manifest(temp_alias_plugin):
    manifest = temp_alias_plugin.manifest
    assert manifest.id == "alias"
    assert manifest.name == "Alias"
    assert "cross-platform" in manifest.tags
    assert "ultra" in manifest.tags


def test_default_aliases_population(temp_alias_plugin):
    # Should have at least 35 baseline commands loaded
    assert len(temp_alias_plugin.mappings) >= 35
    alias_names = {m["alias"] for m in temp_alias_plugin.mappings}
    assert "cat" in alias_names
    assert "rm" in alias_names
    assert "touch" in alias_names
    assert "ll" in alias_names
    assert "grep" in alias_names
    assert "ps" in alias_names


def test_kps_and_kapsel_namespace_never_intercepted(temp_alias_plugin):
    """Ensure kps and kapsel commands are NEVER intercepted by alias filter."""
    # kps commands must pass through untouched
    handled, cmd = temp_alias_plugin.filter_command("kps touch myfile.txt")
    assert not handled
    assert cmd == "kps touch myfile.txt"

    handled, cmd = temp_alias_plugin.filter_command("kps cat config.json")
    assert not handled
    assert cmd == "kps cat config.json"

    handled, cmd = temp_alias_plugin.filter_command("kps rm -rf temp")
    assert not handled
    assert cmd == "kps rm -rf temp"

    handled, cmd = temp_alias_plugin.filter_command("kapsel rm test")
    assert not handled
    assert cmd == "kapsel rm test"


def test_direct_command_translation_interactive(temp_alias_plugin):
    """Direct typing in interactive shell should be translated properly."""
    temp_alias_plugin.current_shell = "pwsh"

    # Test touch
    with patch("shutil.which", return_value=None):
        handled, translated = temp_alias_plugin.filter_command("touch main.py")
        assert handled
        assert "New-Item" in translated
        assert "main.py" in translated

    # Test cat with modern tool fallback vs present
    with patch("shutil.which", return_value=None):
        handled, translated = temp_alias_plugin.filter_command("cat package.json")
        assert handled
        assert "Get-Content" in translated
        assert "package.json" in translated

    with patch("shutil.which", side_effect=lambda x: "C:\\bin\\bat.exe" if x == "bat" else None):
        handled, translated = temp_alias_plugin.filter_command("cat package.json")
        assert handled
        assert "bat" in translated
        assert "package.json" in translated


def test_alias_add_and_remove(temp_alias_plugin):
    """Test adding custom multi-platform alias and removing it."""
    temp_alias_plugin.current_shell = "pwsh"

    # 1. Add single-platform
    code = temp_alias_plugin.handle_alias([
        "add", "mybuild", "npm run build --mode {{args}}",
        "-p", "pwsh",
        "--desc", "Build production artifacts"
    ])
    assert code == 0
    entry = next((m for m in temp_alias_plugin.mappings if m["alias"] == "mybuild"), None)
    assert entry is not None
    assert entry.get("templates", {}).get("pwsh") == "npm run build --mode {{args}}"

    # 2. Add universal platform alias
    code = temp_alias_plugin.handle_alias([
        "add", "echohello", "echo Hello World {{args}}",
        "-p", "universal",
        "--desc", "Echo greeting"
    ])
    assert code == 0
    echo_entry = next((m for m in temp_alias_plugin.mappings if m["alias"] == "echohello"), None)
    assert echo_entry is not None
    assert echo_entry["templates"]["universal"] == "echo Hello World {{args}}"

    # Verify resolution in pwsh
    handled, translated = temp_alias_plugin.filter_command("echohello John")
    assert handled
    assert translated == "echo Hello World John"

    # 3. Remove specific platform
    code = temp_alias_plugin.handle_alias(["remove", "mybuild", "-p", "pwsh"])
    assert code == 0
    assert not any(m["alias"] == "mybuild" for m in temp_alias_plugin.mappings)

    # 4. Remove entire alias
    code = temp_alias_plugin.handle_alias(["remove", "echohello"])
    assert code == 0
    assert not any(m["alias"] == "echohello" for m in temp_alias_plugin.mappings)


def test_alias_list_output(temp_alias_plugin):
    """Test kps alias list executes cleanly."""
    code = temp_alias_plugin.handle_alias(["list"])
    assert code == 0


def test_alias_reset(temp_alias_plugin):
    """Test kps alias reset restores defaults."""
    # Add dummy alias
    temp_alias_plugin.mappings.append({"alias": "custom_dummy", "desc": "test", "templates": {"universal": "echo dummy"}})
    assert any(m["alias"] == "custom_dummy" for m in temp_alias_plugin.mappings)

    code = temp_alias_plugin.handle_alias(["reset"])
    assert code == 0
    assert not any(m["alias"] == "custom_dummy" for m in temp_alias_plugin.mappings)
    assert any(m["alias"] == "cat" for m in temp_alias_plugin.mappings)


def test_alias_ultra_dry_run(temp_alias_plugin):
    """Test kps alias ultra --dry-run prints installation plan without executing."""
    code = temp_alias_plugin.handle_alias(["ultra", "--dry-run"])
    assert code == 0


def test_ultra_tools_catalog_completeness():
    """Verify ULTRA_TOOLS catalog contains key modern command line tools."""
    tool_names = {t["name"] for t in ULTRA_TOOLS}
    expected = {"eza", "bat", "ripgrep", "fd", "procs", "dust", "bottom", "gping", "jq", "sd", "lazygit", "hyperfine"}
    assert expected.issubset(tool_names)
