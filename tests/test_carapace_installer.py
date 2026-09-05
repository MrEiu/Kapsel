"""
Unit tests for Carapace completion engine auto-installer and command handlers.
"""

from unittest.mock import MagicMock, patch
import pytest

from kapsel.completion.carapace_installer import (
    DEFAULT_CARAPACE_VERSION,
    detect_platform_and_arch,
    install_carapace,
)
from kapsel.completion.kps.builtins.add import handle_add_command
from kapsel.completion.kps.registry import get_kps_registry


def test_detect_platform_and_arch():
    """Verifies that platform and architecture detection succeeds on the current runner."""
    os_name, arch_name, ext = detect_platform_and_arch()
    assert os_name in ("windows", "darwin", "linux")
    assert arch_name in ("amd64", "arm64", "386", "armv6")
    assert ext in ("zip", "tar.gz")


def test_install_carapace_already_available():
    """When Carapace is already installed and not forced, installer exits cleanly with True."""
    mock_engine = MagicMock()
    mock_engine.is_available.return_value = True
    mock_engine.executable = "/usr/local/bin/carapace"

    with patch("kapsel.completion.carapace_engine.get_carapace_engine", return_value=mock_engine):
        res = install_carapace(force=False)
        assert res is True


def test_kps_add_carapace_dispatches_installer():
    """Verifies that 'kps add carapace' routes to install_carapace."""
    with patch("kapsel.completion.carapace_installer.install_carapace", return_value=True) as mock_install:
        ret = handle_add_command(["carapace"])
        assert ret == 0
        mock_install.assert_called_once()


def test_kps_registry_has_install_carapace():
    """Verifies that install-carapace is registered in KpsCommandRegistry."""
    reg = get_kps_registry()
    cmd = reg.get("install-carapace")
    assert cmd is not None
    assert "Carapace" in cmd.help_text
