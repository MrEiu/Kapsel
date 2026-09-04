"""
Kapsel Plugin System.
Exposes base classes, metadata schemas, hooks, and manager.
"""

from kapsel.core.plugin.base import KapselPlugin, PluginManifest
from kapsel.core.plugin.context import PluginContext
from kapsel.core.plugin.hooks import HookType
from kapsel.core.plugin.manager import PluginManager

__all__ = [
    "KapselPlugin",
    "PluginManifest",
    "PluginContext",
    "HookType",
    "PluginManager",
]
