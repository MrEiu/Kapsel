"""
Unit tests for Kapsel Upgrade & Plugin Switcher Systems.
Validates:
- Semver version string parsing and comparison
- Kapsel Core update checking with release notes parsing (GitHub/PyPI mock)
- Official plugin update checking with changelog extraction
- Targeted plugin upgrade ('kapsel upgrade <plugin_name>')
- Plugin enable and disable commands ('kapsel enable', 'kapsel disable')
- Backwards compatibility of catalog metadata parser
"""

from pathlib import Path
import sys
from unittest.mock import MagicMock, patch
import pytest
from rich.console import Console

# Ensure root directory is in sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from kapsel.completion.kps.builtins.upgrade import (
    _parse_semver,
    check_kapsel_core_update,
    check_plugins_update,
    handle_upgrade,
)
from kapsel.completion.kps.builtins.plugin_switch import (
    handle_enable_plugin,
    handle_disable_plugin,
)
from kapsel.core.plugin.catalog import (
    load_plugin_catalog,
    load_plugin_catalog_rich,
)


def test_parse_semver():
    """Verify semantic version string parsing."""
    assert _parse_semver("0.1.2") == (0, 1, 2)
    assert _parse_semver("v0.2.0") == (0, 2, 0)
    assert _parse_semver("1.0.0-beta") == (1, 0, 0)
    assert _parse_semver("0.2.0") > _parse_semver("0.1.2")
    assert _parse_semver("0.1.10") > _parse_semver("0.1.2")
    assert _parse_semver("0.1.0") == _parse_semver("v0.1.0")


def test_kapsel_core_update_detection():
    """Test detection of new Kapsel Core version and release notes."""
    # Scenario A: Newer version available on GitHub
    mock_gh_release = {
        "tag_name": "v9.9.9",
        "body": "Major release notes with new terminal features.",
        "published_at": "2026-09-05T12:00:00Z",
    }
    with patch("kapsel.completion.kps.builtins.upgrade._fetch_url_json", return_value=mock_gh_release):
        info = check_kapsel_core_update()
        assert info["has_update"] is True
        assert info["latest"] == "9.9.9"
        assert "Major release notes" in info["notes"]

    # Scenario B: Already at latest version
    with patch("kapsel.completion.kps.builtins.upgrade._fetch_url_json", return_value={"tag_name": "v0.0.1"}):
        info = check_kapsel_core_update()
        assert info["has_update"] is False


def test_check_plugins_update(tmp_path):
    """Test detection of plugin updates and changelog extraction."""
    mock_remote_catalog = {
        "shore": {
            "version": "0.3.0",
            "description": "Fast mirror switcher",
            "changelog": "Added 30+ new mirror sources and speed test benchmarks.",
        },
        "alias": {
            "version": "0.2.0",
            "description": "Cross-platform alias mapper",
            "changelog": "Added Ultra Modern CLI toolchain.",
        },
    }

    # Simulate installed shore plugin with version 0.1.0
    shore_dir = tmp_path / "plugins" / "shore"
    shore_dir.mkdir(parents=True, exist_ok=True)
    (shore_dir / "plugin.py").write_text('version = "0.1.0"\n', encoding="utf-8")

    with patch("kapsel.completion.kps.builtins.upgrade.fetch_remote_plugin_catalog", return_value=mock_remote_catalog):
        with patch("kapsel.completion.kps.builtins.upgrade.get_kapsel_dir", return_value=tmp_path):
            updates = check_plugins_update()
            shore_update = next((u for u in updates if u["name"] == "shore"), None)
            assert shore_update is not None
            assert shore_update["has_update"] is True
            assert shore_update["current"] == "0.1.0"
            assert shore_update["latest"] == "0.3.0"
            assert "Added 30+ new mirror sources" in shore_update["changelog"]


def test_handle_upgrade_targeted_plugin(tmp_path):
    """Test 'kapsel upgrade <plugin>' with changelog display."""
    mock_remote_catalog = {
        "shore": {
            "version": "0.2.0",
            "description": "Fast mirror switcher",
            "changelog": "Performance improvements and mirror testing.",
        }
    }

    # Setup local shore plugin
    shore_dir = tmp_path / "plugins" / "shore"
    shore_dir.mkdir(parents=True, exist_ok=True)
    (shore_dir / "plugin.py").write_text('version = "0.1.0"\n', encoding="utf-8")

    con = Console(record=True)
    with patch("kapsel.completion.kps.builtins.upgrade.fetch_remote_plugin_catalog", return_value=mock_remote_catalog):
        with patch("kapsel.completion.kps.builtins.upgrade.get_kapsel_dir", return_value=tmp_path):
            with patch("kapsel.completion.kps.builtins.upgrade.fetch_plugin_from_remote", return_value=True):
                # 1. Check-only mode
                ret = handle_upgrade(["shore", "--check"], con)
                assert ret == 0
                out = con.export_text()
                assert "Plugin Update Available" in out
                assert "0.1.0" in out
                assert "0.2.0" in out
                assert "Performance improvements" in out

                # 2. Actual upgrade mode
                ret = handle_upgrade(["shore"], con)
                assert ret == 0


