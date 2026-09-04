"""
Kapsel Core Engine orchestrator.
Manages state transitions, plugin lifecycle, command dispatching, and execution history.
"""

from dataclasses import dataclass
from pathlib import Path
import time
from typing import Any, Optional, Tuple

from kapsel.completion.kps.dispatcher import dispatch_kps
from kapsel.completion.kps.registry import KpsCommandRegistry, get_kps_registry
from kapsel.core.detector import EnvironmentDetector, detector
from kapsel.core.executor import CommandExecutor, ExecutionSummary
from kapsel.core.plugin.hooks import HookType
from kapsel.core.plugin.manager import PluginManager
from kapsel.storage.config import KapselConfig, load_config
from kapsel.storage.history import HistoryManager
from kapsel.storage.logger import logger


@dataclass
class DispatchResult:
    mode: str  # "kps" or "native"
    raw_input: str
    translated_cmd: Optional[str]
    execution: ExecutionSummary


class DualStateEngine:
    """The central brain of Kapsel orchestrating dual-state execution, plugins, and state persistence."""

    def __init__(
        self,
        config: Optional[KapselConfig] = None,
        kps_registry: Optional[KpsCommandRegistry] = None,
        history_mgr: Optional[HistoryManager] = None,
        env_detector: Optional[EnvironmentDetector] = None,
    ):
        self.config = config or load_config()
        self.history_mgr = history_mgr or HistoryManager()
        self.detector = env_detector or detector
        self.kps_registry = kps_registry or get_kps_registry()

        # Detect host shell
        self.shell_name, self.shell_path = self.detector.detect_shell()
        self.is_elevated, self.elevated_label = self.detector.is_elevated()

        # Initialize executor
        self.executor = CommandExecutor(self.shell_name, self.shell_path)

        # Initialize Plugin Subsystem
        self.plugin_manager = PluginManager(
            config=self.config,
            kps_command_register_fn=self.kps_registry.register,
            env_detector=self.detector,
        )
        self.plugin_manager.load_all_plugins()
        self.plugin_manager.trigger_hook(HookType.ON_READY)

    def reload(self) -> None:
        """Reload configuration and refresh plugins."""
        self.config = load_config()
        self.plugin_manager.unload_all()
        self.plugin_manager.load_all_plugins()

    def is_kps_mode(self, text: str) -> bool:
        """Determines if the current text line represents Kapsel Mode."""
        stripped = text.strip()
        return stripped == "kps" or stripped.startswith("kps ")

    def dispatch(self, user_input: str) -> DispatchResult:
        """
        Dispatches input line either to Plugin Filter, Kapsel Builtin, or Native execution.
        Records execution duration, status, and history in SQLite history.db.
        """
        stripped = user_input.strip()
        cwd_str = str(Path.cwd())
        start_time = time.time()

        # 1. Plugin Pre-execution filter (e.g. mapping plugin intercepts and translates)
        is_filtered, transformed_cmd = self.plugin_manager.filter_command(user_input)

        if is_filtered:
            mode = "kps"
            cmd_to_run = transformed_cmd
            exec_summary = self.executor.execute(cmd_to_run)
            translated_cmd = cmd_to_run

        elif self.is_kps_mode(user_input):
            mode = "kps"
            translated_cmd = None

            # Try dispatching to core/plugin kps subcommands
            t0 = time.perf_counter()
            handled_code = dispatch_kps(user_input)
            t1 = time.perf_counter()
            duration_ms = int((t1 - t0) * 1000)

            if handled_code is not None:
                exec_summary = ExecutionSummary(
                    command=user_input,
                    exit_code=handled_code,
                    duration_ms=duration_ms,
                    duration_str=f"{duration_ms}ms",
                    success=(handled_code == 0),
                    is_builtin=True,
                )
            else:
                # Not a recognized builtin command
                print(f"kapsel: 未知指令 '{user_input}'。输入 'kps help' 查看可用指令。")
                exec_summary = ExecutionSummary(
                    command=user_input,
                    exit_code=1,
                    duration_ms=0,
                    duration_str="0ms",
                    success=False,
                    is_builtin=True,
                )

        else:
            mode = "native"
            translated_cmd = None
            exec_summary = self.executor.execute(user_input)

        # Record to history database
        self.history_mgr.add_record(
            command=user_input,
            translated_cmd=translated_cmd,
            mode=mode,
            cwd=cwd_str,
            shell=self.shell_name,
            timestamp=start_time,
            duration_ms=exec_summary.duration_ms,
            exit_code=exec_summary.exit_code,
        )

        # Trigger plugin post-execution hook
        self.plugin_manager.trigger_hook(
            HookType.ON_AFTER_EXECUTE,
            command=user_input,
            exit_code=exec_summary.exit_code,
            duration_ms=exec_summary.duration_ms,
        )

        return DispatchResult(
            mode=mode,
            raw_input=user_input,
            translated_cmd=translated_cmd,
            execution=exec_summary,
        )
