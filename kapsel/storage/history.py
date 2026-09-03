"""
Kapsel Command History & Frequency Weight Storage (Facade).
Delegates directly to centralized UserDatabase (~/.kapsel/user.db).
"""

from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from prompt_toolkit.history import History

from kapsel.storage.user_db import get_user_db


def get_history_db_path() -> Path:
    return get_user_db().db_path


class HistoryManager:
    """Manages command history through centralized UserDatabase."""

    def __init__(self, db_path: Optional[Path] = None):
        self.user_db = get_user_db()

    def record_command(
        self,
        command: str,
        working_dir: str,
        exit_code: int = 0,
        duration_ms: int = 0,
        shell: str = "pwsh",
    ) -> None:
        self.user_db.record_history(
            command=command,
            working_dir=working_dir,
            exit_code=exit_code,
            duration_ms=duration_ms,
            shell=shell,
        )

    def record_usage(self, alias: str) -> None:
        pass

    def get_command_weights(self) -> Dict[str, int]:
        return self.user_db.get_command_weights()

    def get_recent_history_strings(self, limit: int = 1000) -> List[str]:
        hist = self.user_db.get_recent_history(limit)
        results: List[str] = []
        for r in reversed(hist):
            cmd = r.get("command", "").strip()
            if cmd and (not results or results[-1] != cmd):
                results.append(cmd)
        return results


class KapselPromptHistory(History):
    """Integrates HistoryManager directly with prompt_toolkit PromptSession."""

    def __init__(self, manager: Optional[HistoryManager] = None):
        super().__init__()
        self.manager = manager or HistoryManager()

    def load_history_strings(self) -> Iterable[str]:
        return self.manager.get_recent_history_strings(limit=2000)

    def store_string(self, string: str) -> None:
        pass
