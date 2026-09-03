"""
KPS-Hub Database Engine.
Standalone SQLite data access layer for the Cloud Command Hub.
"""

from datetime import datetime
from pathlib import Path
import sqlite3
from typing import Any, Dict, List, Optional


def get_hub_db_path() -> Path:
    """Returns path to the server-side registry.db."""
    return Path(__file__).parent / "registry.db"


class HubRepository:
    """
    Central database repository for KPS-Hub.
    Manages:
    1. hub_packages: Two-tier metadata (platform -> software)
    2. hub_commands: Detailed subcommands, usage, and examples per software
    3. hub_mappings: Standalone shell translation templates (focused on pwsh)
    4. hub_users: Cloud sync identity and device registry
    """

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or get_hub_db_path()
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._get_connection() as conn:
            cur = conn.cursor()

            # 1. Packages table
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS hub_packages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    platform TEXT NOT NULL,
                    software TEXT NOT NULL,
                    display_name TEXT NOT NULL,
                    version TEXT DEFAULT '1.0.0',
                    desc TEXT NOT NULL,
                    category TEXT DEFAULT 'general',
                    author TEXT DEFAULT 'Community',
                    tags TEXT DEFAULT '',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(platform, software)
                )
                """
            )

            # 2. Commands table
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS hub_commands (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    package_id INTEGER NOT NULL,
                    platform TEXT NOT NULL,
                    software TEXT NOT NULL,
                    command_name TEXT NOT NULL,
                    full_alias TEXT NOT NULL,
                    desc TEXT NOT NULL,
                    usage TEXT DEFAULT '',
                    example TEXT DEFAULT '',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(platform, software, command_name),
                    FOREIGN KEY(package_id) REFERENCES hub_packages(id) ON DELETE CASCADE
                )
                """
            )

            # 3. Mappings table (focused on pwsh)
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS hub_mappings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_alias TEXT NOT NULL,
                    target_shell TEXT NOT NULL DEFAULT 'pwsh',
                    target_template TEXT NOT NULL,
                    flags_json TEXT DEFAULT '{}',
                    desc TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(source_alias, target_shell)
                )
                """
            )

            # 4. Cloud Users table (for device sync)
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS hub_users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    email TEXT DEFAULT '',
                    sync_key TEXT NOT NULL,
                    device_id TEXT NOT NULL,
                    registered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_synced_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            # Create Indexes for fast lookups
            cur.execute("CREATE INDEX IF NOT EXISTS idx_pkg_plat ON hub_packages(platform, software)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_cmd_soft ON hub_commands(software, platform)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_map_shell ON hub_mappings(target_shell, source_alias)")
            conn.commit()

    # ==================== Queries ====================

    def list_packages(self, platform_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cur = conn.cursor()
            if platform_filter:
                cur.execute(
                    "SELECT * FROM hub_packages WHERE platform = ? OR platform = 'universal' ORDER BY platform, software",
                    (platform_filter.lower(),),
                )
            else:
                cur.execute("SELECT * FROM hub_packages ORDER BY platform, software")
            return [dict(r) for r in cur.fetchall()]

    def get_package(self, software: str, platform: Optional[str] = None) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cur = conn.cursor()
            if platform:
                cur.execute("SELECT * FROM hub_packages WHERE software = ? AND platform = ?", (software.lower(), platform.lower()))
            else:
                cur.execute("SELECT * FROM hub_packages WHERE software = ? ORDER BY id ASC LIMIT 1", (software.lower(),))
            row = cur.fetchone()
            return dict(row) if row else None

    def get_commands_for_software(self, software: str, platform: Optional[str] = None) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cur = conn.cursor()
            if platform:
                cur.execute(
                    "SELECT * FROM hub_commands WHERE software = ? AND (platform = ? OR platform = 'universal') ORDER BY command_name",
                    (software.lower(), platform.lower()),
                )
            else:
                cur.execute("SELECT * FROM hub_commands WHERE software = ? ORDER BY command_name", (software.lower(),))
            return [dict(r) for r in cur.fetchall()]

    def list_mappings(self, target_shell: str = "pwsh") -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT * FROM hub_mappings WHERE target_shell = ? ORDER BY source_alias ASC",
                (target_shell.lower(),),
            )
            return [dict(r) for r in cur.fetchall()]

    def search_all(self, query: str) -> Dict[str, List[Dict[str, Any]]]:
        pattern = f"%{query.strip().lower()}%"
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT * FROM hub_packages WHERE software LIKE ? OR display_name LIKE ? OR desc LIKE ? OR tags LIKE ?",
                (pattern, pattern, pattern, pattern),
            )
            packages = [dict(r) for r in cur.fetchall()]

            cur.execute(
                "SELECT * FROM hub_commands WHERE command_name LIKE ? OR full_alias LIKE ? OR desc LIKE ?",
                (pattern, pattern, pattern),
            )
            commands = [dict(r) for r in cur.fetchall()]

            cur.execute(
                "SELECT * FROM hub_mappings WHERE source_alias LIKE ? OR target_template LIKE ? OR desc LIKE ?",
                (pattern, pattern, pattern),
            )
            mappings = [dict(r) for r in cur.fetchall()]

            return {
                "packages": packages,
                "commands": commands,
                "mappings": mappings,
            }

    # ==================== CRUD ====================

    def add_package(
        self,
        platform: str,
        software: str,
        display_name: str,
        desc: str,
        version: str = "1.0.0",
        category: str = "general",
        author: str = "Community",
        tags: str = "",
    ) -> int:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO hub_packages (platform, software, display_name, version, desc, category, author, tags, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(platform, software) DO UPDATE SET
                    display_name=excluded.display_name,
                    version=excluded.version,
                    desc=excluded.desc,
                    category=excluded.category,
                    author=excluded.author,
                    tags=excluded.tags,
                    updated_at=excluded.updated_at
                """,
                (platform.lower(), software.lower(), display_name, version, desc, category, author, tags, now),
            )
            conn.commit()
            return cur.lastrowid or 0

    def delete_package(self, software: str, platform: Optional[str] = None) -> bool:
        with self._get_connection() as conn:
            cur = conn.cursor()
            if platform:
                cur.execute("DELETE FROM hub_commands WHERE software = ? AND platform = ?", (software.lower(), platform.lower()))
                cur.execute("DELETE FROM hub_packages WHERE software = ? AND platform = ?", (software.lower(), platform.lower()))
            else:
                cur.execute("DELETE FROM hub_commands WHERE software = ?", (software.lower(),))
                cur.execute("DELETE FROM hub_packages WHERE software = ?", (software.lower(),))
            conn.commit()
            return cur.rowcount > 0

    def add_command(
        self,
        software: str,
        command_name: str,
        full_alias: str,
        desc: str,
        platform: str = "universal",
        usage: str = "",
        example: str = "",
    ) -> int:
        pkg = self.get_package(software, platform)
        if not pkg:
            self.add_package(platform=platform, software=software, display_name=software.title(), desc=f"{software} toolset")
            pkg = self.get_package(software, platform)

        pkg_id = pkg["id"] if pkg else 1
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO hub_commands (package_id, platform, software, command_name, full_alias, desc, usage, example)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(platform, software, command_name) DO UPDATE SET
                    full_alias=excluded.full_alias,
                    desc=excluded.desc,
                    usage=excluded.usage,
                    example=excluded.example
                """,
                (pkg_id, platform.lower(), software.lower(), command_name.lower(), full_alias, desc, usage, example),
            )
            conn.commit()
            return cur.lastrowid or 0

    def delete_command(self, software: str, command_name: str, platform: Optional[str] = None) -> bool:
        with self._get_connection() as conn:
            cur = conn.cursor()
            if platform:
                cur.execute("DELETE FROM hub_commands WHERE software = ? AND command_name = ? AND platform = ?", (software.lower(), command_name.lower(), platform.lower()))
            else:
                cur.execute("DELETE FROM hub_commands WHERE software = ? AND command_name = ?", (software.lower(), command_name.lower()))
            conn.commit()
            return cur.rowcount > 0

    def add_mapping(
        self,
        source_alias: str,
        target_template: str,
        desc: str,
        target_shell: str = "pwsh",
        flags_json: str = "{}",
    ) -> int:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO hub_mappings (source_alias, target_shell, target_template, flags_json, desc, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(source_alias, target_shell) DO UPDATE SET
                    target_template=excluded.target_template,
                    flags_json=excluded.flags_json,
                    desc=excluded.desc,
                    updated_at=excluded.updated_at
                """,
                (source_alias, target_shell.lower(), target_template, flags_json, desc, now),
            )
            conn.commit()
            return cur.lastrowid or 0

    def delete_mapping(self, source_alias: str, target_shell: str = "pwsh") -> bool:
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM hub_mappings WHERE source_alias = ? AND target_shell = ?", (source_alias, target_shell.lower()))
            conn.commit()
            return cur.rowcount > 0

    # ==================== User & Sync ====================

    def register_user(self, username: str, email: str, sync_key: str, device_id: str) -> bool:
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO hub_users (username, email, sync_key, device_id)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(username) DO UPDATE SET
                    email=excluded.email,
                    sync_key=excluded.sync_key,
                    device_id=excluded.device_id,
                    last_synced_at=CURRENT_TIMESTAMP
                """,
                (username.strip(), email.strip(), sync_key, device_id),
            )
            conn.commit()
            return True

    def get_user(self, username: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM hub_users WHERE username = ?", (username.strip(),))
            row = cur.fetchone()
            return dict(row) if row else None

    # ==================== Stats & Export ====================

    def get_stats(self) -> Dict[str, Any]:
        size_bytes = self.db_path.stat().st_size if self.db_path.exists() else 0
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM hub_packages")
            pkg_count = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM hub_commands")
            cmd_count = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM hub_mappings")
            map_count = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM hub_users")
            user_count = cur.fetchone()[0]

            return {
                "db_path": str(self.db_path),
                "size_bytes": size_bytes,
                "size_kb": round(size_bytes / 1024, 2),
                "packages_count": pkg_count,
                "commands_count": cmd_count,
                "mappings_count": map_count,
                "users_count": user_count,
                "server_time": datetime.now().isoformat(),
            }

    def export_all(self) -> Dict[str, Any]:
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM hub_packages")
            pkgs = [dict(r) for r in cur.fetchall()]
            cur.execute("SELECT * FROM hub_commands")
            cmds = [dict(r) for r in cur.fetchall()]
            cur.execute("SELECT * FROM hub_mappings")
            maps = [dict(r) for r in cur.fetchall()]

            return {
                "version": "1.0",
                "exported_at": datetime.now().isoformat(),
                "packages": pkgs,
                "commands": cmds,
                "mappings": maps,
            }
