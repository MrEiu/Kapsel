"""
Kapsel core engine package.
"""

from kapsel.core.detector import EnvironmentDetector, detector
from kapsel.core.engine import DispatchResult, DualStateEngine
from kapsel.core.executor import CommandExecutor, ExecutionSummary
from kapsel.core.plugin import (
    HookType,
    KapselPlugin,
    PluginContext,
    PluginManager,
    PluginManifest,
)

__all__ = [
    "EnvironmentDetector",
    "detector",
    "CommandExecutor",
    "ExecutionSummary",
    "DualStateEngine",
    "DispatchResult",
    "KapselPlugin",
    "PluginManifest",
    "PluginContext",
    "HookType",
    "PluginManager",
]
