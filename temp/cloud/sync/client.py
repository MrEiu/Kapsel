"""
Kapsel Cloud Sync Client.
Interacts with KPS-Server for user registration and encrypted cross-device roaming.
Uses Python standard library urllib.request (zero extra pip dependencies).
"""

import json
from typing import Any, Dict, Optional
import urllib.request
import urllib.error

from kapsel.storage.config import load_config
from kapsel.storage.logger import logger


class SyncClient:
    def __init__(self, endpoint: Optional[str] = None):
        cfg = load_config()
        self.endpoint = (endpoint or cfg.raw.get("cloud", {}).get("server_endpoint", "http://127.0.0.1:8000")).rstrip("/")
        self.timeout = cfg.raw.get("sync", {}).get("sync_timeout_seconds", 5)

    def register_user(self, username: str, sync_key: str, device_id: str, email: str = "") -> Dict[str, Any]:
        url = f"{self.endpoint}/api/v1/auth/register"
        payload = {
            "username": username,
            "sync_key": sync_key,
            "device_id": device_id,
            "email": email,
        }
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return {"success": True, "data": data}
        except urllib.error.URLError as e:
            logger.debug(f"Cloud register connection failed: {e}")
            return {"success": False, "error": f"无法连接到云端服务 ({self.endpoint}): {e.reason}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def ping_health(self) -> bool:
        url = f"{self.endpoint}/health"
        try:
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=2) as resp:
                return resp.status == 200
        except Exception:
            return False
