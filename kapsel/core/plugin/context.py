"""
Kapsel Plugin System - Context API.
Provides controlled and safe access to host core services for plugins.
"""

from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from kapsel.core.detector import EnvironmentDetector, detector
from kapsel.core.plugin.hooks import HookType
from kapsel.storage.config import KapselConfig
from kapsel.storage.logger import logger


class PluginContext:
    """
    The Host API context provided to a plugin during `on_load(context)`.
    Enforces security boundaries and structured extension registration.
    """

    def __init__(
        self,
        plugin_id: str,
        config: KapselConfig,
        hook_registry: Dict[HookType, List[Callable]],
        kps_command_register_fn: Callable[..., Any],
        env_detector: Optional[EnvironmentDetector] = None,
    ):
        self.plugin_id = plugin_id
        self._config = config
        self._hook_registry = hook_registry
        self._kps_command_register_fn = kps_command_register_fn
        self.environment = env_detector or detector
        self.logger = logger

    @property
    def plugin_data_dir(self) -> Path:
        """Isolated persistent directory for this plugin to store files."""
        base_dir = self._config.get_data_dir() / "plugins_data" / self.plugin_id
        base_dir.mkdir(parents=True, exist_ok=True)
        return base_dir

    def register_kps_command(
        self,
        name: str,
        handler: Callable[..., Optional[int]],
        help_text: str,
        subcommands: Optional[Dict[str, str]] = None,
        usage: Optional[str] = None,
    ) -> None:
        """
        Registers a new 'kps <name>' subcommand.
        Automatically exposes it to both autocompletion and CLI dispatching.
        """
        self._kps_command_register_fn(
            name=name,
            handler=handler,
            help_text=help_text,
            subcommands=subcommands,
            usage=usage,
            plugin_id=self.plugin_id,
        )

    def register_hook(self, hook_type: HookType, callback: Callable) -> None:
        """Registers an extension callback hook."""
        if hook_type not in self._hook_registry:
            self._hook_registry[hook_type] = []
        self._hook_registry[hook_type].append(callback)
        self.logger.debug(f"[Plugin:{self.plugin_id}] Hook registered: {hook_type.value}")
