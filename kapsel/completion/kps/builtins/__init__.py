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
    from kapsel.completion.kps.builtins.language import handle_language_command
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
    from kapsel.core.plugin.catalog import load_plugin_catalog

    add_subcommands = load_plugin_catalog()
    add_subcommands["update"] = "Scan plugins and update completion dictionary"

    registry.register(
        name="add",
        handler=handle_add_command,
        help_text="Enable and register a plugin into Kapsel environment (e.g. kapsel add install)",
        subcommands=add_subcommands,
        usage="kapsel add <plugin_name> (or: kapsel add update)",
    )

    # 5b. setup-completion (maintenance and repair command)
    def _handle_setup_completion(args, console=None):
        from kapsel.completion.carapace_installer import install_carapace
        force = "--force" in args or "-f" in args
        success = install_carapace(console=console, force=force)
        return 0 if success else 1

    registry.register(
        name="setup-completion",
        handler=_handle_setup_completion,
        help_text="Download, setup, or repair Carapace 1,000+ commands autocompletion engine",
        usage="kapsel setup-completion [--force]",
    )

    # 6. toggle
    registry.register(
        name="toggle",
        handler=handle_toggle_command,
        help_text="Toggle Kapsel as default terminal mode (open on first call, close on second)",
        usage="kapsel toggle (or kps toggle)",
        )

    # 7. language
    registry.register(
        name="language",
        handler=handle_language_command,
        help_text="View and switch active UI language (en, zh_CN, ja, es, fr, de, ru)",
        usage="kapsel language [en|zh_CN|ja|es|fr|de|ru]",
    )

    # 8. completion
    from kapsel.completion.kps.builtins.completion import handle_completion
    registry.register(
        name="completion",
        handler=handle_completion,
        help_text="Manage, inspect, and synchronize declarative Carapace completion specifications",
        subcommands={
            "ls": "List active completion specifications and sources",
            "sync": "Force refresh and sync all specs to Carapace",
            "edit": "Open specification YAML in system editor",
            "new": "Scaffold a new user completion specification",
            "path": "Display active spec directories",
        },
        usage="kapsel completion [ls|sync|edit|new|path]",
    )

