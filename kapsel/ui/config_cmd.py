"""
Kapsel config command subsystem.
Handles 'config', 'config path', 'config edit', 'config get', 'config set', 'config reload'.
"""

import os
from pathlib import Path
import platform
import subprocess
import sys
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
    if console is None:
        console = Console(legacy_windows=False)

    config_path = get_config_path()
    cfg = load_config()

    if not args:
        # 'config' without arguments -> render dashboard
        render_config_dashboard(cfg, config_path, console)
        return 0

    sub = args[0].lower()

    if sub == "path":
        # 'config path' -> print absolute path
        print(str(config_path))
        return 0

    if sub == "edit":
        # 'config edit' -> open in default editor
        console.print(f"[dim]正在打开配置文件:[/] [bold #00f0ff]{config_path}[/]")
        try:
            if platform.system() == "Windows":
                # Try os.startfile first
                os.startfile(str(config_path))
            elif platform.system() == "Darwin":
                subprocess.run(["open", str(config_path)])
            else:
                subprocess.run(["xdg-open", str(config_path)])
            console.print("[bold #10b981]✔ 已在外部编辑器中打开[/]")
        except Exception as e:
            # Fallback to notepad on Windows
            if platform.system() == "Windows":
                subprocess.Popen(["notepad.exe", str(config_path)])
            else:
                console.print(f"[bold #f43f5e]打开失败: {e}[/]")
        return 0

    if sub == "reload":
        # 'config reload'
        cfg = load_config()
        console.print(f"[bold #10b981]✔ 配置已成功重新加载[/] [dim]({config_path})[/]")
        return 0

    if sub == "get":
        # 'config get <key>'
        if len(args) < 2:
            console.print("[bold #f59e0b]用法: config get <配置项名称>[/]")
            return 1
        key = args[1].lower()
        val = _lookup_config_key(cfg, key)
        if val is not None:
            console.print(f"[bold #00f0ff]{key}[/]: [bold #10b981]{val}[/]")
        else:
            console.print(f"[bold #f43f5e]未找到配置项:[/] {key}")
        return 0

    if sub == "set":
        # 'config set <key> <value>'
        if len(args) < 3:
            console.print("[bold #f59e0b]用法: config set <配置项名称> <值>[/]")
            console.print("[dim]示例: config set sensitivity 0.2[/]")
            console.print("[dim]      config set tap_mode full[/]")
            return 1
        raw_key = args[1]
        raw_val = " ".join(args[2:])

        # Type conversion
        val: Any = raw_val
        if raw_val.lower() in ("true", "yes", "on"):
            val = True
        elif raw_val.lower() in ("false", "no", "off"):
            val = False
        else:
            try:
                if "." in raw_val:
                    val = float(raw_val)
                else:
                    val = int(raw_val)
            except ValueError:
                val = raw_val

        # Aliases for convenience
        key_map = {
            "sensitivity": "autosuggest_sensitivity",
            "tap_mode": "autosuggest_tap_mode",
            "hold_action": "autosuggest_hold_action",
            "threshold": "consecutive_press_threshold",
            "banner": "enable_banner",
            "timing": "enable_timing",
            "autosuggest": "enable_autosuggest",
        }
        canonical_key = key_map.get(raw_key.lower(), raw_key)

        success = update_config_value(canonical_key, val)
        if success:
            console.print(f"[bold #10b981]✔ 配置已更新:[/] [bold #00f0ff]{canonical_key}[/] = [bold #a855f7]{val}[/]")
        else:
            console.print(f"[bold #f43f5e]✘ 更新配置失败，请检查文件权限[/]")
        return 0

    console.print(f"[bold #f43f5e]未知 config 子指令:[/] {sub}")
    console.print("[dim]支持的指令: config, config path, config edit, config get <key>, config set <key> <val>, config reload[/]")
    return 1


