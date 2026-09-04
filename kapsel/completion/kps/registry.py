"""
Kapsel Command Registry.
Unified Single Source of Truth for system management ('kapsel <cmd>')
and feature extension ('kps <cmd>') commands.
Used by autocompletion engines and command line dispatchers.
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional
from rich.console import Console


@dataclass
class KpsCommand:
    """
    Represents a registered command in the Kapsel ecosystem.
    scope: 'system' for core capsule management (kapsel <cmd>),
           'feature' for plugin/tooling extensions (kps <cmd>).
    """
    name: str
    help_text: str
    handler: Callable[[List[str], Optional[Console]], Optional[int]]
    subcommands: Dict[str, str] = field(default_factory=dict)
    usage: Optional[str] = None
    plugin_id: Optional[str] = None
    scope: str = "feature"  # "system" or "feature"


class KpsCommandRegistry:
    """Central registry storing and categorizing commands by scope."""

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
        scope: str = "feature",
    ) -> KpsCommand:
        """Registers a command into the registry."""
        cmd = KpsCommand(
            name=name.lower().strip(),
            help_text=help_text,
            handler=handler,
            subcommands=subcommands or {},
            usage=usage,
            plugin_id=plugin_id,
            scope=scope,
        )
        self._commands[cmd.name] = cmd
        return cmd

    def get(self, name: str, scope: Optional[str] = None) -> Optional[KpsCommand]:
        """
        Retrieves a command by name, optionally filtering by scope.
        """
        cmd = self._commands.get(name.lower().strip())
        if cmd and scope and cmd.scope != scope:
            return None
        return cmd

    def list_commands(self) -> List[KpsCommand]:
        """Returns all registered commands sorted by name."""
        return sorted(self._commands.values(), key=lambda c: c.name)

    def list_system_commands(self) -> List[KpsCommand]:
        """Returns commands belonging to the 'system' scope ('kapsel <cmd>')."""
        return sorted(
            [c for c in self._commands.values() if c.scope == "system"],
            key=lambda c: c.name,
        )

    def list_feature_commands(self) -> List[KpsCommand]:
        """Returns commands belonging to the 'feature' scope ('kps <cmd>')."""
        return sorted(
            [c for c in self._commands.values() if c.scope == "feature"],
            key=lambda c: c.name,
        )

    def remove_by_plugin(self, plugin_id: str) -> None:
        """Removes all commands registered by a specific plugin."""
        self._commands = {
            k: v for k, v in self._commands.items() if v.plugin_id != plugin_id
        }


# Global registry singleton
_GLOBAL_REGISTRY: Optional[KpsCommandRegistry] = None


def get_kps_registry() -> KpsCommandRegistry:
    """Gets or initializes the global command registry."""
    global _GLOBAL_REGISTRY
    if _GLOBAL_REGISTRY is None:
        _GLOBAL_REGISTRY = KpsCommandRegistry()
        # Auto-register core built-in system commands
        from kapsel.completion.kps.builtins import register_builtins
        register_builtins(_GLOBAL_REGISTRY)
    return _GLOBAL_REGISTRY
