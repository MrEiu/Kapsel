"""
Kapsel Config Command.
Handles 'config', 'config path', 'config edit', 'config get', 'config set', 'config reload'.
"""

import os
from pathlib import Path
import platform
import subprocess
from typing import Any, List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from kapsel.storage.config import (
    KapselConfig,
    get_config_path,
    load_config,
    update_config_value,
)
from kapsel.ui.banner import ensure_utf8_io


def handle_config_command(args: List[str], console: Optional[Console] = None) -> int:
    """Handles 'config [subcommand]' and renders rich output."""
    ensure_utf8_io()
    con = console or Console(legacy_windows=False)

    config_path = get_config_path()
    cfg = load_config()

    if not args:
        render_config_dashboard(cfg, config_path, con)
        return 0

    sub = args[0].lower()

    if sub == "path":
        print(str(config_path))
        return 0

    if sub == "edit":
        con.print(f"[dim]正在打开配置文件:[/] [bold #00f0ff]{config_path}[/]")
        try:
            if platform.system() == "Windows":
                os.startfile(str(config_path))
            elif platform.system() == "Darwin":
                subprocess.run(["open", str(config_path)])
            else:
                subprocess.run(["xdg-open", str(config_path)])
            con.print("[bold #10b981]✔ 已在外部编辑器中打开[/]")
        except Exception as e:
            con.print(f"[bold #f43f5e]无法打开编辑器: {e}[/]")
            con.print(f"[dim]您可以手动用记事本或 VSCode 编辑: {config_path}[/]")
        return 0

    if sub == "reload":
        new_cfg = load_config(force_reload=True)
        con.print(f"[bold #10b981]✔ 配置文件已成功重载生效！[/] (主题: {new_cfg.theme.get('name')}, Tap模式: {new_cfg.interaction.get('autosuggest_tap_mode')})")
        return 0

    if sub in ("datadir", "migrate"):
        from kapsel.commands.datadir import handle_datadir_command
        return handle_datadir_command(args[1:], con)

    if sub == "get":
        if len(args) < 2:
            con.print("[bold #f43f5e]错误: 请指定要查询的配置项路径 (例如: config get interaction.autosuggest_tap_mode)[/]")
            return 1
        key_path = args[1]
        val = get_nested_val(cfg.raw, key_path)
        if val is None:
            con.print(f"[dim]配置项 '{key_path}' 未设置或不存在 (当前使用默认值)[/]")
        else:
            con.print(f"[bold #00f0ff]{key_path}[/] = [bold #10b981]{val}[/]")
        return 0

    if sub == "set":
        if len(args) < 3:
            con.print("[bold #f43f5e]错误: 格式错误。用法: config set <key.path> <value>[/]")
            con.print("[dim]例如: config set interaction.autosuggest_tap_mode full[/]")
            con.print("[dim]例如: config set interaction.autosuggest_sensitivity 0.15[/]")
            return 1
        key_path = args[1]
        val_str = args[2]

        parsed_val: Any = val_str
        if val_str.lower() in ("true", "yes", "1", "on"):
            parsed_val = True
        elif val_str.lower() in ("false", "no", "0", "off"):
            parsed_val = False
        else:
            try:
                if "." in val_str:
                    parsed_val = float(val_str)
                else:
                    parsed_val = int(val_str)
            except ValueError:
                parsed_val = val_str

        success = update_config_value(key_path, parsed_val)
        if success:
            con.print(f"[bold #10b981]✔ 配置修改成功:[/] [bold #00f0ff]{key_path}[/] = [bold #10b981]{parsed_val}[/]")
            con.print("[dim]已自动持久化写入 ~/.kapsel/config.yaml 并即刻热重载生效。[/]")
            return 0
        else:
            con.print(f"[bold #f43f5e]✘ 配置更新失败，请检查键名: '{key_path}'[/]")
            return 1

    con.print(f"[bold #f43f5e]未知 config 子指令: '{sub}'[/]")
    con.print("[dim]可用指令: config, config path, config edit, config get <key>, config set <key> <val>, config reload[/]")
    return 1


def get_nested_val(data: dict, path: str) -> Any:
    keys = path.split(".")
    curr = data
    for k in keys:
        if isinstance(curr, dict) and k in curr:
            curr = curr[k]
        else:
            return None
    return curr


def render_config_dashboard(cfg: KapselConfig, config_path: Path, console: Console) -> None:
    inter = cfg.interaction
    ui_cfg = cfg.ui
    theme_cfg = cfg.theme
    cloud_cfg = cfg.raw.get("cloud", {})

    grid = Table.grid(expand=True, padding=(0, 2))
    grid.add_column(style="bold #00f0ff", justify="right", width=22)
    grid.add_column(style="#e4e4e7")
    grid.add_column(style="bold #a855f7", justify="right", width=22)
    grid.add_column(style="#e4e4e7")

    grid.add_row(
        "🎯 右箭头点按模式 (Tap):",
        f"[bold #10b981]{inter.get('autosuggest_tap_mode', 'word')}[/] [dim]('word':逐词 / 'full':整行)[/]",
        "🎨 UI 活跃配色主题:",
        f"[bold #00f0ff]{theme_cfg.get('name', 'cyber_dark')}[/]",
    )
    grid.add_row(
        "⚡ 连按/长按行为 (Hold):",
        f"[bold #10b981]{inter.get('autosuggest_hold_action', 'full')}[/] [dim](采纳整行)[/]",
        "⏱ 耗时与卡片封装:",
        f"[bold #10b981]{'开启' if ui_cfg.get('enable_card_border') else '关闭'}[/]",
    )
    grid.add_row(
        "⏲ 敏感度时间阈值:",
        f"[bold #10b981]{inter.get('autosuggest_sensitivity', 0.25)}s[/] [dim](阈值内判为长按)[/]",
        " Git 与 Shell 徽标:",
        f"[bold #10b981]{'开启' if ui_cfg.get('show_git_branch') else '关闭'}[/]",
    )
    grid.add_row(
        "🔢 连续按键判定次数:",
        f"[bold #10b981]{inter.get('consecutive_press_threshold', 2)}[/] [dim](达标后触发长按)[/]",
        "🌐 云端服务地址:",
        f"[dim]{cloud_cfg.get('server_endpoint', 'http://127.0.0.1:8000')}[/]",
    )

    content = Table.grid(expand=True, padding=(1, 0))
    content.add_column()

    header = Text()
    header.append("⚙️ KAPSEL 全局总核心配置面板\n", style="bold #00f0ff")
    header.append(f"配置文件路径: {config_path}\n", style="dim #6b7280")
    header.append("支持交互热重载 · 运行 'config edit' 在编辑器中打开 · 运行 'config set <key> <val>' 快速修改", style="italic #9ca3af")

    content.add_row(header)
    content.add_row(grid)

    panel = Panel(
        content,
        border_style="#0891b2",
        padding=(1, 2),
        expand=False,
    )

    console.print()
    console.print(panel)
    console.print()
