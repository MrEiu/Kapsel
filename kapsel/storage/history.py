"""
Kapsel Command History & Persistence Storage (Facade).
Delegates directly to centralized UserDatabase (~/.kapsel/user.db) for cross-session retention.
"""

from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from prompt_toolkit.history import History

from kapsel.storage.user_db import get_user_db


def get_history_db_path() -> Path:
    return get_user_db().db_path


class HistoryManager:
    """Manages cross-session command history through centralized UserDatabase."""

    def __init__(self, db_path: Optional[Path] = None):
        self.user_db = get_user_db()

    def record_command(
        self,
        command: str,
        working_dir: str = "",
        exit_code: int = 0,
        duration_ms: int = 0,
        shell: str = "pwsh",
    ) -> None:
        cmd = command.strip()
        if not cmd:
            return
        self.user_db.record_history(
            command=cmd,
            working_dir=working_dir or str(Path.cwd()),
            exit_code=exit_code,
            duration_ms=duration_ms,
            shell=shell,
        )

    def add_record(
        self,
        command: str,
        translated_cmd: Optional[str] = None,
        mode: str = "native",
        cwd: str = "",
        shell: str = "pwsh",
        timestamp: float = 0.0,
        duration_ms: int = 0,
        exit_code: int = 0,
    ) -> None:
        """Called by DualStateEngine to persist executed commands with duration and exit status."""
        self.record_command(
            command=command,
            working_dir=cwd,
            exit_code=exit_code,
            duration_ms=duration_ms,
            shell=shell,
        )

    def increment_weight(self, alias: str) -> None:
        """Increments usage count for ranking."""
        pass

    def get_command_weights(self) -> Dict[str, int]:
        return self.user_db.get_command_weights()

    def get_recent_history_strings(self, limit: int = 20) -> List[str]:
        """
        Retrieves recent command strings from user.db.
        Returns entries in reverse chronological order (latest / most recent first),
        as expected by prompt_toolkit.history.History.
        """
        hist = self.user_db.get_recent_history(limit)
        results: List[str] = []
        for r in hist:
            cmd = r.get("command", "").strip()
            if cmd and (not results or results[-1] != cmd):
                results.append(cmd)
        return results


class KapselPromptHistory(History):
    """
    Integrates HistoryManager directly with prompt_toolkit PromptSession.
    Ensures full command lines are loaded across sessions and persisted on every entry.
    """

    def __init__(self, manager: Optional[HistoryManager] = None, limit: int = 20):
        super().__init__()
        self.manager = manager or HistoryManager()
        self.limit = limit

    def load_history_strings(self) -> Iterable[str]:
        """Loads previous session history strings (most recent first)."""
        return self.manager.get_recent_history_strings(limit=self.limit)

    def store_string(self, string: str) -> None:
        """Immediately persists newly entered command line to ~/.kapsel/user.db."""
        cmd = string.strip()
        if cmd:
            self.manager.record_command(command=cmd)