def render_config_dashboard(cfg: KapselConfig, path: Path, console: Console) -> None:
    """Renders visual overview of critical configuration settings."""
    grid = Table.grid(expand=True, padding=(0, 2))
    grid.add_column(style="bold #00f0ff", justify="right", width=22)
    grid.add_column(style="#e4e4e7")

    # Important settings
    inter = cfg.interaction
    tap_mode = inter.get("autosuggest_tap_mode", "word")
    sens = inter.get("autosuggest_sensitivity", 0.25)
    hold_act = inter.get("autosuggest_hold_action", "full")
    thresh = inter.get("consecutive_press_threshold", 2)

    grid.add_row("📁 配置文件路径:", f"[bold #38bdf8]{path}[/]")
    grid.add_row("🎯 右键单按 (Tap):", f"[bold #10b981]{tap_mode}[/] [dim](逐词采纳下一个参数)[/]" if tap_mode == "word" else f"[bold #10b981]{tap_mode}[/] [dim](一键采纳整行)[/]")
    grid.add_row("⚡ 右键连按 (Hold):", f"[bold #a855f7]{hold_act}[/] [dim](连续长按采纳整行)[/]")
    grid.add_row("⏱ 判定敏感度阈值:", f"[bold #f59e0b]{sens}s[/] [dim](按键间隔在此时间内判定为连按/长按)[/]")
    grid.add_row("🔢 连按判定击键数:", f"[bold #f59e0b]{thresh} 次[/]")
    grid.add_row("🎨 活跃主题风格:", f"[#00f0ff]{cfg.theme.get('name', 'cyber_dark')}[/]")
    grid.add_row("🖥️ 启动极简 Logo:", "[bold #10b981]开启[/]" if cfg.enable_banner else "[dim]关闭[/]")
    grid.add_row("⏱ 毫秒计时卡片:", "[bold #10b981]开启[/]" if cfg.enable_timing else "[dim]关闭[/]")
    grid.add_row("🔮 历史行内预测:", "[bold #10b981]开启[/]" if cfg.enable_autosuggest else "[dim]关闭[/]")

    tips = Text()
    tips.append("\n常用指令快捷操作:\n", style="bold #a855f7")
    tips.append("  config path              ", style="bold #00f0ff")
    tips.append("打印配置文件完整绝对路径\n", style="dim")
    tips.append("  config edit              ", style="bold #00f0ff")
    tips.append("使用外部编辑器直接打开 config.yaml 进行编辑\n", style="dim")
    tips.append("  config set sensitivity 0.2", style="bold #00f0ff")
    tips.append("修改长按判定敏感度 (秒)\n", style="dim")
    tips.append("  config set tap_mode full ", style="bold #00f0ff")
    tips.append("设置单次轻按直接采纳整行 (可选 word / full)\n", style="dim")
    tips.append("  config reload            ", style="bold #00f0ff")
    tips.append("重新加载最新配置\n", style="dim")

    content = Table.grid(expand=True, padding=(1, 0))
    content.add_column()

    header = Text()
    header.append("⚙️ KAPSEL 核心系统配置面板\n", style="bold #00f0ff")
    header.append("可直接修改 YAML 文件或使用 'config set' 指令调节灵敏度与功能开关\n", style="dim italic")

    content.add_row(header)
    content.add_row(grid)
    content.add_row(tips)

    panel = Panel(
        content,
        border_style="#0891b2",
        padding=(1, 2),
        expand=False,
    )
    console.print()
    console.print(panel)
    console.print()


def _lookup_config_key(cfg: KapselConfig, key: str) -> Any:
    key_map = {
        "sensitivity": "autosuggest_sensitivity",
        "tap_mode": "autosuggest_tap_mode",
        "hold_action": "autosuggest_hold_action",
        "threshold": "consecutive_press_threshold",
        "banner": "enable_banner",
        "timing": "enable_timing",
        "autosuggest": "enable_autosuggest",
    }
    canonical_key = key_map.get(key.lower(), key)

    # Check interaction
    if canonical_key in cfg.interaction:
        return cfg.interaction[canonical_key]
    # Check ui
    if canonical_key in cfg.ui:
        return cfg.ui[canonical_key]
    # Check theme
    if canonical_key in cfg.theme:
        return cfg.theme[canonical_key]
    # Check raw
    for sec, sub in cfg.raw.items():
        if isinstance(sub, dict) and canonical_key in sub:
            return sub[canonical_key]
        if sec == canonical_key:
            return sub
    return None
