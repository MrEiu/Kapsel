"""
Unit tests for Kapsel remote plugin fetcher and add command integration.
"""

from pathlib import Path
import tempfile
from unittest.mock import MagicMock, patch
import pytest

from kapsel.core.plugin.fetcher import fetch_plugin_from_remote
from kapsel.completion.kps.builtins.add import handle_add_command


def test_fetch_plugin_from_remote_success():
    """Verifies that fetch_plugin_from_remote invokes git or archive streaming."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        dest_path = Path(tmp_dir) / "test_plugin"
        with patch("kapsel.core.plugin.fetcher._fetch_via_git", return_value=True):
            res = fetch_plugin_from_remote("test_plugin", dest_path)
            assert res is True


def test_fetch_plugin_from_remote_fallback_archive():
    """Verifies that if git fails, fallback to archive download is tried."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        dest_path = Path(tmp_dir) / "test_plugin"
        with patch("kapsel.core.plugin.fetcher._fetch_via_git", return_value=False), \
             patch("kapsel.core.plugin.fetcher._fetch_via_archive", return_value=True):
            res = fetch_plugin_from_remote("test_plugin", dest_path)
            assert res is True


def test_kps_add_calls_remote_fetcher_when_missing():
    """Verifies that 'kapsel add <name>' calls fetch_plugin_from_remote when plugin is not local."""
    with patch("kapsel.core.plugin.fetcher.fetch_plugin_from_remote") as mock_fetch, \
         patch("kapsel.completion.kps.builtins.add.load_config") as mock_cfg, \
         patch("kapsel.completion.kps.builtins.add.update_config_value") as mock_update:

        mock_fetch.return_value = False  # Simulate not found
        ret = handle_add_command(["nonexistent_plugin_xyz"])
        assert ret == 1
        assert mock_fetch.called
