"""
Kapsel Install Services Module (Empty Skeleton Placeholder).
Reserved for future dedicated package and toolchain installation services.
"""

from typing import List, Optional
from rich.console import Console

# Reserved extensibility slot for future package/toolchain installer implementations.


def handle_install(args: List[str], console: Optional[Console] = None) -> int:
    con = console or Console()
    con.print("[dim]📦 Kapsel 安装服务骨架已就绪（等待未来专属安装服务接入）。[/]")
    return 0
