"""
Kapsel isolated state and history database manager.
Manages ~/.kapsel/history.db (SQLite) for cross-shell roaming and frequency learning.
"""

from collections.abc import Iterable
from pathlib import Path
import sqlite3
import time
from typing import Dict, List, Optional

from prompt_toolkit.history import History

from kapsel.storage.logger import get_kapsel_dir, logger


def get_history_db_path() -> Path:
    return get_kapsel_dir() / "history.db"


class HistoryManager:
    """Manages persistent command history and command weight statistics in SQLite."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or get_history_db_path()
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=5.0)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        command TEXT NOT NULL,
                        translated_cmd TEXT,
                        mode TEXT NOT NULL,
                        cwd TEXT NOT NULL,
                        shell TEXT NOT NULL,
                        timestamp REAL NOT NULL,
                        duration_ms INTEGER,
                        exit_code INTEGER
                    );
                """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS command_weights (
                        alias TEXT PRIMARY KEY,
                        count INTEGER DEFAULT 1,
                        last_used REAL NOT NULL
                    );
                """)
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_hist_ts ON history (timestamp ASC);")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_hist_cmd ON history (command);")
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to initialize SQLite history database at {self.db_path}: {e}")

    def add_record(
        self,
        command: str,
        translated_cmd: Optional[str] = None,
        mode: str = "native",
        cwd: str = "",
        shell: str = "",
        timestamp: Optional[float] = None,
        duration_ms: Optional[int] = None,
        exit_code: Optional[int] = None,
    ) -> None:
        """Record an executed command and its execution metadata."""
        if not command.strip():
            return
        ts = timestamp or time.time()
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO history (command, translated_cmd, mode, cwd, shell, timestamp, duration_ms, exit_code)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (command, translated_cmd or command, mode, cwd, shell, ts, duration_ms, exit_code),
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to record history entry: {e}")

    def increment_weight(self, alias: str) -> None:
        """Increment frequency weight for a kps alias to optimize completion ranking."""
        alias = alias.strip()
        if not alias:
            return
        now = time.time()
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO command_weights (alias, count, last_used)
                    VALUES (?, 1, ?)
                    ON CONFLICT(alias) DO UPDATE SET
                        count = count + 1,
                        last_used = excluded.last_used
                    """,
                    (alias, now),
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to increment command weight for '{alias}': {e}")

    def get_command_weights(self) -> Dict[str, int]:
        """Return a mapping of alias -> execution count for completion ranking."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT alias, count FROM command_weights")
                return {row["alias"]: row["count"] for row in cursor.fetchall()}
        except Exception as e:
            logger.error(f"Failed to fetch command weights: {e}")
            return {}

    def get_recent_history_strings(self, limit: int = 1000) -> List[str]:
        """Retrieve recent commands in chronological order (oldest to newest)."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT command FROM (
                        SELECT id, command FROM history ORDER BY id DESC LIMIT ?
                    ) ORDER BY id ASC
                    """,
                    (limit,),
                )
                # Filter out adjacent duplicates while preserving order
                results: List[str] = []
                for row in cursor.fetchall():
                    cmd = row["command"]
                    if not results or results[-1] != cmd:
                        results.append(cmd)
                return results
        except Exception as e:
            logger.error(f"Failed to fetch history strings: {e}")
            return []


class KapselPromptHistory(History):
    """Integrates HistoryManager directly with prompt_toolkit PromptSession."""

    def __init__(self, manager: HistoryManager):
        super().__init__()
        self.manager = manager

    def load_history_strings(self) -> Iterable[str]:
        return self.manager.get_recent_history_strings(limit=2000)

    def store_string(self, string: str) -> None:
        # We record the comprehensive record after execution, so nothing needed here.
        pass
