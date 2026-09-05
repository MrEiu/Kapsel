"""
Carapace Specification Manager for Kapsel.
Implements the 'Physical Independence, Logical Unification' architecture for declarative autocompletions.

Features:
1. Dual Root Tree Aggregation: Automatically compiles all built-in commands and plugin specifications
   into unified 'kps.yaml' and 'kapsel.yaml' root completion trees in Carapace.
2. Collision Sentinel: Blocks any top-level spec that matches host shell built-ins/cmdlets
   (e.g. 'alias', 'help', 'install', 'history', 'dir') to prevent hijacking host shell commands.
3. Safe Standalone Specs: Only non-colliding tools with 'standalone: true' (e.g. 'portal', 'shore')
   or custom user tools are synced as standalone top-level specs.
4. Auto-Purge: Detects and removes any legacy conflicting specs from Carapace's specs directory.

All comments and descriptions are in English.
"""

from dataclasses import dataclass, field
import hashlib
import os
from pathlib import Path
import shutil
import sys
from typing import Any, Dict, List, Optional, Set, Tuple
import yaml

from kapsel.storage.config import get_kapsel_dir, load_config
from kapsel.storage.logger import logger


# Commands reserved by host shells (PowerShell, CMD, Bash, Zsh) that MUST NEVER
# be deployed as standalone top-level Carapace specs. They reside strictly under 'kps' / 'kapsel'.
RESERVED_COLLISION_COMMANDS: Set[str] = {
    # PowerShell built-ins & default aliases
    "alias", "help", "history", "dir", "ls", "cat", "rm", "kill",
    "ps", "start", "stop", "sleep", "echo", "diff", "gc", "sc",
    "select", "where", "sort", "tee", "type", "man", "mount", "profile",
    "clear", "cls", "copy", "cp", "move", "mv", "ren", "del", "erase",
    "rdir", "md", "mkdir", "popd", "pushd", "pwd", "cd", "chdir",
    "measure", "compare", "format", "group", "measure-object",
    # Unix / POSIX shell built-ins & core utilities
    "install", "test", "jobs", "fg", "bg", "export", "source",
    "set", "unset", "read", "exec", "eval", "trap", "hash",
    "builtin", "command", "declare", "typeset", "local", "ulimit",
    "umask", "unalias", "wait", "exit", "logout", "return",
}

# Standard Core System commands metadata for the 'kapsel' root completion tree
CORE_SYSTEM_COMMANDS: List[Dict[str, Any]] = [
    {
        "name": "help",
        "aliases": ["?"],
        "description": "Display Kapsel system manual, interaction mechanisms, and command cheatsheet",
    },
    {
        "name": "status",
        "aliases": ["info"],
        "description": "Display OS environment, active shell, Git branch, and sandbox status",
    },
    {
        "name": "config",
        "description": "View or modify core configuration in config.yaml",
        "commands": [
            {"name": "path", "description": "Print physical configuration file path"},
            {"name": "edit", "description": "Open configuration in default external editor"},
            {"name": "get", "description": "Read configuration value for a key"},
            {"name": "set", "description": "Update configuration value for a key"},
            {"name": "reload", "description": "Hot-reload configuration from disk"},
        ],
    },
    {
        "name": "datadir",
        "description": "Inspect or relocate data storage sandbox directory",
        "commands": [
            {"name": "status", "description": "Show current data directory and stats"},
            {"name": "path", "description": "Print current data directory path"},
        ],
    },
    {
        "name": "add",
        "description": "Enable and register a plugin into Kapsel environment",
        "commands": [
            {"name": "update", "description": "Scan plugins and update completion dictionary"},
        ],
    },
    {
        "name": "search",
        "aliases": ["find"],
        "description": "Fuzzy search across Kapsel repository plugins and metadata catalog",
        "flags": {
            "-a, --all": "Display all available plugins and tools without filtering",
        },
    },
    {
        "name": "toggle",
        "description": "Toggle Kapsel as default terminal mode",
    },
    {
        "name": "language",
        "description": "View and switch active UI language",
        "commands": [
            {"name": "en", "description": "English"},
            {"name": "zh_CN", "description": "Simplified Chinese (简体中文)"},
            {"name": "ja", "description": "Japanese (日本語)"},
            {"name": "es", "description": "Spanish (Español)"},
            {"name": "fr", "description": "French (Français)"},
            {"name": "de", "description": "German (Deutsch)"},
            {"name": "ru", "description": "Russian (Русский)"},
        ],
    },
    {
        "name": "completion",
        "description": "Manage, inspect, and synchronize declarative Carapace completion specifications",
        "commands": [
            {"name": "ls", "description": "List active completion specifications and sources"},
            {"name": "sync", "description": "Force refresh and sync all specs to Carapace"},
            {"name": "edit", "description": "Open specification YAML in system editor"},
            {"name": "new", "description": "Scaffold a new user completion specification"},
            {"name": "path", "description": "Display active spec directories"},
        ],
    },
    {
        "name": "upgrade",
        "aliases": ["update"],
        "description": "Check and upgrade Kapsel Core and official plugins with release notes",
        "flags": {
            "-c, --check": "Check for updates without downloading or installing",
        },
    },
    {
        "name": "enable",
        "description": "Enable an installed Kapsel plugin",
    },
    {
        "name": "disable",
        "description": "Disable an active Kapsel plugin without removing its files",
    },
]

