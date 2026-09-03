"""
Kapsel Folder-Based Registry Storage & Fast Indexer.
Aligns with Git repository synchronization (manifests/ and mappings/ JSON files).
"""

from kapsel.storage.registry.indexer import CommandEntry, RegistryIndexer, get_registry_indexer
from kapsel.storage.registry.loader import get_registry_dir, load_all_manifests, load_all_mappings

__all__ = [
    "get_registry_dir",
    "load_all_manifests",
    "load_all_mappings",
    "CommandEntry",
    "RegistryIndexer",
    "get_registry_indexer",
]
