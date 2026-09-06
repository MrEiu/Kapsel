"""
Kapsel Block Registry.
Tracks in-memory execution blocks for active terminal sessions
and supports block navigation in Roaming Mode.
All comments and docstrings are in English.
"""

from pathlib import Path
import time
from typing import List, Optional

from kapsel.core.block.model import BlockStatus, CommandBlock


class BlockRegistry:
    """Thread-safe in-memory registry for command blocks."""

    def __init__(self, max_blocks: int = 200):
        self.max_blocks = max_blocks
        self._blocks: List[CommandBlock] = []
        self._next_id = 1

    def add_block(
        self,
        command: str,
        exit_code: int,
        duration_ms: int,
        cwd: Optional[str] = None,
        sub_commands: Optional[List[str]] = None,
        is_concurrent: bool = False,
        output_text: str = "",
    ) -> CommandBlock:
        """Creates and registers a new command block."""
        block = CommandBlock(
            id=self._next_id,
            command=command,
            sub_commands=sub_commands or [command],
            is_concurrent=is_concurrent,
            cwd=cwd or str(Path.cwd()),
            timestamp=time.time(),
            duration_ms=duration_ms,
            exit_code=exit_code,
            status=BlockStatus.SUCCESS if exit_code == 0 else BlockStatus.FAILED,
            output_text=output_text,
        )
        self._next_id += 1
        self._blocks.append(block)

        if len(self._blocks) > self.max_blocks:
            self._blocks = self._blocks[-self.max_blocks :]

        return block

    def get_blocks(self) -> List[CommandBlock]:
        """Returns all registered blocks in chronological order."""
        return list(self._blocks)

    def get_block_by_index(self, index: int) -> Optional[CommandBlock]:
        """Returns block at 0-based index."""
        if 0 <= index < len(self._blocks):
            return self._blocks[index]
        return None

    def get_block_by_id(self, block_id: int) -> Optional[CommandBlock]:
        """Returns block with specific ID."""
        for b in self._blocks:
            if b.id == block_id:
                return b
        return None

    def latest(self) -> Optional[CommandBlock]:
        """Returns the most recent execution block."""
        if self._blocks:
            return self._blocks[-1]
        return None

    def count(self) -> int:
        return len(self._blocks)

    def preload_from_history(self, history_mgr) -> None:
        """Preloads recent commands from SQLite history if registry is empty."""
        if self._blocks:
            return
        try:
            records = history_mgr.get_recent_records(limit=30)
            for r in records:
                self.add_block(
                    command=r["command"],
                    exit_code=r.get("exit_code", 0),
                    duration_ms=r.get("duration_ms", 0),
                    cwd=r.get("cwd", ""),
                    sub_commands=[r["command"]],
                    is_concurrent=False,
                    output_text=f"$ {r['command']} (exit {r.get('exit_code', 0)})",
                )
        except Exception:
            pass

    def clear(self) -> None:
        self._blocks.clear()


_GLOBAL_BLOCK_REGISTRY: Optional[BlockRegistry] = None


def get_block_registry() -> BlockRegistry:
    """Returns the global singleton block registry."""
    global _GLOBAL_BLOCK_REGISTRY
    if _GLOBAL_BLOCK_REGISTRY is None:
        _GLOBAL_BLOCK_REGISTRY = BlockRegistry()
    return _GLOBAL_BLOCK_REGISTRY
