"""
Fig Completion Engine.
AST context walker and token stream parser for Fig.Spec definitions.
Supports deep multi-level subcommands (e.g. 'docker compose up'),
flags/options (-f, --flag), and descriptions.
"""

import json
from pathlib import Path
import shlex
from typing import Any, Dict, List, Optional, Tuple, Union

from kapsel.core.completion.fig_schema import (
    FigOption,
    FigSpec,
    FigSubcommand,
    parse_fig_spec,
)
from kapsel.storage.logger import get_kapsel_dir, logger

BUILTIN_SPECS_DIR = Path(__file__).parent / "specs"


def get_user_specs_dir() -> Path:
    d = get_kapsel_dir() / "registry" / "specs"
    d.mkdir(parents=True, exist_ok=True)
    return d


class FigCandidate:
    def __init__(self, insert_text: str, display_text: str, description: str, kind: str = "subcommand"):
        self.insert_text = insert_text
        self.display_text = display_text
        self.description = description
        self.kind = kind  # "subcommand" | "option" | "arg"

    def __repr__(self):
        return f"<FigCandidate {self.insert_text} ({self.kind}): {self.description}>"


class FigEngine:
    """
    Main Fig-compatible completion engine.
    Pre-indexes all available Fig.Spec JSON definitions and evaluates
    current command line token streams with sub-millisecond response.
    """

    def __init__(self):
        self._specs: Dict[str, FigSpec] = {}
        self.reload_specs()

    def reload_specs(self) -> None:
        """Loads all builtin and user-defined Fig.Spec JSON files."""
        specs = {}

        # 1. Built-in specs
        if BUILTIN_SPECS_DIR.exists():
            for f in BUILTIN_SPECS_DIR.glob("*.json"):
                try:
                    with open(f, "r", encoding="utf-8") as fp:
                        data = json.load(fp)
                        spec = parse_fig_spec(data)
                        specs[spec.name.lower()] = spec
                except Exception as e:
                    logger.error(f"Failed to parse builtin Fig spec {f}: {e}")

        # 2. User/Community custom specs in ~/.kapsel/registry/specs/
        user_dir = get_user_specs_dir()
        for f in user_dir.glob("*.json"):
            try:
                with open(f, "r", encoding="utf-8") as fp:
                    data = json.load(fp)
                    spec = parse_fig_spec(data)
                    specs[spec.name.lower()] = spec
            except Exception as e:
                logger.error(f"Failed to parse user Fig spec {f}: {e}")

        self._specs = specs

    def has_spec_for_tool(self, tool: str) -> bool:
        return tool.lower() in self._specs

    def list_known_tools(self) -> List[str]:
        return sorted(self._specs.keys())

    def get_spec(self, tool: str) -> Optional[FigSpec]:
        return self._specs.get(tool.lower())

    def tokenize_line(self, line: str) -> Tuple[List[str], str]:
        """
        Tokenizes command line before cursor.
        Returns (completed_tokens, current_partial_token).
        e.g. "git commit -m" -> (["git", "commit"], "-m")
        e.g. "git commit "   -> (["git", "commit"], "")
        """
        if not line:
            return [], ""

        ends_with_space = line.endswith(" ")

        # Use split preserving empty trailing if space
        raw_tokens = line.split()
        if ends_with_space:
            return raw_tokens, ""
        else:
            if not raw_tokens:
                return [], ""
            return raw_tokens[:-1], raw_tokens[-1]

    def get_completions(self, line_before_cursor: str) -> List[FigCandidate]:
        """
        Core evaluation algorithm:
        Walks the Fig.Spec AST based on input tokens and returns context-relevant candidates.
        """
        completed, partial = self.tokenize_line(line_before_cursor)

        if not completed and not partial:
            return []

        # If user is at the very first token (the root CLI command, e.g. "gi" -> "git")
        if not completed:
            results = []
            prefix = partial.lower()
            for tool_name, spec in self._specs.items():
                if tool_name.startswith(prefix):
                    results.append(
                        FigCandidate(
                            insert_text=tool_name,
                            display_text=tool_name,
                            description=spec.description,
                            kind="subcommand",
                        )
                    )
            return results

        root_cmd = completed[0].lower()
        spec = self.get_spec(root_cmd)
        if not spec:
            return []

        # AST Context Traversal
        current_subcommands = spec.subcommands
        available_options: List[FigOption] = list(spec.options)

        # Tokens after the root command
        sub_tokens = completed[1:]

        for tok in sub_tokens:
            tok_lower = tok.lower()

            # Check if this token matches a subcommand
            matched_sub: Optional[FigSubcommand] = None
            for sc in current_subcommands:
                if tok_lower in [n.lower() for n in sc.name]:
                    matched_sub = sc
                    break

            if matched_sub:
                # Descend down AST
                current_subcommands = matched_sub.subcommands
                # Add options from this subcommand
                available_options.extend(matched_sub.options)
            else:
                # Token was an option or argument, skip descending subcommands
                pass

        candidates: List[FigCandidate] = []
        prefix = partial.lower()
        seen_insert_texts = set()

        # 1. If user is not specifically typing a flag ('-'), show Subcommands FIRST
        if not partial.startswith("-"):
            for sc in current_subcommands:
                primary = sc.primary_name
                if primary.lower().startswith(prefix) and primary not in seen_insert_texts:
                    seen_insert_texts.add(primary)
                    candidates.append(
                        FigCandidate(
                            insert_text=primary,
                            display_text=primary,
                            description=sc.description,
                            kind="subcommand",
                        )
                    )

        # 2. Evaluate Options (Flags)
        # If user typed '-', show only options matching the flag prefix
        # If user didn't type '-', show options below subcommands if prefix is empty
        if partial.startswith("-") or partial == "":
            for opt in available_options:
                matched_names = [n for n in opt.name if n.lower().startswith(prefix)]
                for opt_name in matched_names:
                    if opt_name not in seen_insert_texts:
                        seen_insert_texts.add(opt_name)
                        candidates.append(
                            FigCandidate(
                                insert_text=opt_name,
                                display_text=opt.display_names,
                                description=opt.description,
                                kind="option",
                            )
                        )

        return candidates


# Singleton engine instance
_FIG_ENGINE: Optional[FigEngine] = None


def get_fig_engine() -> FigEngine:
    global _FIG_ENGINE
    if _FIG_ENGINE is None:
        _FIG_ENGINE = FigEngine()
    return _FIG_ENGINE
