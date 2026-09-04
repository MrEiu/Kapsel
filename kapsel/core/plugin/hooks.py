"""
Kapsel Plugin System - Hooks Specification.
Defines standard extension hook types and callback signatures.
"""

from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple


class HookType(str, Enum):
    """Available extension hook points in Kapsel Core."""
    # Triggered when core is ready, before user prompt
    ON_READY = "on_ready"

    # Injects extra completion candidates into prompt completion
    # Signature: (text_before_cursor: str) -> List[dict]
    # dict format: {"text": str, "display": str, "display_meta": str}
    PROVIDE_COMPLETIONS = "provide_completions"

    # Pre-execution filter/transformer (e.g. command translation/routing)
    # Signature: (raw_command: str) -> Tuple[bool, str]
    # Returns (is_handled, transformed_command)
    FILTER_COMMAND = "filter_command"

    # Triggered immediately before executing a command
    # Signature: (command: str) -> None
    ON_BEFORE_EXECUTE = "on_before_execute"

    # Triggered after executing a command (e.g. for cloud sync or metrics)
    # Signature: (command: str, exit_code: int, duration_ms: float) -> None
    ON_AFTER_EXECUTE = "on_after_execute"

    # Triggered during shell exit / cleanup
    ON_SHUTDOWN = "on_shutdown"
