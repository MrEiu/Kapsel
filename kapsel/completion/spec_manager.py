"""
Carapace Specification Manager for Kapsel.
Implements the 'Physical Independence, Logical Unification' architecture for declarative autocompletions.
Discovers and synchronizes independent spec files from:
1. Plugin Package Layer (plugins/<name>/spec.yaml)
2. User Global Layer (~/.kapsel/specs/<cmd>.yaml)
Directly into Carapace's native specification directory for instant native completion.
All comments and descriptions are in English.
"""

from dataclasses import dataclass
import hashlib
import os
from pathlib import Path
import shutil
import sys
from typing import Dict, List, Optional, Tuple
import yaml

from kapsel.storage.config import get_kapsel_dir, load_config
from kapsel.storage.logger import logger


@dataclass
class SpecInfo:
    """Metadata describing a single command completion specification."""
    command: str
    description: str
    source_type: str  # 'user', 'plugin', or 'core'
    source_path: Path
    target_path: Path
    aliases: List[str]
    is_overridden: bool = False


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


def _parse_spec_metadata(path: Path) -> Tuple[str, str, List[str]]:
    """
    Extracts command name, description, and aliases from a spec YAML file.
    Falls back to file stem if 'name' is omitted.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if isinstance(data, dict):
            name = str(data.get("name", path.stem)).strip()
            desc = str(data.get("description", "")).strip()
            aliases = [str(a) for a in data.get("aliases", []) if isinstance(a, str)]
            return name, desc, aliases
    except Exception as e:
        logger.debug(f"Failed to parse spec metadata from {path}: {e}")

    return path.stem, "", []


class CarapaceSpecManager:
    """
    Manages discovery, hierarchical precedence, incremental synchronization,
    and inspection of declarative Carapace specifications.
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
            # Auto-resolve from config and data dir
            cfg = load_config()
            data_plugins = self.kapsel_dir / "plugins"
            if data_plugins.is_dir():
                resolved_plugin_dirs.append(data_plugins)
            # Check local repository plugins directory if in development workspace
            local_plugins = Path.cwd() / "plugins"
            if local_plugins.is_dir() and local_plugins not in resolved_plugin_dirs:
                resolved_plugin_dirs.append(local_plugins)

        if enabled_plugins is None:
            cfg = load_config()
            enabled_plugins = cfg.enabled_plugins

        # 2. Discover Plugin Layer Specs (Lower priority than user custom)
        for p_dir in resolved_plugin_dirs:
            if not p_dir.is_dir():
                continue
            for item in p_dir.iterdir():
                if not item.is_dir():
                    continue
                plugin_name = item.name
                if enabled_plugins and plugin_name not in enabled_plugins:
                    continue

                # Look for spec.yaml or <plugin_name>.yaml
                candidate_files = [
                    item / "spec.yaml",
                    item / f"{plugin_name}.yaml",
                    item / "completions.yaml",
                ]
                for c_file in candidate_files:
                    if c_file.is_file():
                        cmd_name, desc, aliases = _parse_spec_metadata(c_file)
                        target_path = self.carapace_specs_dir / f"{cmd_name}.yaml"
                        specs[cmd_name] = SpecInfo(
                            command=cmd_name,
                            description=desc,
                            source_type="plugin",
                            source_path=c_file,
                            target_path=target_path,
                            aliases=aliases,
                            is_overridden=False,
                        )
                        break

        # 3. Discover User Custom Specs (Highest priority: can override plugins)
        if self.user_specs_dir.is_dir():
            for u_file in self.user_specs_dir.glob("*.yaml"):
                if u_file.is_file():
                    cmd_name, desc, aliases = _parse_spec_metadata(u_file)
                    target_path = self.carapace_specs_dir / f"{cmd_name}.yaml"

                    was_plugin = cmd_name in specs
                    specs[cmd_name] = SpecInfo(
                        command=cmd_name,
                        description=desc,
                        source_type="user",
                        source_path=u_file,
                        target_path=target_path,
                        aliases=aliases,
                        is_overridden=was_plugin,
                    )

        return specs

    def sync_specs(
        self,
        plugin_dirs: Optional[List[Path]] = None,
        enabled_plugins: Optional[List[str]] = None,
        force: bool = False,
    ) -> Tuple[int, int]:
        """
        Incrementally mirrors active spec files into Carapace's specs directory.
        Returns a tuple of (synced_count, skipped_count).
        """
        discovered = self.discover_specs(plugin_dirs=plugin_dirs, enabled_plugins=enabled_plugins)
        self.carapace_specs_dir.mkdir(parents=True, exist_ok=True)

        synced_count = 0
        skipped_count = 0

        for cmd_name, info in discovered.items():
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
        # Trigger immediate sync
        self.sync_specs()
        return target
