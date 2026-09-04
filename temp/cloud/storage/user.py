"""
Kapsel User Profile Storage (Facade).
Maintains full backward compatibility by delegating directly to the centralized SQLite UserDatabase (~/.kapsel/user.db).
"""

from typing import Any, Dict, Optional

from kapsel.storage.user_db import get_user_db
from kapsel.sync.device import get_device_id, generate_sync_key


def get_current_user() -> Optional[Dict[str, Any]]:
    return get_user_db().get_active_user()


def save_user(username: str, email: str = "", sync_key: Optional[str] = None) -> Dict[str, Any]:
    db = get_user_db()
    active = db.get_active_user()
    device_id = active.get("device_id") if active else get_device_id()
    final_sync_key = sync_key.strip() if sync_key else (active.get("sync_key") if active else generate_sync_key())
    
    db.save_user(username=username, email=email, sync_key=final_sync_key, device_id=device_id)
    return {
        "username": username,
        "email": email,
        "device_id": device_id,
        "sync_key": final_sync_key,
    }


def logout_user() -> bool:
    return get_user_db().logout_active_user()
