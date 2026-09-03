"""
Dynamic subcommands loader for tool CLI completion.
Retrieves tool subcommands (e.g. git, scoop, docker, npm) directly from RegistryIndexer.
Zero hardcoding in code.
"""

from typing import List, Tuple

from kapsel.storage.registry.indexer import get_registry_indexer


def get_subcommands_for_tool(tool: str) -> List[Tuple[str, str]]:
    """Returns list of (subcommand, description) for the requested tool from registry index."""
    indexer = get_registry_indexer()
    return indexer.get_commands_for_tool(tool)
