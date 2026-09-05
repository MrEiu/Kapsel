"""
Unit tests for Carapace Spec Manager and 'kps completion' management suite.
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

from kapsel.completion.spec_manager import (
    CarapaceSpecManager,
    SpecInfo,
    _compute_file_hash,
    _parse_spec_metadata,
    get_carapace_specs_dir,
    get_user_specs_dir,
)
from kapsel.completion.kps.builtins.completion import handle_completion


@pytest.fixture
def temp_spec_env(tmp_path):
    kapsel_dir = tmp_path / "kapsel_data"
    carapace_dir = tmp_path / "carapace_specs"
    kapsel_dir.mkdir()
    carapace_dir.mkdir()

    mgr = CarapaceSpecManager(kapsel_dir=kapsel_dir, carapace_dir=carapace_dir)
    return mgr, kapsel_dir, carapace_dir


def test_get_spec_directories():
    carapace_dir = get_carapace_specs_dir()
    assert isinstance(carapace_dir, Path)
    assert carapace_dir.exists()

    user_dir = get_user_specs_dir()
    assert isinstance(user_dir, Path)
    assert user_dir.exists()


def test_parse_spec_metadata(tmp_path):
    spec_file = tmp_path / "mytool.yaml"
    spec_file.write_text(
        """
name: custom-tool
description: "My custom development tool"
aliases: ["ct", "ctool"]
flags:
  -h, --help: "Show help"
""",
        encoding="utf-8",
    )

    name, desc, aliases = _parse_spec_metadata(spec_file)
    assert name == "custom-tool"
    assert desc == "My custom development tool"
    assert "ct" in aliases
    assert "ctool" in aliases


def test_discover_specs_hierarchy(temp_spec_env, tmp_path):
    mgr, kapsel_dir, carapace_dir = temp_spec_env

    # 1. Create a plugin directory with spec.yaml
    plugin_root = tmp_path / "plugins"
    demo_plugin = plugin_root / "demo"
    demo_plugin.mkdir(parents=True)
    (demo_plugin / "spec.yaml").write_text(
        """
name: demo
description: "Demo plugin spec"
""",
        encoding="utf-8",
    )

    # 2. Create another plugin that will be overridden by user
    override_plugin = plugin_root / "portal"
    override_plugin.mkdir(parents=True)
    (override_plugin / "spec.yaml").write_text(
        """
name: portal
description: "Plugin portal spec"
""",
        encoding="utf-8",
    )

    # 3. Create user spec for portal (should override plugin)
    (mgr.user_specs_dir / "portal.yaml").write_text(
        """
name: portal
description: "User customized portal spec"
""",
        encoding="utf-8",
    )

    discovered = mgr.discover_specs(plugin_dirs=[plugin_root], enabled_plugins=["demo", "portal"])
    assert "demo" in discovered
    assert discovered["demo"].source_type == "plugin"
    assert discovered["demo"].description == "Demo plugin spec"

    assert "portal" in discovered
    # User layer must take precedence!
    assert discovered["portal"].source_type == "user"
    assert discovered["portal"].description == "User customized portal spec"
    assert discovered["portal"].is_overridden is True


def test_sync_specs_incremental(temp_spec_env):
    mgr, kapsel_dir, carapace_dir = temp_spec_env

    # Write user spec
    (mgr.user_specs_dir / "alpha.yaml").write_text("name: alpha\ndescription: Alpha tool\n", encoding="utf-8")

    # First sync: should copy kps.yaml, kapsel.yaml, and alpha.yaml (3 files)
    synced, skipped = mgr.sync_specs(plugin_dirs=[])
    assert synced == 3
    assert skipped == 0
    target = carapace_dir / "alpha.yaml"
    assert target.exists()
    assert (carapace_dir / "kps.yaml").exists()
    assert (carapace_dir / "kapsel.yaml").exists()
    assert "Alpha tool" in target.read_text(encoding="utf-8")

    # Second sync without changes: should skip all 3
    synced, skipped = mgr.sync_specs(plugin_dirs=[])
    assert synced == 0
    assert skipped == 3

    # Modify source: should re-sync alpha.yaml, kps.yaml, and kapsel.yaml
    (mgr.user_specs_dir / "alpha.yaml").write_text("name: alpha\ndescription: Updated Alpha\n", encoding="utf-8")
    synced, skipped = mgr.sync_specs(plugin_dirs=[])
    assert synced == 3
    assert skipped == 0
    assert "Updated Alpha" in target.read_text(encoding="utf-8")


def test_collision_sentinel_blocks_reserved_commands(temp_spec_env, tmp_path):
    mgr, kapsel_dir, carapace_dir = temp_spec_env

    # 1. Plugin with reserved name 'alias' and standalone: true attempt
    plugin_root = tmp_path / "plugins"
    alias_plugin = plugin_root / "alias"
    alias_plugin.mkdir(parents=True)
    (alias_plugin / "spec.yaml").write_text(
        """
name: alias
standalone: true
description: "Alias plugin"
""",
        encoding="utf-8",
    )

    # Sync
    synced, skipped = mgr.sync_specs(plugin_dirs=[plugin_root], enabled_plugins=["alias"])

    # CRITICAL: alias.yaml MUST NOT exist in carapace_dir to protect host shell
    assert not (carapace_dir / "alias.yaml").exists()

    # But alias MUST exist as a subcommand in kps.yaml and kapsel.yaml
    kps_content = (carapace_dir / "kps.yaml").read_text(encoding="utf-8")
    assert "name: alias" in kps_content
    assert "Alias plugin" in kps_content


def test_create_template(temp_spec_env):
    mgr, kapsel_dir, carapace_dir = temp_spec_env
    path = mgr.create_template("awesome", "An awesome new CLI tool")
    assert path.exists()
    content = path.read_text(encoding="utf-8")
    assert "name: awesome" in content
    assert "An awesome new CLI tool" in content
    assert "commands:" in content

    # Should also have synced to carapace directory
    assert (carapace_dir / "awesome.yaml").exists()


def test_handle_completion_cli(temp_spec_env):
    mgr, kapsel_dir, carapace_dir = temp_spec_env
    console = Console(record=True)

    with patch("kapsel.completion.kps.builtins.completion.CarapaceSpecManager", return_value=mgr):
        # 1. Help
        code_help = handle_completion(["--help"], console)
        assert code_help == 0
        assert "kps completion" in console.export_text()

        # 2. Path
        console = Console(record=True)
        code_path = handle_completion(["path"], console)
        assert code_path == 0
        assert "Completion Spec Directories" in console.export_text()

        # 3. New
        console = Console(record=True)
        code_new = handle_completion(["new", "foobar", "Foo Bar description"], console)
        assert code_new == 0
        assert (mgr.user_specs_dir / "foobar.yaml").exists()

        # 4. List
        console = Console(record=True)
        code_ls = handle_completion(["ls"], console)
        assert code_ls == 0
        out_ls = console.export_text()
        assert "foobar" in out_ls
        assert "Declarative Completion Specifications" in out_ls

        # 5. Sync
        console = Console(record=True)
        code_sync = handle_completion(["sync"], console)
        assert code_sync == 0
        assert "Synchronizing completion specifications" in console.export_text()
