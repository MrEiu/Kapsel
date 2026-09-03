"""
Kapsel user profile and authentication state manager.
Manages ~/.kapsel/user.json for multi-system cloud synchronization.
"""

from dataclasses import asdict, dataclass
from datetime import datetime
import json
from pathlib import Path
import platform
import secrets
import socket
from typing import Any, Dict, Optional
import uuid

from kapsel.storage.logger import get_kapsel_dir, logger


def get_user_file_path() -> Path:
    return get_kapsel_dir() / "user.json"


@dataclass
class UserProfile:
    username: str
    email: str
    device_id: str
    device_name: str
    device_os: str
    sync_key: str
    token: str
    created_at: str
    cloud_server: str = "https://api.kapsel.dev"
    sync_enabled: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UserProfile":
        return cls(
            username=data.get("username", "anonymous"),
            email=data.get("email", ""),
            device_id=data.get("device_id", str(uuid.uuid4())),
            device_name=data.get("device_name", socket.gethostname()),
            device_os=data.get("device_os", f"{platform.system()} {platform.machine()}"),
            sync_key=data.get("sync_key", ""),
            token=data.get("token", ""),
            created_at=data.get("created_at", datetime.now().isoformat()),
            cloud_server=data.get("cloud_server", "https://api.kapsel.dev"),
            sync_enabled=data.get("sync_enabled", True),
        )


class UserManager:
    """Manages local user identity and multi-system sync credentials."""

    @staticmethod
    def get_current_user() -> Optional[UserProfile]:
        """Loads the current user profile if registered."""
        path = get_user_file_path()
        if not path.exists():
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return UserProfile.from_dict(data)
        except Exception as e:
            logger.error(f"Failed to read user profile from {path}: {e}")
            return None

    @staticmethod
    def register(
        username: str,
        email: str = "",
        cloud_server: str = "https://api.kapsel.dev",
    ) -> UserProfile:
        """
        Creates a new user profile, generates cryptographic sync keys and device fingerprint,
        and saves credentials to ~/.kapsel/user.json.
        """
        device_id = f"dev_{uuid.uuid4().hex[:12]}"
        device_name = socket.gethostname()
        device_os = f"{platform.system()} {platform.machine()}"
        sync_key = f"kps_sync_{secrets.token_hex(16)}"
        token = f"kps_sec_{secrets.token_urlsafe(32)}"
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        profile = UserProfile(
            username=username.strip().lstrip("@"),
            email=email.strip(),
            device_id=device_id,
            device_name=device_name,
            device_os=device_os,
            sync_key=sync_key,
            token=token,
            created_at=now_str,
            cloud_server=cloud_server,
            sync_enabled=True,
        )

        path = get_user_file_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(profile.to_dict(), f, indent=2, ensure_ascii=False)
            logger.info(f"Registered Kapsel user '@{profile.username}' at {path}")
        except Exception as e:
            logger.error(f"Failed to write user profile to {path}: {e}")

        return profile

    @staticmethod
    def logout() -> bool:
        """Removes user profile file."""
        path = get_user_file_path()
        if path.exists():
            try:
                path.unlink()
                logger.info("Logged out user and removed user.json")
                return True
            except Exception as e:
                logger.error(f"Failed to remove user.json: {e}")
                return False
        return False
