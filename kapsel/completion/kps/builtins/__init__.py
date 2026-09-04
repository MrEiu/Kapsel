"""
Kapsel Core Built-in Commands Registration.
Registers fundamental core commands: help, status, config, datadir, add, toggle.
These can be invoked interchangeably via 'kapsel <cmd>' or 'kps <cmd>'.
All comments and descriptions are in English.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from kapsel.completion.kps.registry import KpsCommandRegistry


def register_builtins(registry: "KpsCommandRegistry") -> None:
    """Registers core commands into the KpsCommandRegistry."""
    from kapsel.completion.kps.builtins.add import handle_add_command
    from kapsel.completion.kps.builtins.config import handle_config_command
    from kapsel.completion.kps.builtins.datadir import handle_datadir_command
    from kapsel.completion.kps.builtins.help import handle_help
    from kapsel.completion.kps.builtins.status import handle_status
    from kapsel.completion.kps.builtins.toggle import handle_toggle_command

    # 1. help
    registry.register(
        name="help",
        handler=handle_help,
        help_text="Display Kapsel manual, interaction mechanisms, and command cheatsheet",
        usage="kapsel help (or kps help)",
    )

    # 2. status
    registry.register(
        name="status",
        handler=handle_status,
        help_text="Display OS environment, active shell, Git branch, and sandbox status",
        usage="kapsel status (or kps status)",
    )

    # 3. config
    registry.register(
        name="config",
        handler=handle_config_command,
        help_text="View or modify core configuration in config.yaml",
        subcommands={
            "path": "Print physical configuration file path",
            "edit": "Open configuration in default external editor",
            "get": "Read configuration value for a key",
            "set": "Update configuration value for a key",
            "reload": "Hot-reload configuration from disk",
        },
        usage="kapsel config [path|edit|get|set|reload]",
    )

    # 4. datadir
    registry.register(
        name="datadir",
        handler=handle_datadir_command,
        help_text="Inspect or relocate data storage sandbox directory",
        subcommands={
            "status": "Show current data directory and stats",
            "path": "Print current data directory path",
        },
        usage="kapsel datadir [path]",
    )

    # 5. add <plugin_name>
    registry.register(
        name="add",
        handler=handle_add_command,
        help_text="Enable and register a plugin into Kapsel environment (e.g. kapsel add autopilot)",
        subcommands={
            "autopilot": "Enable background task queue and autonomous execution plugin (Pueue)",
            "install": "Enable unified cross-platform package manager plugin (mpm)",
            "rec": "Enable snippet recorder and interactive runner plugin (pet)",
            "alias": "Enable cross-platform Linux command alias mapper plugin",
            "profile": "Enable dotfiles and workspace sync roaming plugin (chezmoi)",
            "fuck": "Enable intelligent console command error correction plugin (thefuck)",
            "help": "Enable fast interactive command cheat sheets plugin (tealdeer)",
            "ai": "Enable terminal AI assistant and setup wizard plugin (aichat)",
        },
        usage="kapsel add <plugin_name>",
    )

    # 6. toggle
    registry.register(
        name="toggle",
        handler=handle_toggle_command,
        help_text="Toggle Kapsel as default terminal mode (open on first call, close on second)",
        usage="kapsel toggle (or kps toggle)",
    )