# Backward compatibility alias
CORE_BUILTIN_COMMANDS = CORE_SYSTEM_COMMANDS

# Default feature commands for 'kps' root completion tree (tools and plugins)
DEFAULT_FEATURE_COMMANDS: List[Dict[str, Any]] = [
    {
        "name": "search",
        "description": "Search for packages across package managers (powered by mpm)",
    },
    {
        "name": "help",
        "description": "Fast command cheat sheets powered by tealdeer (tldr)",
        "flags": {
            "-u, --update": "Update local tldr cheat sheet cache",
            "-l, --list": "List all available command cheat sheets",
            "-p, --platform=": "Select target platform (linux, macos, windows, common)",
            "--raw": "Display raw markdown page without rendering",
            "--clear-cache": "Clear local cheat sheet cache",
        },
    },
    {
        "name": "install",
        "description": "Install package(s) across systems using meta-package-manager (mpm)",
        "flags": {
            "--order": "Show package manager priority order",
            "--detect": "Rescan system and update package manager priorities",
            "--config": "Show path to independent package manager configuration",
        },
    },
    {
        "name": "update",
        "description": "Update installed packages across package managers (mpm)",
    },
    {
        "name": "sync",
        "description": "Synchronize package configurations (mpm)",
        "flags": {
            "-mpm, --mpm": "Sync package manager configurations via mpm",
        },
    },
]



@dataclass
class SpecInfo:
    """Metadata describing a single command completion specification."""
    command: str
    description: str
    source_type: str  # 'user', 'plugin', or 'core'
    source_path: Path
    target_path: Path
    aliases: List[str] = field(default_factory=list)
    standalone: bool = False
    is_overridden: bool = False
    raw_data: Dict[str, Any] = field(default_factory=dict)


def get_carapace_specs_dir() -> Path:
    """
    Resolves Carapace's native specifications directory across platforms:
    - Windows: %APPDATA%/carapace/specs (or ~/AppData/Roaming/carapace/specs)
    - macOS / Linux: ~/.config/carapace/specs
    """
    if sys.platform == "win32":
        appdata = os.environ.get("APPDATA")
        if appdata:
            base = Path(appdata)
        else:
            base = Path.home() / "AppData" / "Roaming"
        specs_dir = base / "carapace" / "specs"
    else:
        xdg_config = os.environ.get("XDG_CONFIG_HOME")
        if xdg_config:
            base = Path(xdg_config)
        else:
            base = Path.home() / ".config"
        specs_dir = base / "carapace" / "specs"

    specs_dir.mkdir(parents=True, exist_ok=True)
    return specs_dir


def get_user_specs_dir() -> Path:
    """
    Resolves the user's custom specifications directory (~/.kapsel/specs or KPS-data/specs).
    """
    user_specs = get_kapsel_dir() / "specs"
    user_specs.mkdir(parents=True, exist_ok=True)
    return user_specs


def _compute_file_hash(path: Path) -> str:
    """Calculates SHA256 hash of a file for incremental sync comparison."""
    try:
        content = path.read_bytes()
        return hashlib.sha256(content).hexdigest()
    except Exception:
        return ""


