"""
Kapsel Completion Subpackage.
Context-aware dynamic autocompletion powered by Carapace engine.
"""

from kapsel.completion.carapace_engine import CarapaceCandidate, CarapaceEngine, get_carapace_engine
from kapsel.completion.completer import DualStateCompleter

__all__ = [
    "DualStateCompleter",
    "CarapaceEngine",
    "get_carapace_engine",
    "CarapaceCandidate",
]
