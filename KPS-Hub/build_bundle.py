"""
KPS-Hub Build Script.
Compiles all JSON manifests in manifests/ and mappings in mappings/
into a standalone SQLite database (registry.db) and a static bundle (registry.bundle.json).
"""

import gzip
import json
from pathlib import Path
import sqlite3
import sys

if sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT = Path(__file__).parent
MANIFESTS_DIR = ROOT / "manifests"
MAPPINGS_DIR = ROOT / "mappings"
DB_PATH = ROOT / "registry.db"
BUNDLE_JSON_PATH = ROOT / "registry.bundle.json"
BUNDLE_GZ_PATH = ROOT / "registry.bundle.json.gz"


def build():
    print("🔨 Compiling KPS-Hub Community Registry...")
    packages = []
    for f in sorted(MANIFESTS_DIR.glob("*.json")):
        with open(f, "r", encoding="utf-8") as fp:
            data = json.load(fp)
            packages.append(data)
            print(f"  • Loaded manifest: {f.name} ({len(data.get('commands', []))} commands)")

    mappings = []
    for f in sorted(MAPPINGS_DIR.glob("*.json")):
        with open(f, "r", encoding="utf-8") as fp:
            data = json.load(fp)
            if isinstance(data, list):
                mappings.extend(data)
                print(f"  • Loaded mapping: {f.name} ({len(data)} rules)")

    bundle = {
        "version": "1.0.0",
        "packages": packages,
        "mappings": mappings,
    }

    # 1. Output registry.bundle.json
    with open(BUNDLE_JSON_PATH, "w", encoding="utf-8") as fp:
        json.dump(bundle, fp, indent=2, ensure_ascii=False)
    print(f"✔ Generated bundle: {BUNDLE_JSON_PATH}")

    # 2. Output registry.bundle.json.gz
    with gzip.open(BUNDLE_GZ_PATH, "wt", encoding="utf-8") as fp:
        json.dump(bundle, fp, ensure_ascii=False)
    print(f"✔ Generated compressed gzip bundle: {BUNDLE_GZ_PATH} ({BUNDLE_GZ_PATH.stat().st_size} bytes)")

    # 3. Compile into SQLite database
    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE hub_packages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            platform TEXT NOT NULL,
            software TEXT NOT NULL,
            display_name TEXT NOT NULL,
            version TEXT DEFAULT '1.0.0',
            desc TEXT NOT NULL,
            category TEXT DEFAULT 'general',
            author TEXT DEFAULT 'Community',
            tags TEXT DEFAULT '',
            UNIQUE(platform, software)
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE hub_commands (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            package_id INTEGER NOT NULL,
            platform TEXT NOT NULL,
            software TEXT NOT NULL,
            command_name TEXT NOT NULL,
            full_alias TEXT NOT NULL,
            desc TEXT NOT NULL,
            usage TEXT DEFAULT '',
            example TEXT DEFAULT '',
            UNIQUE(platform, software, command_name)
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE hub_mappings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_alias TEXT NOT NULL,
            target_shell TEXT NOT NULL DEFAULT 'pwsh',
            target_template TEXT NOT NULL,
            flags_json TEXT DEFAULT '{}',
            desc TEXT NOT NULL,
            UNIQUE(source_alias, target_shell)
        )
        """
    )

    for p in packages:
        cur.execute(
            """
            INSERT INTO hub_packages (platform, software, display_name, version, desc, category, author, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (p["platform"], p["software"], p["display_name"], p.get("version", "1.0.0"), p["desc"], p.get("category", "general"), p.get("author", "Community"), p.get("tags", "")),
        )
        pkg_id = cur.lastrowid
        for c in p.get("commands", []):
            cur.execute(
                """
                INSERT INTO hub_commands (package_id, platform, software, command_name, full_alias, desc, usage, example)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (pkg_id, p["platform"], p["software"], c["command_name"], c["full_alias"], c["desc"], c.get("usage", ""), c.get("example", "")),
            )

    for m in mappings:
        cur.execute(
            """
            INSERT INTO hub_mappings (source_alias, target_shell, target_template, flags_json, desc)
            VALUES (?, ?, ?, ?, ?)
            """,
            (m["source_alias"], m.get("target_shell", "pwsh"), m["target_template"], m.get("flags_json", "{}"), m["desc"]),
        )

    conn.commit()
    conn.close()
    print(f"✔ Compiled SQLite database: {DB_PATH} ({DB_PATH.stat().st_size} bytes)")
    print("🎉 KPS-Hub Community Build Finished Successfully!")


if __name__ == "__main__":
    build()