def _parse_spec_file(path: Path) -> Tuple[str, str, List[str], bool, Dict[str, Any]]:
    """
    Extracts command name, description, aliases, standalone flag, and full raw dict from a spec YAML file.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if isinstance(data, dict):
            name = str(data.get("name", path.stem)).strip()
            desc = str(data.get("description", "")).strip()
            aliases = [str(a) for a in data.get("aliases", []) if isinstance(a, str)]
            standalone = bool(data.get("standalone", False))
            return name, desc, aliases, standalone, data
    except Exception as e:
        logger.debug(f"Failed to parse spec file {path}: {e}")

    return path.stem, "", [], False, {}


def _parse_spec_metadata(path: Path) -> Tuple[str, str, List[str]]:
    """Backward-compatible helper returning (name, description, aliases)."""
    name, desc, aliases, _, _ = _parse_spec_file(path)
    return name, desc, aliases


class CarapaceSpecManager:
    """
    Manages discovery, hierarchical precedence, incremental synchronization,
    dual root aggregation ('kps.yaml' and 'kapsel.yaml'), and collision prevention.
    """

    def __init__(self, kapsel_dir: Optional[Path] = None, carapace_dir: Optional[Path] = None):
        self.kapsel_dir = kapsel_dir or get_kapsel_dir()
        self.carapace_specs_dir = carapace_dir or get_carapace_specs_dir()
        self.user_specs_dir = self.kapsel_dir / "specs"
        self.user_specs_dir.mkdir(parents=True, exist_ok=True)

    def discover_specs(
        self,
        plugin_dirs: Optional[List[Path]] = None,
        enabled_plugins: Optional[List[str]] = None,
    ) -> Dict[str, SpecInfo]:
        """
        Discovers all available specification files applying precedence hierarchy:
        User Custom (~/.kapsel/specs/) > Enabled Plugins (plugins/*/spec.yaml)
        """
        specs: Dict[str, SpecInfo] = {}

        # 1. Resolve plugin directories to scan
        resolved_plugin_dirs: List[Path] = []
        if plugin_dirs is not None:
            resolved_plugin_dirs = list(plugin_dirs)
        else:
            cfg = load_config()
            data_plugins = self.kapsel_dir / "plugins"
            if data_plugins.is_dir():
                resolved_plugin_dirs.append(data_plugins)
            local_plugins = Path.cwd() / "plugins"
            if local_plugins.is_dir() and local_plugins not in resolved_plugin_dirs:
                resolved_plugin_dirs.append(local_plugins)

        if enabled_plugins is None:
            cfg = load_config()
            enabled_plugins = cfg.enabled_plugins

        # 2. Discover Plugin Layer Specs (Default standalone: False unless specified)
        for p_dir in resolved_plugin_dirs:
            if not p_dir.is_dir():
                continue
            for item in p_dir.iterdir():
                if not item.is_dir():
                    continue
                plugin_name = item.name
                if enabled_plugins and plugin_name not in enabled_plugins:
                    continue

                candidate_files = [
                    item / "spec.yaml",
                    item / f"{plugin_name}.yaml",
                    item / "completions.yaml",
                ]
                for c_file in candidate_files:
                    if c_file.is_file():
                        cmd_name, desc, aliases, standalone, raw_data = _parse_spec_file(c_file)
                        # Sentinel: Force standalone=False if command collides with host shell
                        if cmd_name.lower() in RESERVED_COLLISION_COMMANDS:
                            standalone = False

                        target_path = self.carapace_specs_dir / f"{cmd_name}.yaml"
                        specs[cmd_name] = SpecInfo(
                            command=cmd_name,
                            description=desc,
                            source_type="plugin",
                            source_path=c_file,
                            target_path=target_path,
                            aliases=aliases,
                            standalone=standalone,
                            is_overridden=False,
                            raw_data=raw_data,
                        )
                        break

        # 3. Discover User Custom Specs (Default standalone: True unless specified)
        if self.user_specs_dir.is_dir():
            for u_file in self.user_specs_dir.glob("*.yaml"):
                if u_file.is_file():
                    cmd_name, desc, aliases, standalone_field, raw_data = _parse_spec_file(u_file)
                    # User custom specs default to standalone=True unless user explicitly set False
                    standalone = raw_data.get("standalone", True) if "standalone" in raw_data else True
                    if cmd_name.lower() in RESERVED_COLLISION_COMMANDS:
                        standalone = False

                    target_path = self.carapace_specs_dir / f"{cmd_name}.yaml"
                    was_plugin = cmd_name in specs
                    specs[cmd_name] = SpecInfo(
                        command=cmd_name,
                        description=desc,
                        source_type="user",
                        source_path=u_file,
                        target_path=target_path,
                        aliases=aliases,
                        standalone=standalone,
                        is_overridden=was_plugin,
                        raw_data=raw_data,
                    )

        return specs

    def build_aggregated_root_specs(
        self,
        discovered_specs: Optional[Dict[str, SpecInfo]] = None,
        plugin_dirs: Optional[List[Path]] = None,
        enabled_plugins: Optional[List[str]] = None,
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Builds unified root completion trees for 'kps' and 'kapsel'.
        Aggregates Kapsel core built-ins and all enabled plugin specifications
        into structured command trees without polluting host shell command names.
        Returns a tuple of (kps_spec_dict, kapsel_spec_dict).
        """
        if discovered_specs is None:
            discovered_specs = self.discover_specs(
                plugin_dirs=plugin_dirs, enabled_plugins=enabled_plugins
            )

        # 1. Build System Command Tree for 'kapsel'
        kapsel_commands: List[Dict[str, Any]] = [dict(c) for c in CORE_SYSTEM_COMMANDS]

        # Dynamically populate 'add' subcommands under 'kapsel' with all catalog and discovered plugins
        try:
            from kapsel.core.plugin.catalog import load_plugin_catalog
            catalog = load_plugin_catalog()
            add_subcmds: List[Dict[str, Any]] = [
                {"name": "update", "description": "Scan plugins and update completion dictionary"}
            ]
            for p_name, p_desc in sorted(catalog.items()):
                if p_name != "update":
                    add_subcmds.append({"name": p_name, "description": p_desc})
            for d_name, d_info in sorted(discovered_specs.items()):
                if not any(c["name"] == d_name for c in add_subcmds):
                    add_subcmds.append({
                        "name": d_name,
                        "description": d_info.description or f"Kapsel {d_name} extension",
                    })
            plugin_subcmds = [c for c in add_subcmds if c["name"] != "update"]
            for cmd_entry in kapsel_commands:
                if cmd_entry["name"] == "add":
                    cmd_entry["commands"] = add_subcmds
                elif cmd_entry["name"] in ("upgrade", "enable", "disable"):
                    cmd_entry["commands"] = plugin_subcmds
        except Exception as e:
            logger.debug(f"Failed to populate dynamic add subcommands: {e}")

        kapsel_commands.sort(key=lambda c: c["name"])

        # 2. Build Feature/Tool Command Tree for 'kps'
        kps_commands: List[Dict[str, Any]] = [dict(c) for c in DEFAULT_FEATURE_COMMANDS]
        kps_names = {c["name"].lower() for c in kps_commands}
        system_command_names = {c["name"].lower() for c in CORE_SYSTEM_COMMANDS}

        # Add discovered plugin / user specs as subcommands under 'kps'
        for cmd_name, info in discovered_specs.items():
            clean_name = cmd_name.lower().strip()
            # Do not allow system commands to leak into kps
            if clean_name in system_command_names:
                continue

            raw = info.raw_data or {}
            subcmd_entry: Dict[str, Any] = {
                "name": clean_name,
                "description": info.description or f"Kapsel {clean_name} extension",
            }
            if info.aliases:
                subcmd_entry["aliases"] = info.aliases

            if "flags" in raw:
                subcmd_entry["flags"] = raw["flags"]

            if "commands" in raw and isinstance(raw["commands"], list):
                subcmd_entry["commands"] = raw["commands"]

            if "completion" in raw:
                subcmd_entry["completion"] = raw["completion"]

            if clean_name in kps_names:
                for idx, existing in enumerate(kps_commands):
                    if existing["name"].lower() == clean_name:
                        kps_commands[idx] = subcmd_entry
                        break
            else:
                kps_commands.append(subcmd_entry)
                kps_names.add(clean_name)

        kps_commands.sort(key=lambda c: c["name"])

        # 3. Assemble 'kps' root spec (Tools & Plugins execution)
        kps_spec = {
            "name": "kps",
            "description": "Kapsel Plugin Command Subsystem & High-Speed Tool Wrapper",
            "flags": {
                "-v, --version": "Show Kapsel version",
                "-h, --help": "Show help information",
            },
            "commands": kps_commands,
        }

        # 4. Assemble 'kapsel' root spec (System Platform & Shell Management)
        kapsel_spec = {
            "name": "kapsel",
            "description": "Kapsel Intelligent Capsule Shell & System Management",
            "flags": {
                "-v, --version": "Show Kapsel version",
                "-h, --help": "Show help information",
                "--no-banner": "Start interactive shell without header banner",
                "-c, --command=": "Execute single command inside Kapsel sandbox",
            },
            "commands": kapsel_commands,
        }

        return kps_spec, kapsel_spec

    def sync_specs(
        self,
        plugin_dirs: Optional[List[Path]] = None,
        enabled_plugins: Optional[List[str]] = None,
        force: bool = False,
    ) -> Tuple[int, int]:
        """
        Synchronizes declarative specifications to Carapace:
        1. Compiles and syncs dual root specs: 'kps.yaml' and 'kapsel.yaml'.
        2. Discovers safe standalone specs ('standalone: true' and not in RESERVED_COLLISION_COMMANDS).
        3. Cleans up any colliding or deprecated top-level specs in Carapace's specs directory.
        Returns a tuple of (synced_count, skipped_count).
        """
        discovered = self.discover_specs(plugin_dirs=plugin_dirs, enabled_plugins=enabled_plugins)
        self.carapace_specs_dir.mkdir(parents=True, exist_ok=True)

        synced_count = 0
        skipped_count = 0

        # Step 1: Compile and sync dual root specs: kps.yaml & kapsel.yaml
        kps_spec, kapsel_spec = self.build_aggregated_root_specs(
            discovered_specs=discovered,
            plugin_dirs=plugin_dirs,
            enabled_plugins=enabled_plugins,
        )

        for root_name, root_data in [("kps", kps_spec), ("kapsel", kapsel_spec)]:
            root_file = self.carapace_specs_dir / f"{root_name}.yaml"
            new_content = yaml.dump(root_data, sort_keys=False, allow_unicode=True)
            existing_content = ""
            if root_file.exists():
                try:
                    existing_content = root_file.read_text(encoding="utf-8")
                except Exception:
                    pass

            if force or existing_content != new_content:
                try:
                    root_file.write_text(new_content, encoding="utf-8")
                    synced_count += 1
                except Exception as e:
                    logger.error(f"Failed to write root spec {root_file}: {e}")
            else:
                skipped_count += 1

        # Step 2: Sync safe standalone specs
        for cmd_name, info in discovered.items():
            if not info.standalone:
                continue

            if cmd_name.lower() in RESERVED_COLLISION_COMMANDS:
                logger.warning(
                    f"Spec '{cmd_name}' requested standalone mode but collides with "
                    f"host shell reserved commands. Suppressing top-level spec."
                )
                continue

            target = info.target_path
            src = info.source_path

            needs_copy = force or not target.exists()
            if not needs_copy:
                src_hash = _compute_file_hash(src)
                target_hash = _compute_file_hash(target)
                if src_hash != target_hash:
                    needs_copy = True

            if needs_copy:
                try:
                    shutil.copy2(src, target)
                    synced_count += 1
                except Exception as e:
                    logger.error(f"Failed to sync spec {src} -> {target}: {e}")
            else:
                skipped_count += 1

        # Step 3: Purge any conflicting specs from Carapace specs dir
        for reserved_cmd in RESERVED_COLLISION_COMMANDS:
            bad_file = self.carapace_specs_dir / f"{reserved_cmd}.yaml"
            if bad_file.exists():
                try:
                    bad_file.unlink()
                    logger.info(f"Purged conflicting Carapace spec: {bad_file}")
                except Exception as e:
                    logger.warning(f"Failed to remove conflicting spec {bad_file}: {e}")

        return synced_count, skipped_count

    def create_template(self, command_name: str, description: str = "") -> Path:
        """
        Scaffolds a new standard Carapace spec template in user specs directory.
        """
        target = self.user_specs_dir / f"{command_name}.yaml"
        if target.exists():
            return target

        desc_str = description or f"Custom completion for {command_name}"
        content = f"""# yaml-language-server: $schema=https://carapace.sh/schemas/command.json
name: {command_name}
description: "{desc_str}"
standalone: true

flags:
  -h, --help: "Show help information"
  -v, --verbose: "Enable verbose output"
  -V, --version: "Show version"

commands:
  - name: run
    description: "Run {command_name} command"
    flags:
      -f, --force: "Force execution"
  - name: status
    description: "Inspect status"
"""
        target.write_text(content, encoding="utf-8")
        self.sync_specs()
        return target
