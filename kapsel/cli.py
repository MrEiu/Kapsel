"""
Kapsel CLI entry point.
Provides both the interactive TUI capsule shell (`kapsel`) and one-shot translator tool (`kps`).
"""

import argparse
import sys
from typing import List, Optional

from kapsel import __version__
from kapsel.completion.kps import dispatch_kps
from kapsel.core.engine import DualStateEngine
from kapsel.storage.logger import logger
from kapsel.ui.banner import ensure_utf8_io, render_banner
from kapsel.ui.card import render_execution_footer
from kapsel.ui.prompt import KapselPrompt


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="kapsel",
        description="💊 Kapsel：跨平台自适应智能终端胶囊 (Cross-platform adaptive smart terminal capsule)",
    )
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"Kapsel v{__version__}",
    )
    parser.add_argument(
        "--no-banner",
        action="store_true",
        help="禁用启动欢迎面板",
    )
    parser.add_argument(
        "-c", "--command",
        type=str,
        help="直接执行单条指令并退出",
    )
    return parser.parse_args(args)


def main(args: Optional[List[str]] = None) -> int:
    """Main interactive capsule shell loop."""
    ensure_utf8_io()
    parsed = parse_args(args)

    engine = DualStateEngine()

    # One-shot command execution via -c
    if parsed.command:
        result = engine.dispatch(parsed.command)
        if engine.config.enable_card_border and not result.execution.is_builtin:
            render_execution_footer(
                summary=result.execution,
                translation=result.translated_cmd,
                config=engine.config,
            )
        return result.execution.exit_code

    # Render startup banner if enabled
    if engine.config.enable_banner and not parsed.no_banner:
        render_banner()

    prompt_session = KapselPrompt(engine)

    # Interactive REPL loop
    while True:
        try:
            user_input = prompt_session.prompt()
        except KeyboardInterrupt:
            # User pressed Ctrl+C, reset prompt without exiting
            print()
            continue
        except EOFError:
            # User pressed Ctrl+D, cleanly exit
            print("\nExiting Kapsel. Bye! 💊")
            break

        stripped = user_input.strip()
        if not stripped:
            continue

        if stripped.lower() in ("exit", "quit"):
            print("Exiting Kapsel. Bye! 💊")
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
