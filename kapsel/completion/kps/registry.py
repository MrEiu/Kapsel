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
    Shared uniformly across 'kapsel <cmd>' and 'kps <cmd>'.
    """
    name: str
    help_text: str
    handler: Callable[[List[str], Optional[Console]], Optional[int]]
    subcommands: Dict[str, str] = field(default_factory=dict)
    usage: Optional[str] = None
    plugin_id: Optional[str] = None
    scope: str = "default"
    hidden: bool = False


class KpsCommandRegistry:
    """Central registry storing Kapsel commands with distinct system and feature scopes."""

    def __init__(self):
        # Keyed by command name (lowercase)
        self._commands: Dict[str, KpsCommand] = {}
        self._system_commands: Dict[str, KpsCommand] = {}
        self._feature_commands: Dict[str, KpsCommand] = {}

    def register(
        self,
        name: str,
        handler: Callable[[List[str], Optional[Console]], Optional[int]],
        help_text: str,
        subcommands: Optional[Dict[str, str]] = None,
        usage: Optional[str] = None,
        plugin_id: Optional[str] = None,
        scope: str = "default",
        hidden: bool = False,
    ) -> KpsCommand:
        """Registers a command into the registry under its designated scope."""
        clean_name = name.lower().strip()
        cmd = KpsCommand(
            name=clean_name,
            help_text=help_text,
            handler=handler,
            subcommands=subcommands or {},
            usage=usage,
            plugin_id=plugin_id,
            scope=scope,
            hidden=hidden,
        )

        is_system = (scope == "system") or (scope == "default" and not plugin_id)
        if is_system:
            self._system_commands[clean_name] = cmd
        else:
            self._feature_commands[clean_name] = cmd

        self._commands[clean_name] = cmd
        return cmd

    def get_system_command(self, name: str) -> Optional[KpsCommand]:
        """Retrieves a system management command (kapsel <cmd>)."""
        clean_name = name.lower().strip()
        return self._system_commands.get(clean_name)

    def get_feature_command(self, name: str) -> Optional[KpsCommand]:
        """Retrieves a plugin tool command (kps <cmd>)."""
        clean_name = name.lower().strip()
        return self._feature_commands.get(clean_name)

    def get(self, name: str, scope: Optional[str] = None) -> Optional[KpsCommand]:
        """Retrieves a command by name from the registry, respecting scope if given."""
        clean_name = name.lower().strip()
        if scope == "system":
            return self._system_commands.get(clean_name)
        elif scope == "feature":
            return self._feature_commands.get(clean_name)
        return self._feature_commands.get(clean_name) or self._system_commands.get(clean_name)

    def list_commands(self, include_hidden: bool = False) -> List[KpsCommand]:
        """Returns all registered commands sorted by name."""
        cmds = self._commands.values()
        if not include_hidden:
            cmds = [c for c in cmds if not c.hidden]
        return sorted(cmds, key=lambda c: c.name)

    def list_system_commands(self, include_hidden: bool = False) -> List[KpsCommand]:
        """Returns all system platform commands (kapsel <cmd>)."""
        cmds = self._system_commands.values()
        if not include_hidden:
            cmds = [c for c in cmds if not c.hidden]
        return sorted(cmds, key=lambda c: c.name)

    def list_feature_commands(self, include_hidden: bool = False) -> List[KpsCommand]:
        """Returns all plugin/tool feature commands (kps <cmd>)."""
        cmds = self._feature_commands.values()
        if not include_hidden:
            cmds = [c for c in cmds if not c.hidden]
        return sorted(cmds, key=lambda c: c.name)

    def remove_by_plugin(self, plugin_id: str) -> None:
        """Removes all commands registered by a specific plugin."""
        self._commands = {
            k: v for k, v in self._commands.items() if v.plugin_id != plugin_id
        }
        self._feature_commands = {
            k: v for k, v in self._feature_commands.items() if v.plugin_id != plugin_id
        }



# Global registry singleton
_GLOBAL_REGISTRY: Optional[KpsCommandRegistry] = None


def get_kps_registry() -> KpsCommandRegistry:
    """Gets or initializes the global command registry."""
    global _GLOBAL_REGISTRY
    if _GLOBAL_REGISTRY is None:
        _GLOBAL_REGISTRY = KpsCommandRegistry()
        # Auto-register core built-in commands
        from kapsel.completion.kps.builtins import register_builtins
        register_builtins(_GLOBAL_REGISTRY)
    return _GLOBAL_REGISTRY
