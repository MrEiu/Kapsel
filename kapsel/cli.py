"""
Kapsel CLI entry point.
Provides both the interactive TUI capsule shell (`kapsel`) and one-shot translator tool (`kps`).
Includes 'kapsel toggle' to toggle Kapsel as the default terminal environment.
All comments and descriptions are in English.
"""

import os
import sys
from typing import List, Optional

from rich.console import Console
from rich.panel import Panel

from kapsel import __version__
from kapsel.completion.kps import dispatch_kps
from kapsel.core.engine import DualStateEngine
from kapsel.storage.logger import logger
from kapsel.ui.banner import ensure_utf8_io, render_banner
from kapsel.ui.card import render_execution_footer
from kapsel.ui.prompt import KapselPrompt


def main(args: Optional[List[str]] = None) -> int:
    """Main interactive capsule shell loop and command runner."""
    ensure_utf8_io()
    if args is None:
        args = sys.argv[1:]

    # Handle quick flags
    if args and args[0] in ("-v", "--version"):
        print(f"Kapsel v{__version__}")
        return 0

    no_banner = "--no-banner" in args
    clean_args = [a for a in args if a != "--no-banner"]

    # Handle -c / --command
    if clean_args and clean_args[0] in ("-c", "--command"):
        cmd_str = " ".join(clean_args[1:])
        engine = DualStateEngine()
        result = engine.dispatch(cmd_str)
        if engine.config.enable_card_border and not result.execution.is_builtin:
            render_execution_footer(
                summary=result.execution,
                translation=result.translated_cmd,
                config=engine.config,
            )
        return result.execution.exit_code

    is_toggle_start = False
    if clean_args and clean_args[0] == "toggle":
        is_toggle_start = True
        clean_args = clean_args[1:]

    # If other positional subcommands passed (e.g. kapsel status, kapsel help, kapsel add, kapsel config, kapsel datadir)
    if clean_args and not is_toggle_start:
        engine = DualStateEngine()
        full_cmd = "kapsel " + " ".join(clean_args)
        result = engine.dispatch(full_cmd)
        if engine.config.enable_card_border and not result.execution.is_builtin:
            render_execution_footer(
                summary=result.execution,
                translation=result.translated_cmd,
                config=engine.config,
            )
        return result.execution.exit_code

    # Launch interactive shell (Kapsel Default Mode)
    engine = DualStateEngine()
    console = Console(legacy_windows=False)

    # Auto-bootstrap Carapace autocompletion engine on first run (0ms on subsequent runs)
    from kapsel.completion.carapace_installer import ensure_carapace_installed
    ensure_carapace_installed(console=console)

    os.environ["KAPSEL_ACTIVE"] = "1"

    if is_toggle_start:
        console.print("[bold #10b981]✔ Kapsel active.[/] [dim]Type 'toggle' or 'exit' to quit.[/]\n")
    elif engine.config.enable_banner and not no_banner:
        render_banner()

    prompt_session = KapselPrompt(engine)

    # Interactive REPL loop
    while True:
        try:
            user_input = prompt_session.prompt()
        except KeyboardInterrupt:
            # Prevent empty line pollution
            continue
        except EOFError:
            # User pressed Ctrl+D, cleanly exit
            os.environ.pop("KAPSEL_ACTIVE", None)
            print("\nExiting Kapsel. Bye!")
            break

        stripped = user_input.strip()
        if not stripped:
            continue

        normalized = " ".join(stripped.lower().split())
        if normalized in ("exit", "quit", "toggle", "kapsel toggle", "kps toggle"):
            os.environ.pop("KAPSEL_ACTIVE", None)
            console.print("[dim]Exited Kapsel.[/]")
            break

        try:
            result = engine.dispatch(user_input)
            if engine.config.enable_card_border and not result.execution.is_builtin:
                render_execution_footer(
                    summary=result.execution,
                    translation=result.translated_cmd,
                    config=engine.config,
                )
        except Exception as e:
            logger.exception(f"Unexpected error executing '{user_input}': {e}")
            print(f"kapsel: unexpected error: {e}", file=sys.stderr)

    return 0


def kps_cli() -> int:
    """
    Direct CLI entry point for 'kps' command.
    Allows running single commands from external shells:
    e.g. `kps status` or `kps rm -rf node_modules`
    """
    ensure_utf8_io()
    argv = sys.argv[1:]
    if not argv:
        # If run as bare 'kps', launch the full interactive shell
        return main()

    if argv[0] in ("-v", "--version"):
        print(f"Kapsel v{__version__}")
        return 0

    if argv[0] == "toggle":
        return main(["toggle"])

    # 1. Fast dispatch to registered built-in or plugin kps commands
    cmd_line = " ".join(argv)
    builtin_exit = dispatch_kps(cmd_line)
    if builtin_exit is not None:
        return builtin_exit

    # 2. Otherwise dispatch through engine (executes plugin filters or reports error)
    full_line = "kps " + cmd_line
    engine = DualStateEngine()
    result = engine.dispatch(full_line)

    if engine.config.enable_card_border and not result.execution.is_builtin:
        render_execution_footer(
            summary=result.execution,
            translation=result.translated_cmd,
            config=engine.config,
        )

    return result.execution.exit_code


if __name__ == "__main__":
    sys.exit(main())
