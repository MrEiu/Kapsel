"""
Kapsel Command Mapping Facade.
Delegates command loading and matching directly to RegistryIndexer and folder-based storage.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from kapsel.storage.logger import get_kapsel_dir
from kapsel.storage.registry.indexer import CommandEntry, RegistryIndexer, get_registry_indexer


class CommandRegistry:
    def __init__(self, commands: Optional[List[CommandEntry]] = None):
        self.indexer = get_registry_indexer()
        if commands is not None:
            self._commands = commands
        else:
            self._commands = self.indexer.list_all_commands()

    @property
    def commands(self) -> List[CommandEntry]:
        return self._commands

    def get(self, alias: str) -> Optional[CommandEntry]:
        entry, _ = self.indexer.find_best_match(alias) or (None, "")
        if entry and entry.alias == alias:
            return entry
        for c in self._commands:
            if c.alias == alias:
                return c
        return None

    def find_best_match(self, input_text: str) -> Optional[Tuple[CommandEntry, str]]:
        return self.indexer.find_best_match(input_text)

    def list_all(self) -> List[CommandEntry]:
        return self.indexer.list_all_commands()


def get_commands_path() -> Path:
    return get_kapsel_dir() / "commands.yaml"


def load_commands() -> CommandRegistry:
    """Loads active commands directly via RegistryIndexer."""
    return CommandRegistry()
