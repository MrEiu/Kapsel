"""
Kapsel Command Registry.
Unified Single Source of Truth for 'kps' subcommands - used by both
interactive autocompletion menus and command line dispatchers.
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional
from rich.console import Console


@dataclass
class KpsCommand:
    """Represents a registered 'kps' command."""
    name: str
    help_text: str
    handler: Callable[[List[str], Optional[Console]], Optional[int]]
    subcommands: Dict[str, str] = field(default_factory=dict)
    usage: Optional[str] = None
    plugin_id: Optional[str] = None


class KpsCommandRegistry:
    """Central registry storing and serving all kps subcommands."""

    def __init__(self):
        self._commands: Dict[str, KpsCommand] = {}

    def register(
        self,
        name: str,
        handler: Callable[[List[str], Optional[Console]], Optional[int]],
        help_text: str,
        subcommands: Optional[Dict[str, str]] = None,
        usage: Optional[str] = None,
        plugin_id: Optional[str] = None,
    ) -> KpsCommand:
        """Registers a command."""
        cmd = KpsCommand(
            name=name.lower().strip(),
            help_text=help_text,
            handler=handler,
            subcommands=subcommands or {},
            usage=usage,
            plugin_id=plugin_id,
        )
        self._commands[cmd.name] = cmd
        return cmd

    def get(self, name: str) -> Optional[KpsCommand]:
        """Retrieves a command by its primary name or alias."""
        return self._commands.get(name.lower().strip())

    def list_commands(self) -> List[KpsCommand]:
        """Returns all registered commands sorted by name."""
        return sorted(self._commands.values(), key=lambda c: c.name)

    def remove_by_plugin(self, plugin_id: str) -> None:
        """Removes all commands registered by a specific plugin."""
        self._commands = {
            k: v for k, v in self._commands.items() if v.plugin_id != plugin_id
        }


# Global registry singleton
_GLOBAL_REGISTRY: Optional[KpsCommandRegistry] = None


def get_kps_registry() -> KpsCommandRegistry:
    """Gets or initializes the global kps command registry."""
    global _GLOBAL_REGISTRY
    if _GLOBAL_REGISTRY is None:
        _GLOBAL_REGISTRY = KpsCommandRegistry()
        # Auto-register core builtins
        from kapsel.completion.kps.builtins import register_builtins
        register_builtins(_GLOBAL_REGISTRY)
    return _GLOBAL_REGISTRY
