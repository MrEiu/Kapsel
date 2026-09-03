"""
Kapsel core engine package.
"""

from kapsel.core.detector import EnvironmentDetector, detector
from kapsel.core.router import CommandRouter, TranslationResult
from kapsel.core.executor import CommandExecutor, ExecutionSummary
from kapsel.core.engine import DualStateEngine, DispatchResult

__all__ = [
    "EnvironmentDetector",
    "detector",
    "CommandRouter",
    "TranslationResult",
    "CommandExecutor",
    "ExecutionSummary",
    "DualStateEngine",
    "DispatchResult",
]
