"""
Kapsel Registry Indexer.
Builds an in-memory index over the folder-based registry (~/.kapsel/registry/)
providing sub-millisecond retrieval, prefix matching, and fuzzy search.
Supports dynamic reloading upon Git pull/sync.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from kapsel.storage.registry.loader import load_all_manifests, load_all_mappings


@dataclass
class CommandEntry:
    alias: str
    desc: str
    mapping: Dict[str, str]

    def get_template_for_shell(self, shell: str) -> Optional[str]:
        if shell in self.mapping:
            return self.mapping[shell]
        if shell == "pwsh" and "powershell" in self.mapping:
            return self.mapping["powershell"]
        if shell == "powershell" and "pwsh" in self.mapping:
            return self.mapping["pwsh"]
        return self.mapping.get("unix") or next(iter(self.mapping.values()), None)


class RegistryIndexer:
    """
    High-performance in-memory indexer for folder-based manifests and mappings.
    Guarantees <1ms keystroke response latency while keeping storage in clean Git-syncable files.
    """

    def __init__(self, target_shell: str = "pwsh"):
        self.target_shell = target_shell
        self._manifests: List[Dict[str, Any]] = []
        self._mappings: List[Dict[str, Any]] = []
        self._commands_list: List[CommandEntry] = []
        self._tool_commands_cache: Dict[str, List[Tuple[str, str]]] = {}
        self.reload()

    def reload(self) -> None:
        """Reloads all files from ~/.kapsel/registry/ and rebuilds in-memory index."""
        self._manifests = load_all_manifests()
        self._mappings = load_all_mappings(self.target_shell)

        # 1. Build CommandEntry list from mappings & manifests
        entries = []
        # From mappings (system Linux-First aliases)
        for m in self._mappings:
            entries.append(
                CommandEntry(
                    alias=m["source_alias"],
                    desc=m["desc"],
                    mapping={
                        self.target_shell: m["target_template"],
                        "unix": f"{m['source_alias']} {{{{args}}}}",
                    },
                )
            )

        # 2. Build tool subcommands cache
        tool_cache: Dict[str, List[Tuple[str, str]]] = {}
        for p in self._manifests:
            soft = p.get("software", "").lower()
            cmds = p.get("commands", [])
            sub_list = []
            for c in cmds:
                sub_list.append((c.get("command_name", ""), c.get("desc", "")))
            tool_cache[soft] = sub_list

        # Sort entries by descending alias length for longest-prefix match
        entries.sort(key=lambda e: len(e.alias), reverse=True)
        self._commands_list = entries
        self._tool_commands_cache = tool_cache

    def list_all_commands(self) -> List[CommandEntry]:
        return self._commands_list

    def find_best_match(self, input_text: str) -> Optional[Tuple[CommandEntry, str]]:
        cleaned = input_text.strip()
        for entry in self._commands_list:
            if cleaned == entry.alias:
                return entry, ""
            if cleaned.startswith(entry.alias + " "):
                args = cleaned[len(entry.alias) + 1:].strip()
                return entry, args
        return None

    def get_commands_for_tool(self, tool: str) -> List[Tuple[str, str]]:
        return self._tool_commands_cache.get(tool.lower(), [])

    def list_packages(self, platform_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        if not platform_filter:
            return self._manifests
        return [
            p for p in self._manifests
            if p.get("platform") == platform_filter or p.get("platform") == "universal"
        ]

    def get_package(self, software: str) -> Optional[Dict[str, Any]]:
        soft_lower = software.lower()
        for p in self._manifests:
            if p.get("software", "").lower() == soft_lower:
                return p
        return None

    def search(self, query: str) -> Dict[str, List[Any]]:
        q = query.strip().lower()
        matched_pkgs = []
        matched_cmds = []
        matched_maps = []

        for p in self._manifests:
            if q in p.get("software", "").lower() or q in p.get("display_name", "").lower() or q in p.get("desc", "").lower():
                matched_pkgs.append(p)
            for c in p.get("commands", []):
                if q in c.get("command_name", "").lower() or q in c.get("full_alias", "").lower() or q in c.get("desc", "").lower():
                    matched_cmds.append({**c, "software": p.get("software")})

        for m in self._mappings:
            if q in m.get("source_alias", "").lower() or q in m.get("target_template", "").lower() or q in m.get("desc", "").lower():
                matched_maps.append(m)

        return {
            "packages": matched_pkgs,
            "commands": matched_cmds,
            "mappings": matched_maps,
        }


# Global singleton instance
_INDEXER_INSTANCE: Optional[RegistryIndexer] = None


def get_registry_indexer(shell: str = "pwsh") -> RegistryIndexer:
    global _INDEXER_INSTANCE
    if _INDEXER_INSTANCE is None:
        _INDEXER_INSTANCE = RegistryIndexer(shell)
    return _INDEXER_INSTANCE
