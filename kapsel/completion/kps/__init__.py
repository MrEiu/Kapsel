"""
Kapsel Command Subsystem.
Integrates command registration and dispatching with autocompletion.
"""

from kapsel.completion.kps.dispatcher import dispatch_kps
from kapsel.completion.kps.registry import (
    KpsCommand,
    KpsCommandRegistry,
    get_kps_registry,
)

__all__ = [
    "KpsCommand",
    "KpsCommandRegistry",
    "get_kps_registry",
    "dispatch_kps",
]
