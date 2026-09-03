"""
Kapsel Dual-State Engine orchestrator.
Manages state transitions between Native Mode and Kapsel Mode, dispatching commands to router and executor.
"""

from dataclasses import dataclass
from pathlib import Path
import time
from typing import Optional, Tuple

from kapsel.core.detector import EnvironmentDetector, detector
from kapsel.core.executor import CommandExecutor, ExecutionSummary
from kapsel.core.router import CommandRouter, TranslationResult
from kapsel.storage.commands import CommandRegistry, load_commands
from kapsel.storage.config import KapselConfig, load_config
from kapsel.storage.history import HistoryManager
from kapsel.storage.logger import logger


@dataclass
class DispatchResult:
    mode: str  # "kps" or "native"
    raw_input: str
    translated: Optional[TranslationResult]
    execution: ExecutionSummary


class DualStateEngine:
    """The central brain of Kapsel orchestrating dual-state execution, routing, and state persistence."""

    def __init__(
        self,
        config: Optional[KapselConfig] = None,
        registry: Optional[CommandRegistry] = None,
        history_mgr: Optional[HistoryManager] = None,
        env_detector: Optional[EnvironmentDetector] = None,
    ):
        self.config = config or load_config()
        self.registry = registry or load_commands()
        self.history_mgr = history_mgr or HistoryManager()
        self.detector = env_detector or detector

        # Detect host shell
        self.shell_name, self.shell_path = self.detector.detect_shell()
        self.is_elevated, self.elevated_label = self.detector.is_elevated()

        # Initialize subsystems
        self.router = CommandRouter(self.registry, self.shell_name)
        self.executor = CommandExecutor(self.shell_name, self.shell_path)

    def reload(self) -> None:
        """Reload configuration and command mappings."""
        self.config = load_config()
        self.registry = load_commands()
        self.router.registry = self.registry

    def is_kps_mode(self, text: str) -> bool:
        """Determines if the current text line represents Kapsel Mode."""
        stripped = text.strip()
        return stripped == "kps" or stripped.startswith("kps ")

    def dispatch(self, user_input: str) -> DispatchResult:
        """
        Dispatches input line either to Kapsel translation or Native execution.
        Records execution duration, status, and frequency in history.db.
        """
        stripped = user_input.strip()
        cwd_str = str(Path.cwd())
        start_time = time.time()

        if self.is_kps_mode(user_input):
            mode = "kps"
            trans = self.router.translate(user_input)
            cmd_to_run = trans.translated_cmd if trans else user_input

            # Learn / increment weight for the alias
            if trans and trans.alias:
                self.history_mgr.increment_weight(trans.alias)

            exec_summary = self.executor.execute(cmd_to_run)

            # Persist to history database
            self.history_mgr.add_record(
                command=user_input,
                translated_cmd=cmd_to_run,
                mode="kps",
                cwd=cwd_str,
                shell=self.shell_name,
                timestamp=start_time,
                duration_ms=exec_summary.duration_ms,
                exit_code=exec_summary.exit_code,
            )

            return DispatchResult(
                mode=mode,
                raw_input=user_input,
                translated=trans,
                execution=exec_summary,
            )

        else:
            mode = "native"
            exec_summary = self.executor.execute(user_input)

            self.history_mgr.add_record(
                command=user_input,
                translated_cmd=user_input,
                mode="native",
                cwd=cwd_str,
                shell=self.shell_name,
                timestamp=start_time,
                duration_ms=exec_summary.duration_ms,
                exit_code=exec_summary.exit_code,
            )

            return DispatchResult(
                mode=mode,
                raw_input=user_input,
                translated=None,
                execution=exec_summary,
            )
