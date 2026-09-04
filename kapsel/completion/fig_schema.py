"""
Fig.Spec declarative schema data models.
100% aligned with withfig/autocomplete (and Amazon Q Developer CLI) schema:
Spec -> Subcommands -> Options (Flags) -> Arguments
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union


@dataclass
class FigArg:
    name: str = ""
    description: str = ""
    is_optional: bool = False
    is_variadic: bool = False
    suggestions: List[str] = field(default_factory=list)


@dataclass
class FigOption:
    name: List[str] = field(default_factory=list)  # e.g. ["-m", "--message"]
    description: str = ""
    args: Optional[FigArg] = None
    is_persistent: bool = False

    @property
    def primary_name(self) -> str:
        return self.name[0] if self.name else ""

    @property
    def display_names(self) -> str:
        return ", ".join(self.name)


@dataclass
class FigSubcommand:
    name: List[str] = field(default_factory=list)  # e.g. ["commit"] or ["checkout", "co"]
    description: str = ""
    subcommands: List["FigSubcommand"] = field(default_factory=list)
    options: List[FigOption] = field(default_factory=list)
    args: Optional[List[FigArg]] = None

    @property
    def primary_name(self) -> str:
        return self.name[0] if self.name else ""


@dataclass
class FigSpec:
    name: str = ""
    description: str = ""
    subcommands: List[FigSubcommand] = field(default_factory=list)
    options: List[FigOption] = field(default_factory=list)
    args: Optional[List[FigArg]] = None


def parse_fig_arg(raw: Any) -> Optional[FigArg]:
    if not raw:
        return None
    if isinstance(raw, str):
        return FigArg(name=raw)
    if isinstance(raw, dict):
        return FigArg(
            name=raw.get("name", ""),
            description=raw.get("description", ""),
            is_optional=raw.get("isOptional", False),
            is_variadic=raw.get("isVariadic", False),
            suggestions=raw.get("suggestions", []),
        )
    return None


def parse_fig_option(raw: Dict[str, Any]) -> FigOption:
    raw_name = raw.get("name", [])
    if isinstance(raw_name, str):
        names = [raw_name]
    elif isinstance(raw_name, list):
        names = [str(n) for n in raw_name]
    else:
        names = []

    arg_data = raw.get("args")
    parsed_arg = parse_fig_arg(arg_data)

    return FigOption(
        name=names,
        description=raw.get("description", ""),
        args=parsed_arg,
        is_persistent=raw.get("isPersistent", False),
    )


def parse_fig_subcommand(raw: Dict[str, Any]) -> FigSubcommand:
    raw_name = raw.get("name", [])
    if isinstance(raw_name, str):
        names = [raw_name]
    elif isinstance(raw_name, list):
        names = [str(n) for n in raw_name]
    else:
        names = []

    subcmds = [parse_fig_subcommand(s) for s in raw.get("subcommands", []) if isinstance(s, dict)]
    opts = [parse_fig_option(o) for o in raw.get("options", []) if isinstance(o, dict)]

    raw_args = raw.get("args")
    parsed_args = None
    if isinstance(raw_args, list):
        parsed_args = [parse_fig_arg(a) for a in raw_args if a]
    elif isinstance(raw_args, (dict, str)):
        parsed_args = [parse_fig_arg(raw_args)]

    return FigSubcommand(
        name=names,
        description=raw.get("description", ""),
        subcommands=subcmds,
        options=opts,
        args=parsed_args,
    )


def parse_fig_spec(raw: Dict[str, Any]) -> FigSpec:
    name = raw.get("name", "")
    if isinstance(name, list):
        name = name[0] if name else ""

    subcmds = [parse_fig_subcommand(s) for s in raw.get("subcommands", []) if isinstance(s, dict)]
    opts = [parse_fig_option(o) for o in raw.get("options", []) if isinstance(o, dict)]

    return FigSpec(
        name=str(name),
        description=raw.get("description", ""),
        subcommands=subcmds,
        options=opts,
    )
