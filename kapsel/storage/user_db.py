"""
Kapsel User Data Storage.
Centralized SQLite database (~/.kapsel/user.db) storing user execution history and identity profiles.
Prevents file clutter and prepares a single point for whole-database encryption in the future.
"""

from datetime import datetime
from pathlib import Path
import sqlite3
from typing import Any, Dict, List, Optional

from kapsel.storage.logger import get_kapsel_dir, logger


def get_user_db_path() -> Path:
    """Returns path to ~/.kapsel/user.db (or within KAPSEL_HOME)."""
    return get_kapsel_dir() / "user.db"


class UserDatabase:
    """
    Central SQLite database for personal user data:
    1. history: command execution logs, timings, exit codes, and frequency weights.
    2. user_profile: digital identity, device fingerprint, and cloud sync credentials.
    Designed with future whole-database encryption hooks (e.g. SQLCipher / envelope encryption).
    """

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or get_user_db_path()
        self._active_conns: List[sqlite3.Connection] = []
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        self._active_conns.append(conn)
        return conn

    def _init_db(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._get_connection() as conn:
            cur = conn.cursor()

            # 1. Execution history table
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    command TEXT NOT NULL,
                    working_dir TEXT NOT NULL,
                    exit_code INTEGER DEFAULT 0,
                    duration_ms INTEGER DEFAULT 0,
                    shell TEXT DEFAULT 'pwsh',
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            # 2. User profile & identity credentials table
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS user_profile (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    email TEXT DEFAULT '',
                    sync_key TEXT NOT NULL,
                    device_id TEXT NOT NULL,
                    registered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_synced_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    is_active INTEGER DEFAULT 1
                )
                """
            )

            # Indexes for fast retrieval
            cur.execute("CREATE INDEX IF NOT EXISTS idx_hist_cmd ON history(command)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_hist_ts ON history(timestamp DESC)")
            conn.commit()

    # ==================== History Management ====================

    def record_history(
        self,
        command: str,
        working_dir: str,
        exit_code: int = 0,
        duration_ms: int = 0,
        shell: str = "pwsh",
    ) -> int:
        cmd_clean = command.strip()
        if not cmd_clean:
            return 0
        try:
            with self._get_connection() as conn:
                cur = conn.cursor()
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cur.execute(
                    """
                    INSERT INTO history (command, working_dir, exit_code, duration_ms, shell, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (cmd_clean, working_dir, exit_code, duration_ms, shell, now),
                )
                conn.commit()
                return cur.lastrowid or 0
        except Exception as e:
            logger.error(f"Failed to record history: {e}")
            return 0

    def get_recent_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        try:
            with self._get_connection() as conn:
                cur = conn.cursor()
                cur.execute(
                    "SELECT command, working_dir, exit_code, duration_ms, shell, timestamp FROM history ORDER BY id DESC LIMIT ?",
                    (limit,),
                )
                return [dict(r) for r in cur.fetchall()]
        except Exception as e:
            logger.error(f"Failed to fetch recent history: {e}")
            return []

    def get_command_weights(self) -> Dict[str, int]:
        """
        Calculates frequency-based weights for autocomplete suggestion ranking.
        Commands used more frequently receive higher ranking weight scores.
        """
        try:
            with self._get_connection() as conn:
                cur = conn.cursor()
                cur.execute(
                    """
                    SELECT command, COUNT(*) as cnt
                    FROM history
                    GROUP BY command
                    ORDER BY cnt DESC
                    LIMIT 200
                    """
                )
                weights = {}
                for row in cur.fetchall():
                    cmd = row["command"].strip()
                    primary = cmd.split()[0] if cmd else ""
                    cnt = row["cnt"]
                    weights[cmd] = weights.get(cmd, 0) + (cnt * 10)
                    if primary:
                        weights[primary] = weights.get(primary, 0) + (cnt * 5)
                return weights
        except Exception as e:
            logger.error(f"Failed to calculate command weights: {e}")
            return {}

    def get_stats(self) -> Dict[str, Any]:
        try:
            with self._get_connection() as conn:
                cur = conn.cursor()
                cur.execute("SELECT COUNT(*) FROM history")
                total_history = cur.fetchone()[0]
                cur.execute("SELECT COUNT(DISTINCT command) FROM history")
                unique_cmds = cur.fetchone()[0]
                return {"total_history": total_history, "unique_commands": unique_cmds}
        except Exception:
            return {"total_history": 0, "unique_commands": 0}

    # ==================== User Profile Management ====================

    def save_user(self, username: str, sync_key: str, device_id: str, email: str = "") -> bool:
        try:
            with self._get_connection() as conn:
                cur = conn.cursor()
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                # Deactivate others to make this one the active profile
                cur.execute("UPDATE user_profile SET is_active = 0")
                cur.execute(
                    """
                    INSERT INTO user_profile (username, email, sync_key, device_id, registered_at, last_synced_at, is_active)
                    VALUES (?, ?, ?, ?, ?, ?, 1)
                    ON CONFLICT(username) DO UPDATE SET
                        email=excluded.email,
                        sync_key=excluded.sync_key,
                        device_id=excluded.device_id,
                        last_synced_at=excluded.last_synced_at,
                        is_active=1
                    """,
                    (username.strip(), email.strip(), sync_key.strip(), device_id.strip(), now, now),
                )
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Failed to save user profile: {e}")
            return False

    def get_active_user(self) -> Optional[Dict[str, Any]]:
        try:
            with self._get_connection() as conn:
                cur = conn.cursor()
                cur.execute("SELECT * FROM user_profile WHERE is_active = 1 LIMIT 1")
                row = cur.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"Failed to get active user: {e}")
            return None

    def logout_active_user(self) -> bool:
        try:
            with self._get_connection() as conn:
                cur = conn.cursor()
                cur.execute("UPDATE user_profile SET is_active = 0")
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Failed to logout user: {e}")
            return False

    def close(self) -> None:
        """Flushes and releases all database connections."""
        for conn in list(self._active_conns):
            try:
                conn.close()
            except Exception:
                pass
        self._active_conns.clear()
        import gc
        gc.collect()

    def reset_path(self, new_path: Optional[Path] = None) -> None:
        """Re-points database path to new location and re-initializes."""
        self.db_path = new_path or get_user_db_path()
        self._init_db()


# Global singleton instance accessor
_USER_DB_INSTANCE: Optional[UserDatabase] = None


def get_user_db() -> UserDatabase:
    global _USER_DB_INSTANCE
    if _USER_DB_INSTANCE is None or _USER_DB_INSTANCE.db_path != get_user_db_path():
        _USER_DB_INSTANCE = UserDatabase(get_user_db_path())
    return _USER_DB_INSTANCE
