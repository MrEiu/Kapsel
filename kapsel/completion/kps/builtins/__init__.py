"""
Kapsel Core Built-in Commands Registration.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from kapsel.completion.kps.registry import KpsCommandRegistry


def register_builtins(registry: "KpsCommandRegistry") -> None:
    """Registers core built-in commands into the KpsCommandRegistry."""
    from kapsel.completion.kps.builtins.config import handle_config_command
    from kapsel.completion.kps.builtins.datadir import handle_datadir_command
    from kapsel.completion.kps.builtins.help import handle_help
    from kapsel.completion.kps.builtins.status import handle_status

    registry.register(
        name="help",
        handler=handle_help,
        help_text="查阅 Kapsel 终端胶囊使用手册与双态体系",
        usage="kps help",
    )

    registry.register(
        name="status",
        handler=handle_status,
        help_text="查看操作系统环境、宿主 Shell 与沙箱配置",
        usage="kps status",
    )

    registry.register(
        name="config",
        handler=handle_config_command,
        help_text="查看或交互式修改全局配置 config.yaml",
        subcommands={
            "path": "输出配置文件物理路径",
            "edit": "在外部编辑器中打开配置文件",
            "get": "读取指定键的配置值",
            "set": "设置指定键的配置值",
            "reload": "热重载全局配置",
        },
        usage="kps config [path|edit|get|set|reload]",
    )

    registry.register(
        name="datadir",
        handler=handle_datadir_command,
        help_text="查看或自定义迁移数据存储目录 (自动搬迁旧数据)",
        subcommands={
            "status": "查看当前数据目录与统计信息",
            "path": "输出当前数据目录路径",
        },
        usage="kps datadir [path]",
    )
