"""
Kapsel Command Block Data Model.
Represents an atomic command execution unit or concurrent track.
All comments and docstrings are in English.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class BlockStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


@dataclass
class CommandBlock:
    """Represents a single command execution block or batch execution."""

    id: int
    command: str
    sub_commands: List[str] = field(default_factory=list)
    is_concurrent: bool = False
    cwd: str = ""
    timestamp: float = 0.0
    duration_ms: int = 0
    exit_code: int = 0
    status: BlockStatus = BlockStatus.SUCCESS
    output_text: str = ""

    @property
    def success(self) -> bool:
        return self.exit_code == 0
