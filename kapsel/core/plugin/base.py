"""
Kapsel Plugin System - Base Specification.
Defines the core abstract plugin interface and metadata models.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from kapsel.core.plugin.context import PluginContext


@dataclass
class PluginManifest:
    """Metadata describing a Kapsel plugin."""
    id: str
    name: str
    version: str
    description: str = ""
    author: str = ""
    homepage: str = ""
    min_kapsel_version: str = "0.1.0"
    dependencies: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)


class KapselPlugin(ABC):
    """
    Abstract base class that all Kapsel plugins must inherit from.
    """
    manifest: PluginManifest

    def __init__(self, manifest: Optional[PluginManifest] = None):
        if manifest:
            self.manifest = manifest
        elif not hasattr(self, "manifest"):
            raise ValueError(f"Plugin {self.__class__.__name__} must define a manifest.")

    @abstractmethod
    def on_load(self, context: "PluginContext") -> None:
        """
        Called when the plugin is loaded into the Kapsel engine.
        Use this method to register kps commands, hooks, and initialize state.
        """
        pass

    def on_unload(self) -> None:
        """
        Called when the plugin is being unloaded or Kapsel is shutting down.
        Clean up resources, open files, or network connections here.
        """
        pass