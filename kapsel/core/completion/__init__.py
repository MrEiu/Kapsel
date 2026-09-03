"""
Kapsel Completion Subpackage.
"""

from kapsel.core.completion.completer import DualStateCompleter
from kapsel.core.completion.dynamic_subcmds import get_subcommands_for_tool

__all__ = ["DualStateCompleter", "get_subcommands_for_tool"]