def test_handle_upgrade_full_flow():
    """Test full 'kapsel upgrade --check' inspecting both Kapsel Core and plugins."""
    con = Console(record=True)
    with patch("kapsel.completion.kps.builtins.upgrade.check_kapsel_core_update", return_value={
        "has_update": False,
        "current": "0.1.2",
        "latest": "0.1.2",
        "notes": "",
        "published_at": "",
    }):
        with patch("kapsel.completion.kps.builtins.upgrade.check_plugins_update", return_value=[]):
            ret = handle_upgrade(["--check"], con)
            assert ret == 0
            out = con.export_text()
            assert "Kapsel Core is up to date" in out


def test_handle_enable_and_disable_plugin(tmp_path):
    """Test 'kapsel enable <plugin>' and 'kapsel disable <plugin>' commands."""
    con = Console(record=True)
    test_plugin = "mytool"

    # Simulate installed plugin directory
    tool_dir = tmp_path / "plugins" / test_plugin
    tool_dir.mkdir(parents=True, exist_ok=True)
    (tool_dir / "__init__.py").write_text("# init", encoding="utf-8")
    (tool_dir / "plugin.py").write_text('version = "0.1.0"\n', encoding="utf-8")

    with patch("kapsel.completion.kps.builtins.plugin_switch.get_kapsel_dir", return_value=tmp_path):
        with patch("kapsel.completion.kps.builtins.plugin_switch.update_config_value") as mock_update:
            # 1. Enable plugin
            with patch("kapsel.completion.kps.builtins.plugin_switch.load_config") as mock_cfg:
                mock_cfg.return_value.enabled_plugins = ["other"]
                ret = handle_enable_plugin([test_plugin], con)
                assert ret == 0
                mock_update.assert_called_with("plugins", "enabled", ["other", test_plugin])

            # 2. Disable plugin with explicit list
            with patch("kapsel.completion.kps.builtins.plugin_switch.load_config") as mock_cfg:
                mock_cfg.return_value.enabled_plugins = [test_plugin, "other"]
                ret = handle_disable_plugin([test_plugin], con)
                assert ret == 0
                mock_update.assert_called_with("plugins", "enabled", ["other"])

            # 3. Disable plugin when enabled_plugins is empty (implicit all enabled)
            with patch("kapsel.completion.kps.builtins.plugin_switch.load_config") as mock_cfg:
                mock_cfg.return_value.enabled_plugins = []
                with patch("kapsel.completion.kps.builtins.plugin_switch.get_all_installed_plugins", return_value=[test_plugin, "other"]):
                    ret = handle_disable_plugin([test_plugin], con)
                    assert ret == 0
                    mock_update.assert_called_with("plugins", "enabled", ["other"])


def test_builtins_registration_and_subcommands():
    """Verify upgrade, update, enable, and disable are registered with subcommands."""
    from kapsel.completion.kps.registry import KpsCommandRegistry
    from kapsel.completion.kps.builtins import register_builtins

    reg = KpsCommandRegistry()
    register_builtins(reg)

    for cmd_name in ["upgrade", "enable", "disable"]:
        cmd = reg.get_system_command(cmd_name)
        assert cmd is not None, f"Command '{cmd_name}' must be registered"
        assert cmd.subcommands is not None
        assert "alias" in cmd.subcommands
        assert "shore" in cmd.subcommands


def test_catalog_rich_loading_backwards_compatibility():
    """Verify load_plugin_catalog and load_plugin_catalog_rich return expected schemas."""
    # 1. Flat dictionary backwards compatibility (mapping ID -> str)
    flat = load_plugin_catalog()
    assert isinstance(flat, dict)
    assert "alias" in flat
    assert isinstance(flat["alias"], str)

    # 2. Rich dictionary (mapping ID -> {version, description, changelog})
    rich = load_plugin_catalog_rich()
    assert isinstance(rich, dict)
    assert "alias" in rich
    assert isinstance(rich["alias"], dict)
    assert "version" in rich["alias"]
    assert "description" in rich["alias"]
    assert "changelog" in rich["alias"]
    assert rich["alias"]["version"] == "0.2.1"
