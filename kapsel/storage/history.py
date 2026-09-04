"""
Kapsel Command History & Persistence Storage.
Directly uses local SQLite database (~/.kapsel/history.db) for cross-session retention.
"""

from datetime import datetime
from pathlib import Path
import sqlite3
from typing import Any, Dict, Iterable, List, Optional

from prompt_toolkit.history import History

from kapsel.storage.logger import get_kapsel_dir, logger


def get_history_db_path() -> Path:
    return get_kapsel_dir() / "history.db"


class HistoryManager:
    """Manages cross-session command history through local SQLite database."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or get_history_db_path()
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=10.0)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        """Initializes SQLite database and tables with automatic schema migration."""
        try:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            with self._get_connection() as conn:
                cur = conn.cursor()
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        command TEXT NOT NULL,
                        working_dir TEXT DEFAULT '',
                        cwd TEXT DEFAULT '',
                        exit_code INTEGER DEFAULT 0,
                        duration_ms INTEGER DEFAULT 0,
                        shell TEXT DEFAULT 'pwsh',
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
                # Check existing columns and migrate if necessary
                cols = [row[1] for row in cur.execute("PRAGMA table_info(history)").fetchall()]
                if "working_dir" not in cols:
                    cur.execute("ALTER TABLE history ADD COLUMN working_dir TEXT DEFAULT ''")
                if "cwd" not in cols:
                    cur.execute("ALTER TABLE history ADD COLUMN cwd TEXT DEFAULT ''")
                if "exit_code" not in cols:
                    cur.execute("ALTER TABLE history ADD COLUMN exit_code INTEGER DEFAULT 0")
                if "duration_ms" not in cols:
                    cur.execute("ALTER TABLE history ADD COLUMN duration_ms INTEGER DEFAULT 0")
                if "shell" not in cols:
                    cur.execute("ALTER TABLE history ADD COLUMN shell TEXT DEFAULT 'pwsh'")

                cur.execute("CREATE INDEX IF NOT EXISTS idx_hist_cmd ON history(command)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_hist_ts ON history(timestamp DESC)")
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to initialize history database: {e}")

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
        try:
            import time
            with self._get_connection() as conn:
                cur = conn.cursor()
                now_ts = time.time()
                target_dir = working_dir or str(Path.cwd())
                cur.execute(
                    """
                    INSERT INTO history (command, translated_cmd, mode, cwd, working_dir, exit_code, duration_ms, shell, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (cmd, None, "native", target_dir, target_dir, exit_code, duration_ms, shell, now_ts),
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to record history: {e}")

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
        """Called by Engine to persist executed commands with duration and exit status."""
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

    def get_recent_history_strings(self, limit: int = 50) -> List[str]:
        """
        Retrieves recent command strings.
        Returns entries in reverse chronological order (latest / most recent first).
        """
        try:
            with self._get_connection() as conn:
                cur = conn.cursor()
                cur.execute(
                    "SELECT command FROM history ORDER BY id DESC LIMIT ?",
                    (limit,),
                )
                rows = cur.fetchall()
                results: List[str] = []
                for r in rows:
                    cmd = r["command"].strip()
                    if cmd and (not results or results[-1] != cmd):
                        results.append(cmd)
                return results
        except Exception as e:
            logger.error(f"Failed to fetch history strings: {e}")
            return []


class KapselPromptHistory(History):
    """
    Integrates HistoryManager directly with prompt_toolkit PromptSession.
    Ensures full command lines are loaded across sessions and persisted on every entry.
    """

    def __init__(self, manager: Optional[HistoryManager] = None, limit: int = 50):
        super().__init__()
        self.manager = manager or HistoryManager()
        self.limit = limit

    def load_history_strings(self) -> Iterable[str]:
        """Loads previous session history strings (most recent first)."""
        return self.manager.get_recent_history_strings(limit=self.limit)

    def store_string(self, string: str) -> None:
        """Immediately persists newly entered command line to local SQLite history."""
        cmd = string.strip()
        if cmd:
            self.manager.record_command(command=cmd)
