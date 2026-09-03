"""
Kapsel dynamic environment welcome banner.
Renders high-aesthetic Rich panel on startup.
"""

from pathlib import Path
import platform
import sys
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from kapsel.core.detector import detector
from kapsel.storage.commands import CommandRegistry
from kapsel.storage.logger import get_kapsel_dir


def ensure_utf8_io() -> None:
    """Ensure standard input and output streams use utf-8 encoding."""
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def render_banner(
    console: Optional[Console] = None,
    registry: Optional[CommandRegistry] = None,
) -> None:
    """Renders the modern startup card banner in the terminal."""
    ensure_utf8_io()
    if console is None:
        console = Console(legacy_windows=False)

    shell_name, shell_path = detector.detect_shell()
    is_elevated, elevated_label = detector.is_elevated()
    cmd_count = len(registry.commands) if registry else 35
    sandbox_dir = get_kapsel_dir()

    # Pretty platform string
    os_name = platform.system()
    os_release = platform.release()
    arch = platform.machine()
    os_display = f"{os_name} {os_release} ({arch})"

    # Privilege badge style
    priv_color = "bold #10b981" if not is_elevated else "bold #f59e0b"

    # Header text
    header = Text()
    header.append("💊  K A P S E L  ", style="bold #00f0ff")
    header.append("v0.1.0\n", style="dim #6b7280")
    header.append("跨平台自适应智能终端胶囊 · Wrap complexity, expose simplicity", style="italic #9ca3af")

    # Information grid
    grid = Table.grid(expand=True, padding=(0, 2))
    grid.add_column(style="bold #38bdf8", justify="right")
    grid.add_column(style="default")
    grid.add_column(style="bold #a855f7", justify="right")
    grid.add_column(style="default")

    grid.add_row(
        "🖥️ 宿主终端:",
        f"[bold #00f0ff]{shell_name}[/] [dim]({Path(shell_path).name})[/]",
        "🛡️ 运行权限:",
        f"[{priv_color}][{elevated_label}][/]",
    )
    grid.add_row(
        "💻 操作系统:",
        f"[#e4e4e7]{os_display}[/]",
        "📂 指令仓库:",
        f"[bold #10b981]{cmd_count}[/] 条 Linux 映射已就绪",
    )
    grid.add_row(
        "📦 独立沙箱:",
        f"[dim]{sandbox_dir}[/]",
        "⚡ 交互引擎:",
        "[bold #00f0ff]双态引擎 (Native ⇋ Kapsel)[/]",
    )

    # Quick tips
    tips = Table.grid(expand=True, padding=(0, 1))
    tips.add_column(style="bold #00f0ff", justify="left")
    tips.add_column(style="dim")
    tips.add_row(
        " ❯ [bold #00f0ff]kps <cmd>[/] [dim]跨平台映射模式 (如 kps rm -rf, kps ls -la)[/]",
        "[bold #a855f7]Tab[/] [dim]路径/指令补全[/]  |  [bold #a855f7]→[/] [dim]采纳历史预测[/]  |  [dim]'exit' 退出[/]",
    )

    # Combined content inside Panel
    content = Table.grid(expand=True, padding=(1, 0))
    content.add_column()
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
