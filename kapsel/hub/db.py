"""
Kapsel Cloud Command Hub & Mapping Repository (SQLite-backed).
Implements a 2-layer hierarchy (Platform -> Software) and a dedicated Mapping Registry (pwsh-focused).
"""

from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
import sqlite3
from typing import Any, Dict, List, Optional

from kapsel.storage.logger import logger


def get_hub_db_path() -> Path:
    """
    Returns the primary Hub SQLite path:
    1. ~/.kapsel/registry.db (Local User Sync Cache)
    2. KPS-Hub/registry.db (Standalone KPS-Hub workspace master)
    3. kapsel/hub/registry.db (Internal fallback)
    """
    user_db = Path.home() / ".kapsel" / "registry.db"
    if user_db.exists():
        return user_db

    workspace_hub = Path(__file__).resolve().parent.parent.parent / "KPS-Hub" / "registry.db"
    if workspace_hub.exists():
        return workspace_hub

    return Path(__file__).resolve().parent / "registry.db"


@dataclass
class HubPackage:
    id: Optional[int]
    platform: str
    software: str
    display_name: str
    version: str
    desc: str
    category: str
    author: str
    tags: str
    updated_at: str


@dataclass
class HubCommand:
    id: Optional[int]
    package_id: int
    platform: str
    software: str
    command_name: str
    full_alias: str
    desc: str
    usage: str
    example: str


@dataclass
class HubMapping:
    id: Optional[int]
    command_id: Optional[int]
    source_alias: str
    target_shell: str
    target_template: str
    flags_json: str
    desc: str
    version: str
    updated_at: str


