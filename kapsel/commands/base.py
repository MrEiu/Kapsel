"""
Kapsel Commands Base Architecture.
Defines execution contracts and helpers for all built-in CLI commands.
"""

from typing import List, Optional
from rich.console import Console


class BaseCommand:
    """Base interface for Kapsel built-in commands."""

    name: str = ""
    description: str = ""
    aliases: List[str] = []

    def execute(self, args: List[str], console: Optional[Console] = None) -> int:
        raise NotImplementedError
