"""
Kapsel Device Identity & Hardware Fingerprinting.
Generates unique hardware device IDs (dev_...) and cryptographic sync keys.
"""

import hashlib
import platform
import secrets
import uuid


def get_device_id() -> str:
    """Generates a stable pseudo-unique hardware fingerprint string."""
    try:
        node = str(uuid.getnode())
        sys_name = platform.node() or platform.system()
        combined = f"{node}-{sys_name}-{platform.machine()}"
        digest = hashlib.sha256(combined.encode("utf-8")).hexdigest()[:12]
        return f"dev_{digest}"
    except Exception:
        return f"dev_{secrets.token_hex(6)}"


def generate_sync_key() -> str:
    """Generates a secure cryptographic roaming sync key."""
    return f"kps_sync_{secrets.token_urlsafe(24)}"
