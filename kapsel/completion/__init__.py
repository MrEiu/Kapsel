"""
Kapsel Completion Subpackage.
Fuses Fig.Spec declarative hierarchy with Kapsel's core command subsystem and plugin hooks.
"""

from kapsel.completion.completer import DualStateCompleter
from kapsel.completion.fig_engine import FigCandidate, FigEngine, get_fig_engine
from kapsel.completion.fig_schema import FigArg, FigOption, FigSpec, FigSubcommand

__all__ = [
    "DualStateCompleter",
    "FigEngine",
    "get_fig_engine",
    "FigCandidate",
    "FigSpec",
    "FigSubcommand",
    "FigOption",
    "FigArg",
]
