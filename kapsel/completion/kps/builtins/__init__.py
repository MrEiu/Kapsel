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

    # 1. help (system manual)
    registry.register(
        name="help",
        handler=handle_help,
        help_text="Display Kapsel manual, interaction mechanisms, and command cheatsheet",
        usage="kapsel help",
        scope="system",
    )

    # 2. status (platform environment & sandbox看板)
    registry.register(
        name="status",
        handler=handle_status,
        help_text="Display OS environment, active shell, Git branch, and sandbox status",
        usage="kapsel status",
        scope="system",
    )

    # 3. config (core config.yaml)
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

    # 4. datadir (sandbox directory)
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
        scope="system",
    )

    # 5b. search (fuzzy search across Kapsel repository and catalog)
    from kapsel.completion.kps.builtins.search import handle_search

    registry.register(
        name="search",
        handler=handle_search,
        help_text="Fuzzy search across Kapsel plugins, tools, and ecosystem packages",
        usage="kapsel search [query] [-a | --all]",
        scope="system",
    )

    # 5c. setup-completion (maintenance and repair command, hidden from autocompletion)
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
        scope="system",
        hidden=True,
    )

    # 6. toggle
    registry.register(
        name="toggle",
        handler=handle_toggle_command,
        help_text="Toggle Kapsel as default terminal mode (open on first call, close on second)",
        usage="kapsel toggle",
        scope="system",
    )

    # 7. language
    registry.register(
        name="language",
        handler=handle_language_command,
        help_text="View and switch active UI language (en, zh_CN, ja, es, fr, de, ru)",
        usage="kapsel language [en|zh_CN|ja|es|fr|de|ru]",
        scope="system",
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
        scope="system",
    )

    # 9. upgrade & update (Kapsel Core & official plugins)
    from kapsel.completion.kps.builtins.upgrade import handle_upgrade

    plugin_subcommands = {k: v for k, v in add_subcommands.items() if k != "update"}

    registry.register(
        name="upgrade",
        handler=handle_upgrade,
        help_text="Check and upgrade Kapsel Core and official plugins with release notes",
        subcommands=plugin_subcommands,
        usage="kapsel upgrade [plugin_name] [--check]",
        scope="system",
    )
    registry.register(
        name="update",
        handler=handle_upgrade,
        help_text="Alias for 'kapsel upgrade'",
        subcommands=plugin_subcommands,
        usage="kapsel update [plugin_name] [--check]",
        scope="system",
        hidden=True,
    )

    # 10. enable & disable (Plugin switcher)
    from kapsel.completion.kps.builtins.plugin_switch import handle_enable_plugin, handle_disable_plugin
    registry.register(
        name="enable",
        handler=handle_enable_plugin,
        help_text="Enable an installed Kapsel plugin",
        subcommands=plugin_subcommands,
        usage="kapsel enable <plugin_name>",
        scope="system",
    )
    registry.register(
        name="disable",
        handler=handle_disable_plugin,
        help_text="Disable an active Kapsel plugin without removing its files",
        subcommands=plugin_subcommands,
        usage="kapsel disable <plugin_name>",
        scope="system",
    )


