"""
Carapace Dynamic Completion Engine for Kapsel.
Bridges 'carapace-bin' to provide context-aware, multi-shell autocompletion
for over 1,000+ commands (git, docker, kubectl, cargo, npm, etc.) with millisecond response.
All comments and descriptions are in English.
"""

from dataclasses import dataclass
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
from typing import Dict, List, Optional, Set, Tuple

from kapsel.completion.spec_manager import CarapaceSpecManager
from kapsel.storage.config import get_kapsel_dir
from kapsel.storage.logger import logger


@dataclass
class CarapaceCandidate:
    """Represents a single autocompletion candidate returned by Carapace."""
    value: str
    display: str
    description: str
    style: str = ""
    tag: str = ""


_ANSI_ESCAPE_RE = re.compile(r"(\x1b|\x9b|`e)\[[0-?]*[ -/]*[@-~]")


def _strip_ansi(text: str) -> str:
    """Removes ANSI color and style escape codes from text."""
    if not text:
        return ""
    return _ANSI_ESCAPE_RE.sub("", text).strip()


def resolve_carapace_executable() -> Optional[str]:
    """
    Finds the carapace-bin executable in standard locations:
    1. System PATH
    2. Scoop shims / apps directory
    3. Kapsel local bin directory (~/.kapsel/bin/carapace)
    4. Cargo bin directory (~/.cargo/bin)
    """
    # 1. Direct Scoop app binary (avoids shim process wrapper overhead on Windows)
    if sys.platform == "win32":
        user_profile = Path(os.environ.get("USERPROFILE", Path.home()))
        for candidate in [
            user_profile / "scoop/apps/carapace-bin/current/carapace.exe",
            user_profile / "scoop/shims/carapace.exe",
            user_profile / ".cargo/bin/carapace.exe",
            user_profile / "AppData/Local/Microsoft/WinGet/Links/carapace.exe",
        ]:
            if candidate.exists():
                return str(candidate)

    # 2. System PATH
    which_p = shutil.which("carapace")
    if which_p:
        return which_p

    # 3. Kapsel local bin
    is_win = sys.platform == "win32"
    local_bin = get_kapsel_dir() / "bin" / ("carapace.exe" if is_win else "carapace")
    if local_bin.exists():
        return str(local_bin)

    return None


class CarapaceEngine:
    """
    High-performance completion engine delegating to Carapace (carapace-bin).
    Caches the list of 1,000+ supported tools and invokes JSON export for dynamic context.
    """

    def __init__(self, executable: Optional[str] = None):
        self.executable: Optional[str] = executable or resolve_carapace_executable()
        self._supported_tools: Optional[Set[str]] = None
        self._completion_cache: Dict[Tuple[str, Tuple[str, ...], str], List[CarapaceCandidate]] = {}
        self.spec_manager = CarapaceSpecManager()

        # Light auto-sync of declarative specs on initialization
        try:
            self.spec_manager.sync_specs()
        except Exception as e:
            logger.debug(f"Carapace spec auto-sync on init skipped: {e}")

    def is_available(self) -> bool:
        """Returns True if carapace-bin is installed and executable."""
        return self.executable is not None and Path(self.executable).exists()

    def reload_tools(self) -> None:
        """Refreshes supported tools and re-syncs all specifications."""
        try:
            self.spec_manager.sync_specs()
        except Exception:
            pass
        self._supported_tools = None
        self.get_supported_tools()

    def get_supported_tools(self) -> Set[str]:
        """
        Returns the set of tool names supported by Carapace.
        Lazy-loads via 'carapace --list' and caches in memory.
        """
        if self._supported_tools is not None:
            return self._supported_tools

        if not self.is_available():
            self._supported_tools = set()
            return self._supported_tools

        try:
            res = subprocess.run(
                [self.executable, "--list"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=2.0,
            )
            if res.returncode == 0 and res.stdout.strip():
                data = json.loads(res.stdout)
                if isinstance(data, dict):
                    self._supported_tools = set(data.keys())
                    # Include active spec commands
                    try:
                        for s_cmd in self.spec_manager.discover_specs().keys():
                            self._supported_tools.add(s_cmd.lower())
                    except Exception:
                        pass
                    return self._supported_tools
        except Exception as e:
            logger.warning(f"Failed to load Carapace tools list: {e}")

        self._supported_tools = set()
        return self._supported_tools

    def has_completer_for(self, tool: str) -> bool:
        """Checks if Carapace has a completion specification for the given tool."""
        normalized = tool.lower()
        if normalized.endswith(".exe"):
            normalized = normalized[:-4]
        return normalized in self.get_supported_tools()

    def get_completions(self, text_line: str) -> Tuple[List[CarapaceCandidate], str]:
        """
        Retrieves completion candidates from Carapace for the given command line.
        Returns a tuple of (candidates, current_word_prefix).
        """
        if not self.is_available() or not text_line.strip():
            return [], ""

        stripped = text_line.lstrip()
        ends_with_space = text_line.endswith(" ")

        # Tokenize line respecting spaces
        try:
            # We use a custom parser or shlex to extract tokens
            words = shlex.split(stripped)
        except ValueError:
            # Unterminated quote, fall back to simple whitespace split
            words = stripped.split()

        if not words:
            return [], ""

        first_tool = words[0].lower()
        if first_tool.endswith(".exe"):
            first_tool = first_tool[:-4]

        if not self.has_completer_for(first_tool):
            return [], ""

        # Determine the current word prefix being completed
        if ends_with_space:
            prefix = ""
            args_for_carapace = words + [""]
        else:
            prefix = words[-1]
            args_for_carapace = words

        # Check in-memory cache
        cwd_str = str(Path.cwd())
        cache_key = (first_tool, tuple(args_for_carapace), cwd_str)
        if cache_key in self._completion_cache:
            return self._completion_cache[cache_key], prefix

        # Execute: carapace <tool> export <tool> <arg1> <arg2> ...
        cmd = [self.executable, first_tool, "export"] + args_for_carapace

        try:
            res = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=0.8,  # Robust timeout for process execution on Windows
                cwd=cwd_str,
            )
            if res.returncode != 0 or not res.stdout.strip():
                return [], prefix

            data = json.loads(res.stdout)
            values = data.get("values", [])
            candidates: List[CarapaceCandidate] = []

            for item in values:
                if not isinstance(item, dict):
                    continue
                val = item.get("value", "")
                disp = item.get("display", val)
                desc = _strip_ansi(item.get("description", ""))
                style = item.get("style", "")
                tag = item.get("tag", "")

                candidates.append(
                    CarapaceCandidate(
                        value=val,
                        display=disp,
                        description=desc,
                        style=style,
                        tag=tag,
                    )
                )

            # Limit cache size to 256 entries
            if len(self._completion_cache) > 256:
                self._completion_cache.clear()
            self._completion_cache[cache_key] = candidates

            return candidates, prefix

        except subprocess.TimeoutExpired:
            logger.debug(f"Carapace completion timed out for: {text_line}")
            return [], prefix
        except Exception as e:
            logger.debug(f"Error querying Carapace for '{text_line}': {e}")
            return [], prefix


_CARAPACE_ENGINE: Optional[CarapaceEngine] = None


def get_carapace_engine() -> CarapaceEngine:
    """Returns the singleton instance of CarapaceEngine."""
    global _CARAPACE_ENGINE
    if _CARAPACE_ENGINE is None:
        _CARAPACE_ENGINE = CarapaceEngine()
    return _CARAPACE_ENGINE
