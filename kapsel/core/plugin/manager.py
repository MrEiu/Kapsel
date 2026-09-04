"""
Kapsel Plugin System - Plugin Manager.
Handles plugin discovery, lifecycle, hook dispatching, and crash-proof execution boundaries.
"""

import importlib.util
from pathlib import Path
import sys
from typing import Any, Callable, Dict, List, Optional, Tuple

from kapsel.core.detector import EnvironmentDetector, detector
from kapsel.core.plugin.base import KapselPlugin
from kapsel.core.plugin.context import PluginContext
from kapsel.core.plugin.hooks import HookType
from kapsel.storage.config import KapselConfig
from kapsel.storage.logger import logger


class PluginManager:
    """Manages the full lifecycle of Kapsel plugins."""

    def __init__(
        self,
        config: KapselConfig,
        kps_command_register_fn: Callable[..., Any],
        env_detector: Optional[EnvironmentDetector] = None,
    ):
        self.config = config
        self.detector = env_detector or detector
        self.kps_command_register_fn = kps_command_register_fn

        self.plugins: Dict[str, KapselPlugin] = {}
        self.hooks: Dict[HookType, List[Callable]] = {h: [] for h in HookType}

    def load_all_plugins(self) -> None:
        """Discovers and initializes enabled plugins from configured directories."""
        plugin_dirs = self._resolve_plugin_dirs()
        for p_dir in plugin_dirs:
            if not p_dir.is_dir():
                continue
            for item in p_dir.iterdir():
                if item.is_dir() and (item / "__init__.py").exists():
                    self._load_plugin_from_directory(item)

    def _resolve_plugin_dirs(self) -> List[Path]:
        """
        Resolves universal directories to load plugins from.
        All plugins reside in the user global plugin directory (~/.kapsel/plugins or configured data dir).
        """
        dirs: List[Path] = []

        # User global plugin directory (cross-project & universal)
        user_plugins = self.config.get_data_dir() / "plugins"
        user_plugins.mkdir(parents=True, exist_ok=True)
        dirs.append(user_plugins)

        # Custom configured plugin directories
        for custom_path in getattr(self.config, "plugin_dirs", []):
            p = Path(custom_path).expanduser()
            if p.exists() and p not in dirs:
                dirs.append(p)

        return dirs

    def _load_plugin_from_directory(self, plugin_path: Path) -> None:
        """Dynamically imports and initializes a plugin folder."""
        plugin_name = plugin_path.name
        enabled_list = getattr(self.config, "enabled_plugins", None)
        if enabled_list and plugin_name not in enabled_list:
            logger.debug(f"Skipping disabled plugin: {plugin_name}")
            return

        try:
            init_file = plugin_path / "__init__.py"
            module_name = f"kapsel_plugin_{plugin_name}"
            spec = importlib.util.spec_from_file_location(module_name, init_file)
            if not spec or not spec.loader:
                return

            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)

            # Find KapselPlugin subclasses
            plugin_cls = None
            if hasattr(module, "Plugin") and issubclass(module.Plugin, KapselPlugin):
                plugin_cls = module.Plugin
            else:
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (
                        isinstance(attr, type)
                        and issubclass(attr, KapselPlugin)
                        and attr is not KapselPlugin
                    ):
                        plugin_cls = attr
                        break

            if plugin_cls:
                plugin_instance: KapselPlugin = plugin_cls()
                ctx = PluginContext(
                    plugin_id=plugin_instance.manifest.id,
                    config=self.config,
                    hook_registry=self.hooks,
                    kps_command_register_fn=self.kps_command_register_fn,
                    env_detector=self.detector,
                )
                plugin_instance.on_load(ctx)
                self.plugins[plugin_instance.manifest.id] = plugin_instance
                logger.info(
                    f"Successfully loaded plugin: [{plugin_instance.manifest.name} "
                    f"v{plugin_instance.manifest.version}]"
                )
        except Exception as e:
            # Crash-proof boundary: A faulty plugin must never crash Kapsel Core
            logger.exception(f"Failed to load plugin from {plugin_path}: {e}")

    def trigger_hook(self, hook_type: HookType, *args, **kwargs) -> List[Any]:
        """Safely invokes all callbacks registered for a given hook."""
        results: List[Any] = []
        for cb in self.hooks.get(hook_type, []):
            try:
                res = cb(*args, **kwargs)
                results.append(res)
            except Exception as e:
                logger.exception(f"Error in hook callback ({hook_type.value}): {e}")
        return results

    def filter_command(self, raw_command: str) -> Tuple[bool, str]:
        """
        Executes FILTER_COMMAND hooks sequentially.
        If a plugin handles/translates the command, returns (True, translated_cmd).
        """
        current_cmd = raw_command
        handled = False

        for cb in self.hooks.get(HookType.FILTER_COMMAND, []):
            try:
                is_handled, new_cmd = cb(current_cmd)
                if is_handled:
                    handled = True
                    current_cmd = new_cmd
            except Exception as e:
                logger.exception(f"Error executing FILTER_COMMAND hook: {e}")

        return handled, current_cmd

    def get_plugin_completions(self, text_before_cursor: str) -> List[dict]:
        """Collects dynamic completion candidates from plugins."""
        candidates: List[dict] = []
        for cb in self.hooks.get(HookType.PROVIDE_COMPLETIONS, []):
            try:
                res = cb(text_before_cursor)
                if isinstance(res, list):
                    candidates.extend(res)
            except Exception as e:
                logger.exception(f"Error executing PROVIDE_COMPLETIONS hook: {e}")
        return candidates

    def unload_all(self) -> None:
        """Safely tears down all active plugins."""
        for p_id, plugin in list(self.plugins.items()):
            try:
                plugin.on_unload()
            except Exception as e:
                logger.exception(f"Error unloading plugin {p_id}: {e}")
        self.plugins.clear()
        self.hooks = {h: [] for h in HookType}
