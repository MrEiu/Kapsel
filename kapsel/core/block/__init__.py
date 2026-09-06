"""
Kapsel Command Block Module.
Provides Block data models, BlockRegistry, and BlockRunner (kp).
"""

from kapsel.core.block.model import BlockStatus, CommandBlock
from kapsel.core.block.registry import BlockRegistry, get_block_registry
from kapsel.core.block.runner import (
    execute_parallel_block,
    execute_sequential_block,
    split_commands,
)

__all__ = [
    "BlockStatus",
    "CommandBlock",
    "BlockRegistry",
    "get_block_registry",
    "execute_sequential_block",
    "execute_parallel_block",
    "split_commands",
]
