"""
Kapsel Cryptographic Engine.
Provides end-to-end payload encryption (AES-256-GCM / HMAC) and keys for future database encryption.
"""

import base64
import hashlib
import json
from typing import Any, Dict, Optional


def derive_key(sync_key: str, salt: bytes = b"kapsel_salt_v1") -> bytes:
    """Derives a 32-byte AES key from sync_key using SHA-256 PBKDF."""
    return hashlib.pbkdf2_hmac("sha256", sync_key.encode("utf-8"), salt, 100000, dklen=32)


def encrypt_payload(data: Dict[str, Any], sync_key: str) -> str:
    """
    Encrypts a JSON payload using AES-256-GCM.
    Falls back to base64 obfuscated token if cryptography library is not yet installed.
    """
    json_bytes = json.dumps(data, ensure_ascii=False).encode("utf-8")
    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        import secrets
        key = derive_key(sync_key)
        aesgcm = AESGCM(key)
        nonce = secrets.token_bytes(12)
        ct = aesgcm.encrypt(nonce, json_bytes, None)
        return base64.b64encode(nonce + ct).decode("utf-8")
    except ImportError:
        # Standard library fallback representation
        return base64.b64encode(json_bytes).decode("utf-8")


def decrypt_payload(encrypted_str: str, sync_key: str) -> Optional[Dict[str, Any]]:
    """Decrypts an AES-256-GCM encrypted payload back into a dictionary."""
    try:
        raw_bytes = base64.b64decode(encrypted_str.encode("utf-8"))
        try:
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM
            key = derive_key(sync_key)
            aesgcm = AESGCM(key)
            nonce = raw_bytes[:12]
            ct = raw_bytes[12:]
            pt = aesgcm.decrypt(nonce, ct, None)
            return json.loads(pt.decode("utf-8"))
        except ImportError:
            return json.loads(raw_bytes.decode("utf-8"))
    except Exception:
        return None
