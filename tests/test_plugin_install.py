import sys
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest
from rich.console import Console

# Ensure root directory is in sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from plugins.install.plugin import (
    InstallPlugin,
    _detect_installed_managers,
    _sort_managers_by_platform,
    _get_current_platform_key,
    _resolve_mpm_executable,
)
from kapsel.core.plugin.context import PluginContext


def test_install_plugin_manifest():
    """Verify plugin manifest fields."""
    plugin = InstallPlugin()
    assert plugin.manifest.id == "install"
    assert plugin.manifest.name == "Install"
    assert "meta-package-manager" in plugin.manifest.dependencies


def test_sort_managers_windows_priority():
    """Verify Windows platform puts winget and scoop before language managers."""
    detected = ["npm", "pip", "uv", "winget", "cargo", "scoop"]
    sorted_managers = _sort_managers_by_platform(detected, "windows")

    # scoop and winget should come before uv, cargo, npm, pip
    assert sorted_managers.index("scoop") < sorted_managers.index("winget")
    assert sorted_managers.index("winget") < sorted_managers.index("uv")
    assert sorted_managers.index("uv") < sorted_managers.index("cargo")
    assert sorted_managers.index("cargo") < sorted_managers.index("npm")
    assert sorted_managers.index("npm") < sorted_managers.index("pip")


def test_sort_managers_macos_priority():
    """Verify macOS platform puts brew and mas first."""
    detected = ["pip", "mas", "cargo", "brew", "uv"]
    sorted_managers = _sort_managers_by_platform(detected, "macos")

    assert sorted_managers[0] == "brew"
    assert sorted_managers[1] == "mas"
    assert sorted_managers[2] == "uv"
    assert sorted_managers[3] == "cargo"
    assert sorted_managers[4] == "pip"


def test_sort_managers_linux_arch_priority():
    """Verify Arch Linux puts pacman and yay/paru before sandboxes and language tools."""
    detected = ["flatpak", "uv", "pacman", "yay", "npm"]
    sorted_managers = _sort_managers_by_platform(detected, "linux_arch")

    assert sorted_managers[0] == "pacman"
    assert sorted_managers[1] == "yay"
    assert sorted_managers[2] == "flatpak"
    assert sorted_managers[3] == "uv"
    assert sorted_managers[4] == "npm"


def test_sort_managers_linux_debian_priority():
    """Verify Debian / Ubuntu puts apt before snap/flatpak and language tools."""
    detected = ["snap", "uv", "apt", "flatpak"]
    sorted_managers = _sort_managers_by_platform(detected, "linux_debian")

    assert sorted_managers[0] == "apt"
    assert sorted_managers[1] == "snap"
    assert sorted_managers[2] == "flatpak"
    assert sorted_managers[3] == "uv"


def test_config_generation_and_persistence(tmp_path):
    """Verify config auto-generation and saving to disk."""
    plugin = InstallPlugin()
    mock_context = MagicMock()
    mock_context.plugin_data_dir = tmp_path
    plugin.context = mock_context

    # Mock detection on windows
    with patch("plugins.install.plugin._detect_installed_managers", return_value=["winget", "scoop", "pip", "uv"]):
        with patch("plugins.install.plugin._get_current_platform_key", return_value="windows"):
            conf = plugin.load_config(force_refresh=True)

    assert conf["platform"] == "windows"
    assert conf["managers"] == ["scoop", "winget", "uv"]
    assert "pip" in conf["disabled"]

    config_file = tmp_path / "config.yaml"
    assert config_file.is_file()

    # Re-reading should match without generating anew
    cached = plugin.load_config()
    assert cached["managers"] == ["scoop", "winget", "uv"]


def test_user_custom_order_respected(tmp_path):
    """Verify that manual user reordering in config.yaml is honored."""
    plugin = InstallPlugin()
    mock_context = MagicMock()
    mock_context.plugin_data_dir = tmp_path
    plugin.context = mock_context

    # Manually write user preference where scoop is preferred over winget
    config_file = tmp_path / "config.yaml"
    config_file.write_text(
        """
platform: windows
managers:
  - scoop
  - winget
  - uv
disabled:
  - choco
""",
        encoding="utf-8",
    )

    active = plugin.get_active_managers()
    assert active == ["scoop", "winget", "uv"]


def test_inject_priority_args(tmp_path):
    """Verify priority flags are injected into mpm argument list."""
    plugin = InstallPlugin()
    mock_context = MagicMock()
    mock_context.plugin_data_dir = tmp_path
    plugin.context = mock_context

    with patch.object(plugin, "get_active_managers", return_value=["winget", "scoop", "uv"]):
        # 1. Bare package name: should inject ordered flags
        injected = plugin._inject_priority_args(["curl"])
        assert injected == ["--winget", "--scoop", "--uv", "curl"]

        # 2. Explicit manager passed by user: should NOT override or duplicate
        explicit = plugin._inject_priority_args(["--scoop", "curl"])
        assert explicit == ["--scoop", "curl"]

        # 3. Explicit --manager selector
        explicit_m = plugin._inject_priority_args(["--manager", "choco", "curl"])
        assert explicit_m == ["--manager", "choco", "curl"]


def test_handle_install_subcommands(tmp_path):
    """Verify --order, --detect, and --config subcommands."""
    plugin = InstallPlugin()
    mock_context = MagicMock()
    mock_context.plugin_data_dir = tmp_path
    plugin.context = mock_context

    con = Console(record=True)

    with patch("plugins.install.plugin._detect_installed_managers", return_value=["winget", "scoop"]):
        with patch("plugins.install.plugin._get_current_platform_key", return_value="windows"):
            # 1. --order
            ret = plugin.handle_install(["--order"], con)
            assert ret == 0
            out = con.export_text()
            assert "Package Manager Priority Order" in out
            assert "winget" in out
            assert "scoop" in out

            # 2. --detect
            con = Console(record=True)
            ret = plugin.handle_install(["--detect"], con)
            assert ret == 0
            out = con.export_text()
            assert "Rescanning system package managers" in out
            assert "updated successfully" in out

            # 3. --config
            con = Console(record=True)
            ret = plugin.handle_install(["--config"], con)
            assert ret == 0
            out = con.export_text()
            assert "config.yaml" in out

            # 4. --help
            con = Console(record=True)
            ret = plugin.handle_install(["--help"], con)
            assert ret == 0
            out = con.export_text()
            assert "kps install <package_name>" in out


def test_handle_install_forwarding():
    """Verify 'kps install curl' forwards to mpm with ordered flags."""
    plugin = InstallPlugin()
    con = Console(record=True)

    with patch.object(plugin, "_inject_priority_args", return_value=["--winget", "--scoop", "curl"]):
        with patch("plugins.install.plugin._run_mpm_command") as mock_run:
            mock_run.return_value = 0
            ret = plugin.handle_install(["curl"], con)
            assert ret == 0
            mock_run.assert_called_once_with("install", ["--winget", "--scoop", "curl"], con)
