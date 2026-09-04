"""
Kapsel Core Built-in Commands Registration.
Registers fundamental system management commands: help, status, config, datadir, add.
These are invoked via 'kapsel <cmd>'.
All comments and descriptions are in English.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from kapsel.completion.kps.registry import KpsCommandRegistry


def register_builtins(registry: "KpsCommandRegistry") -> None:
    """Registers core system commands into the KpsCommandRegistry."""
    from kapsel.completion.kps.builtins.add import handle_add_command
    from kapsel.completion.kps.builtins.config import handle_config_command
    from kapsel.completion.kps.builtins.datadir import handle_datadir_command
    from kapsel.completion.kps.builtins.help import handle_help
    from kapsel.completion.kps.builtins.status import handle_status

    # 1. kapsel help
    registry.register(
        name="help",
        handler=handle_help,
        help_text="Display Kapsel manual, interaction mechanisms, and command cheatsheet",
        usage="kapsel help",
        scope="system",
    )

    # 2. kapsel status
    registry.register(
        name="status",
        handler=handle_status,
        help_text="Display OS environment, active shell, Git branch, and sandbox status",
        usage="kapsel status",
        scope="system",
    )

    # 3. kapsel config
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
        scope="system",
    )

    # 4. kapsel datadir
    registry.register(
        name="datadir",
        handler=handle_datadir_command,
        help_text="Inspect or relocate data storage sandbox directory",
        subcommands={
            "status": "Show current data directory and stats",
            "path": "Print current data directory path",
        },
        usage="kapsel datadir [path]",
        scope="system",
    )

    # 5. kapsel add <plugin_name>
    registry.register(
        name="add",
        handler=handle_add_command,
        help_text="Enable and register a plugin into Kapsel environment (e.g. kapsel add install)",
        subcommands={
            "install": "Enable the official cross-platform package installer plugin",
        },
        usage="kapsel add <plugin_name>",
        scope="system",
    )
