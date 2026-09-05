"""
Kapsel card-based visual block packaging.
Encloses command input and output in modern terminal block cards.
"""

from datetime import datetime
from pathlib import Path
from typing import Any, List, Optional, Tuple, Union

from prompt_toolkit.formatted_text import FormattedText
from rich.console import Console

from kapsel.core.detector import detector
from kapsel.core.executor import ExecutionSummary
from kapsel.storage.config import KapselConfig
from kapsel.ui.banner import ensure_utf8_io


def get_prompt_tokens(config: KapselConfig, shell_name: str) -> FormattedText:
    """
    Constructs the prompt_toolkit FormattedText tuple list for the 2-line block prompt:
    ╭─ kapsel  [pwsh]  ~/Desktop/Kapsel  (main)  21:50:30
    ╰─ ❯ 
    """
    symbols = config.symbols
    cwd_str = detector.format_cwd()
    branch = detector.get_git_branch() if config.ui.get("show_git_branch", True) else None
    time_str = datetime.now().strftime("%H:%M:%S") if config.ui.get("show_timestamp", True) else ""

    tokens: List[Tuple[str, str]] = []

    # Line 1: Header line
    top_sym = symbols.get("top", "╭─")
    tokens.append(("class:prompt.top", f"{top_sym} " if top_sym else ""))
    tokens.append(("class:prompt.capsule", "kapsel  "))

    try:
        from kapsel.storage.user import UserManager
        user = UserManager.get_current_user()
        if user:
            tokens.append(("class:prompt.branch", f"@{user.username}  "))
    except Exception:
        pass

    if config.ui.get("show_shell_badge", True):
        tokens.append(("class:prompt.shell", f"[{shell_name}]  "))

    tokens.append(("class:prompt.cwd", f"{cwd_str}  "))

    if branch:
        tokens.append(("class:prompt.branch", f"({branch})  "))

    if time_str:
        tokens.append(("class:prompt.time", f"{time_str}"))

    tokens.append(("", "\n"))

    # Line 2: Input line
    bottom_sym = symbols.get("bottom", "╰─")
    arrow_sym = symbols.get("arrow", "❯")
    tokens.append(("class:prompt.bottom", f"{bottom_sym} " if bottom_sym else ""))
    tokens.append(("class:prompt.arrow", f"{arrow_sym} " if arrow_sym else "> "))

    return FormattedText(tokens)


def render_execution_footer(
    summary: ExecutionSummary,
    translation: Optional[Any] = None,
    config: Optional[KapselConfig] = None,
    console: Optional[Console] = None,
) -> None:
    """
    Prints the bottom closing block card line with execution status badge and timing.
    Example:
    ╰─ ✔ [0]  ⏱ 42ms  ·  Remove-Item -Recurse -Force dist
    """
    ensure_utf8_io()
    if console is None:
        console = Console(legacy_windows=False)

    symbols = config.symbols if config else {
        "bottom": "╰─",
        "success": "✔",
        "failure": "✘",
        "clock": "⏱",
    }

    bottom_sym = symbols.get("bottom", "╰─")
    clock_sym = symbols.get("clock", "⏱")

    if summary.success:
        badge_sym = symbols.get("success", "✔")
        badge = f"[bold #10b981]{badge_sym} 0[/]"
    else:
        badge_sym = symbols.get("failure", "✘")
        badge = f"[bold #f43f5e]{badge_sym} exit {summary.exit_code}[/]"

    timing = f"[dim #6b7280]{clock_sym} {summary.duration_str}[/]"

    meta_parts = [f"[bold #0891b2]{bottom_sym}[/]", badge, timing]

    # If it was a Kapsel Mode translated command, display the real command that executed
    if translation:
        real_cmd = getattr(translation, "translated_cmd", str(translation))
        orig_cmd = getattr(translation, "original_input", "")
        if real_cmd and real_cmd != orig_cmd:
            meta_parts.append(f"[dim #4b5563]·[/] [italic #a855f7]{real_cmd}[/]")

    footer_line = "  ".join(meta_parts)
    console.print(footer_line)
    console.print()
