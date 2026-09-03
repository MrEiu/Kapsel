"""
KPS-Server: Cloud Sync & Identity Gateway for Kapsel Terminal Capsule.
Provides RESTful APIs for user registration, device pairing, and encrypted multi-device sync.
"""

from datetime import datetime
import json
import os
from pathlib import Path
import sqlite3
import sys
from typing import Any, Dict, Optional
from urllib.parse import parse_qs, urlparse

# Database path for cloud server
DB_PATH = Path(__file__).parent / "server.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS cloud_users (
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
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS user_sync_blobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                encrypted_payload TEXT NOT NULL,
                payload_hash TEXT NOT NULL,
                version INTEGER DEFAULT 1,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(username) REFERENCES cloud_users(username) ON DELETE CASCADE
            )
            """
        )
        conn.commit()


init_db()


def run_server(host: str = "0.0.0.0", port: int = 8000):
    from http.server import BaseHTTPRequestHandler, HTTPServer

    class ServerHandler(BaseHTTPRequestHandler):
        def _send_json(self, data, status: int = 200):
            payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Headers", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.end_headers()
            self.wfile.write(payload)

        def do_OPTIONS(self):
            self.send_response(204)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Headers", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.end_headers()

        def do_GET(self):
            parsed = urlparse(self.path)
            path = parsed.path.rstrip("/")
            params = parse_qs(parsed.query)

            if path in ("", "/health"):
                return self._send_json({"status": "ok", "service": "KPS-Server", "version": "1.0.0"})

            # Pull encrypted user sync blob
            if path == "/api/v1/user/sync":
                username = params.get("username", [None])[0]
                sync_key = params.get("sync_key", [None])[0]
                if not username or not sync_key:
                    return self._send_json({"error": "username and sync_key required"}, 401)

                with get_connection() as conn:
                    cur = conn.cursor()
                    cur.execute("SELECT * FROM cloud_users WHERE username = ? AND sync_key = ?", (username, sync_key))
                    user = cur.fetchone()
                    if not user:
                        return self._send_json({"error": "Unauthorized / invalid credentials"}, 401)

                    cur.execute("SELECT * FROM user_sync_blobs WHERE username = ?", (username,))
                    blob = cur.fetchone()
                    if not blob:
                        return self._send_json({"payload": None, "version": 0})
                    return self._send_json({
                        "payload": blob["encrypted_payload"],
                        "hash": blob["payload_hash"],
                        "version": blob["version"],
                        "updated_at": blob["updated_at"],
                    })

            return self._send_json({"error": "Not Found"}, 404)

        def do_POST(self):
            parsed = urlparse(self.path)
            path = parsed.path.rstrip("/")
            content_len = int(self.headers.get("Content-Length", 0))
            post_body = self.rfile.read(content_len)

            try:
                data = json.loads(post_body.decode("utf-8"))
            except Exception:
                return self._send_json({"error": "Invalid JSON payload"}, 400)

            # Register user
            if path == "/api/v1/auth/register":
                username = data.get("username", "").strip()
                sync_key = data.get("sync_key", "").strip()
                device_id = data.get("device_id", "").strip()
                email = data.get("email", "").strip()

                if not username or not sync_key:
                    return self._send_json({"error": "username and sync_key are required"}, 400)

                with get_connection() as conn:
                    cur = conn.cursor()
                    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    cur.execute(
                        """
                        INSERT INTO cloud_users (username, email, sync_key, device_id, last_synced_at)
                        VALUES (?, ?, ?, ?, ?)
                        ON CONFLICT(username) DO UPDATE SET
                            email=excluded.email,
                            sync_key=excluded.sync_key,
                            device_id=excluded.device_id,
                            last_synced_at=excluded.last_synced_at
                        """,
                        (username, email, sync_key, device_id, now),
                    )
                    conn.commit()
                return self._send_json({"success": True, "username": username, "registered_at": now})

            # Push encrypted user sync blob
            if path == "/api/v1/user/sync":
                username = data.get("username", "").strip()
                sync_key = data.get("sync_key", "").strip()
                encrypted_payload = data.get("payload", "")
                payload_hash = data.get("hash", "")

                with get_connection() as conn:
                    cur = conn.cursor()
                    cur.execute("SELECT * FROM cloud_users WHERE username = ? AND sync_key = ?", (username, sync_key))
                    if not cur.fetchone():
                        return self._send_json({"error": "Unauthorized / invalid sync_key"}, 401)

                    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    cur.execute(
                        """
                        INSERT INTO user_sync_blobs (username, encrypted_payload, payload_hash, updated_at)
                        VALUES (?, ?, ?, ?)
                        ON CONFLICT(username) DO UPDATE SET
                            encrypted_payload=excluded.encrypted_payload,
                            payload_hash=excluded.payload_hash,
                            version=user_sync_blobs.version + 1,
                            updated_at=excluded.updated_at
                        """,
                        (username, encrypted_payload, payload_hash, now),
                    )
                    conn.commit()
                return self._send_json({"success": True, "updated_at": now})

            return self._send_json({"error": "Not Found"}, 404)

        def log_message(self, format, *args):
            print(f"[KPS-Server] {self.address_string()} - {format % args}")

    server = HTTPServer((host, port), ServerHandler)
    print(f"🚀 KPS-Server Gateway running on http://{host}:{port}")
    print(f"   • Database: {DB_PATH}")
    print(f"   • Auth:     http://{host}:{port}/api/v1/auth/register")
    print(f"   • Sync:     http://{host}:{port}/api/v1/user/sync")
    server.serve_forever()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    run_server("0.0.0.0", port)
