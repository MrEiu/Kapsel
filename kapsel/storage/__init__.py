"""
Kapsel storage package.
Provides configuration, history database, and logging.
"""

from kapsel.storage.config import KapselConfig, load_config
from kapsel.storage.history import HistoryManager, KapselPromptHistory
from kapsel.storage.logger import get_kapsel_dir, logger

__all__ = [
    "KapselConfig",
    "load_config",
    "HistoryManager",
    "KapselPromptHistory",
    "logger",
    "get_kapsel_dir",
]