class HubRepository:
    """SQLite-backed command hub repository manager."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or get_hub_db_path()
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=10.0)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        """Initializes tables for packages (Platform -> Software), commands, and mappings."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                # 1. Platform -> Software package layer
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS hub_packages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        platform TEXT NOT NULL,
                        software TEXT NOT NULL,
                        display_name TEXT NOT NULL,
                        version TEXT DEFAULT '1.0.0',
                        desc TEXT NOT NULL,
                        category TEXT DEFAULT 'general',
                        author TEXT DEFAULT 'Kapsel Official',
                        tags TEXT DEFAULT '',
                        updated_at TEXT NOT NULL,
                        UNIQUE(platform, software)
                    );
                """)

                # 2. Software commands layer
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS hub_commands (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        package_id INTEGER REFERENCES hub_packages(id) ON DELETE CASCADE,
                        platform TEXT NOT NULL,
                        software TEXT NOT NULL,
                        command_name TEXT NOT NULL,
                        full_alias TEXT NOT NULL,
                        desc TEXT NOT NULL,
                        usage TEXT,
                        example TEXT,
                        UNIQUE(platform, software, command_name)
                    );
                """)

                # 3. Dedicated Mapping Repository (Focused on pwsh first)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS hub_mappings (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        command_id INTEGER,
                        source_alias TEXT NOT NULL,
                        target_shell TEXT NOT NULL DEFAULT 'pwsh',
                        target_template TEXT NOT NULL,
                        flags_json TEXT DEFAULT '{}',
                        desc TEXT NOT NULL,
                        version TEXT DEFAULT '1.0.0',
                        updated_at TEXT NOT NULL,
                        UNIQUE(source_alias, target_shell)
                    );
                """)

                cursor.execute("CREATE INDEX IF NOT EXISTS idx_hub_pkg_sw ON hub_packages (platform, software);")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_hub_cmd_alias ON hub_commands (full_alias);")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_hub_map_alias ON hub_mappings (source_alias, target_shell);")
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to initialize Hub SQLite DB at {self.db_path}: {e}")

    def list_packages(self, platform_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Lists all registered software packages, optionally filtered by platform."""
        with self._get_connection() as conn:
            cur = conn.cursor()
            if platform_filter:
                cur.execute(
                    "SELECT * FROM hub_packages WHERE platform = ? OR platform = 'universal' ORDER BY platform, software",
                    (platform_filter,),
                )
            else:
                cur.execute("SELECT * FROM hub_packages ORDER BY platform, software")
            rows = cur.fetchall()
            return [dict(r) for r in rows]

    def get_package(self, software: str, platform: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Retrieves package metadata by software name."""
        with self._get_connection() as conn:
            cur = conn.cursor()
            if platform:
                cur.execute("SELECT * FROM hub_packages WHERE software = ? AND platform = ?", (software, platform))
            else:
                cur.execute("SELECT * FROM hub_packages WHERE software = ? ORDER BY id ASC LIMIT 1", (software,))
            row = cur.fetchone()
            return dict(row) if row else None

    def get_commands_for_software(self, software: str, platform: Optional[str] = None) -> List[Dict[str, Any]]:
        """Returns all command entries under a specific software package."""
        with self._get_connection() as conn:
            cur = conn.cursor()
            if platform:
                cur.execute(
                    "SELECT * FROM hub_commands WHERE software = ? AND (platform = ? OR platform = 'universal') ORDER BY command_name",
                    (software, platform),
                )
            else:
                cur.execute("SELECT * FROM hub_commands WHERE software = ? ORDER BY command_name", (software,))
            return [dict(r) for r in cur.fetchall()]

    def list_mappings(self, target_shell: str = "pwsh") -> List[Dict[str, Any]]:
        """Lists all mappings registered for a specific target shell (default: pwsh)."""
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT * FROM hub_mappings WHERE target_shell = ? ORDER BY source_alias ASC",
                (target_shell,),
            )
            return [dict(r) for r in cur.fetchall()]

    def search(self, query: str) -> Dict[str, Any]:
        """Performs cross-table search across packages, commands, and mappings."""
        pattern = f"%{query.strip().lower()}%"
        with self._get_connection() as conn:
            cur = conn.cursor()
            # Search packages
            cur.execute(
                "SELECT * FROM hub_packages WHERE lower(software) LIKE ? OR lower(display_name) LIKE ? OR lower(desc) LIKE ?",
                (pattern, pattern, pattern),
            )
            packages = [dict(r) for r in cur.fetchall()]

            # Search commands
            cur.execute(
                "SELECT * FROM hub_commands WHERE lower(full_alias) LIKE ? OR lower(command_name) LIKE ? OR lower(desc) LIKE ?",
                (pattern, pattern, pattern),
            )
            commands = [dict(r) for r in cur.fetchall()]

            # Search mappings
            cur.execute(
                "SELECT * FROM hub_mappings WHERE lower(source_alias) LIKE ? OR lower(target_template) LIKE ? OR lower(desc) LIKE ?",
                (pattern, pattern, pattern),
            )
            mappings = [dict(r) for r in cur.fetchall()]

            return {
                "packages": packages,
                "commands": commands,
                "mappings": mappings,
            }

    # ==================== CRUD & Administration ====================

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
        """Creates or updates a package in the hub."""
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
        """Deletes a package and all associated commands."""
        with self._get_connection() as conn:
            cur = conn.cursor()
            if platform:
                cur.execute("DELETE FROM hub_commands WHERE software = ? AND platform = ?", (software, platform))
                cur.execute("DELETE FROM hub_packages WHERE software = ? AND platform = ?", (software, platform))
            else:
                cur.execute("DELETE FROM hub_commands WHERE software = ?", (software,))
                cur.execute("DELETE FROM hub_packages WHERE software = ?", (software,))
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
        """Adds or updates a command under a software package."""
        pkg = self.get_package(software, platform)
        if not pkg:
            # Auto create package if missing
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
        """Deletes a command from a software package."""
        with self._get_connection() as conn:
            cur = conn.cursor()
            if platform:
                cur.execute("DELETE FROM hub_commands WHERE software = ? AND command_name = ? AND platform = ?", (software, command_name, platform))
            else:
                cur.execute("DELETE FROM hub_commands WHERE software = ? AND command_name = ?", (software, command_name))
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
        """Adds or updates a mapping in the mapping repository."""
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
        """Deletes a mapping from the mapping repository."""
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM hub_mappings WHERE source_alias = ? AND target_shell = ?", (source_alias, target_shell.lower()))
            conn.commit()
            return cur.rowcount > 0

    def get_stats(self) -> Dict[str, Any]:
        """Returns database metadata and statistical metrics."""
        size_bytes = self.db_path.stat().st_size if self.db_path.exists() else 0
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM hub_packages")
            pkg_count = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM hub_commands")
            cmd_count = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM hub_mappings")
            map_count = cur.fetchone()[0]

            return {
                "db_path": str(self.db_path),
                "size_bytes": size_bytes,
                "size_kb": round(size_bytes / 1024, 2),
                "packages_count": pkg_count,
                "commands_count": cmd_count,
                "mappings_count": map_count,
            }

    def export_all(self) -> Dict[str, Any]:
        """Exports all hub tables into a serializable dictionary."""
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

    def import_all(self, data: Dict[str, Any]) -> Dict[str, int]:
        """Imports packages, commands, and mappings from export dictionary."""
        pkgs = data.get("packages", [])
        cmds = data.get("commands", [])
        maps = data.get("mappings", [])

        pkg_inserted = 0
        cmd_inserted = 0
        map_inserted = 0

        for p in pkgs:
            self.add_package(
                platform=p.get("platform", "universal"),
                software=p.get("software", ""),
                display_name=p.get("display_name", p.get("software", "")),
                desc=p.get("desc", ""),
                version=p.get("version", "1.0.0"),
                category=p.get("category", "general"),
                author=p.get("author", "Community"),
                tags=p.get("tags", ""),
            )
            pkg_inserted += 1

        for c in cmds:
            self.add_command(
                software=c.get("software", ""),
                command_name=c.get("command_name", ""),
                full_alias=c.get("full_alias", ""),
                desc=c.get("desc", ""),
                platform=c.get("platform", "universal"),
                usage=c.get("usage", ""),
                example=c.get("example", ""),
            )
            cmd_inserted += 1

        for m in maps:
            self.add_mapping(
                source_alias=m.get("source_alias", ""),
                target_template=m.get("target_template", ""),
                desc=m.get("desc", ""),
                target_shell=m.get("target_shell", "pwsh"),
                flags_json=m.get("flags_json", "{}"),
            )
            map_inserted += 1

        return {
            "packages": pkg_inserted,
            "commands": cmd_inserted,
            "mappings": map_inserted,
        }

