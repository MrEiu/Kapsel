"""
Kapsel Completion Subpackage.
Fuses Fig.Spec declarative hierarchy with Kapsel's core Linux mapping engine.
"""

from kapsel.core.completion.completer import DualStateCompleter
from kapsel.core.completion.fig_engine import FigCandidate, FigEngine, get_fig_engine
from kapsel.core.completion.fig_schema import FigArg, FigOption, FigSpec, FigSubcommand

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
