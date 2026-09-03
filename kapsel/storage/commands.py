"""
Kapsel commands manager.
Manages Linux-First command mappings in ~/.kapsel/commands.yaml.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml

from kapsel.storage.logger import get_kapsel_dir, logger

def get_hub_default_commands() -> List[Dict[str, Any]]:
    """
    Dynamically loads default command mappings from the local Hub SQLite database.
    Adheres strictly to the architectural manifesto in DEVELOPMENT.md:
    Zero hardcoding in code; data is stored in the Hub repository,
    synced to local SQLite, and loaded cleanly.
    """
    try:
        from kapsel.hub.db import HubRepository
        repo = HubRepository()
        maps = repo.list_mappings("pwsh")
        if maps:
            entries = []
            for m in maps:
                entries.append({
                    "alias": m["source_alias"],
                    "desc": m["desc"],
                    "mapping": {
                        "pwsh": m["target_template"],
                        "powershell": m["target_template"],
                        "unix": f"{m['source_alias']} {{{{args}}}}",
                    },
                })
            return entries
    except Exception as e:
        logger.debug(f"Could not load mappings from Hub: {e}")

    # Minimal emergency fallback only if SQLite DB is missing
    return [
        {
            "alias": "rm -rf",
            "desc": "递归强制删除目录或文件",
            "mapping": {"pwsh": "Remove-Item -Recurse -Force {{args}}", "unix": "rm -rf {{args}}"},
        },
        {
            "alias": "ls -la",
            "desc": "详细列出所有文件",
            "mapping": {"pwsh": "Get-ChildItem -Force {{args}}", "unix": "ls -la {{args}}"},
        },
        {
            "alias": "clear",
            "desc": "清除当前终端屏幕",
            "mapping": {"pwsh": "Clear-Host", "unix": "clear"},
        },
    ]


@dataclass
class CommandEntry:
    alias: str
    desc: str
    mapping: Dict[str, str]

    def get_template_for_shell(self, shell: str) -> Optional[str]:
        """
        Lookup template with multi-tier fallback:
        1. Exact shell match ('pwsh', 'powershell', 'cmd', 'zsh', 'bash', 'fish')
        2. PowerShell fallback (pwsh -> powershell, powershell -> pwsh)
        3. OS-level fallback ('windows' / 'unix')
        4. Global fallback to unix mapping or first available
        """
        # Exact shell
        if shell in self.mapping:
            return self.mapping[shell]

        # pwsh / powershell alias
        if shell == "pwsh" and "powershell" in self.mapping:
            return self.mapping["powershell"]
        if shell == "powershell" and "pwsh" in self.mapping:
            return self.mapping["pwsh"]

        # Family fallback
        if shell in ("cmd", "powershell", "pwsh"):
            if "windows" in self.mapping:
                return self.mapping["windows"]
        else:
            if "unix" in self.mapping:
                return self.mapping["unix"]

        # Final fallback
        return self.mapping.get("unix") or next(iter(self.mapping.values()), None)


class CommandRegistry:
    def __init__(self, commands: Optional[List[CommandEntry]] = None):
        self.commands: List[CommandEntry] = commands or []
        self._alias_map: Dict[str, CommandEntry] = {c.alias: c for c in self.commands}

    def get(self, alias: str) -> Optional[CommandEntry]:
        return self._alias_map.get(alias)

    def find_best_match(self, input_text: str) -> Optional[tuple[CommandEntry, str]]:
        """
        Matches the longest matching alias from input_text.
        e.g., 'rm -rf node_modules' -> (CommandEntry('rm -rf'), 'node_modules')
        Returns (entry, remainder_args) or None.
        """
        cleaned = input_text.strip()
        # Sort aliases by descending length so "rm -rf" matches before "rm"
        sorted_entries = sorted(self.commands, key=lambda e: len(e.alias), reverse=True)
        for entry in sorted_entries:
            if cleaned == entry.alias:
                return entry, ""
            if cleaned.startswith(entry.alias + " "):
                args = cleaned[len(entry.alias) + 1:].strip()
                return entry, args
        return None

    def list_all(self) -> List[CommandEntry]:
        return self.commands


def get_commands_path() -> Path:
    return get_kapsel_dir() / "commands.yaml"


def load_commands() -> CommandRegistry:
    """Load commands.yaml or initialize with default commands from the local Hub SQLite database."""
    path = get_commands_path()
    if not path.exists():
        save_default_commands(path)
        entries = [CommandEntry(**item) for item in get_hub_default_commands()]
        return CommandRegistry(entries)

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        raw_list = data.get("commands", [])
        entries = []
        for item in raw_list:
            if isinstance(item, dict) and "alias" in item and "desc" in item and "mapping" in item:
                entries.append(CommandEntry(
                    alias=item["alias"],
                    desc=item["desc"],
                    mapping=item["mapping"],
                ))
        if not entries:
            entries = [CommandEntry(**item) for item in get_hub_default_commands()]
        return CommandRegistry(entries)
    except Exception as e:
        logger.error(f"Error loading commands from {path}: {e}")
        entries = [CommandEntry(**item) for item in get_hub_default_commands()]
        return CommandRegistry(entries)


def save_default_commands(path: Path) -> None:
    try:
        defaults = get_hub_default_commands()
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump({"commands": defaults}, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        logger.info(f"Initialized default commands at {path} from Hub repository")
    except Exception as e:
        logger.error(f"Failed to write default commands: {e}")
