"""
Kapsel user registration and identity CLI command handlers.
Implements 'register', 'whoami', 'logout' commands for multi-system cloud sync readiness.
"""

import re
import sys
from typing import List, Optional

from prompt_toolkit import prompt
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from kapsel.storage.user import UserManager, UserProfile, get_user_file_path
from kapsel.ui.banner import ensure_utf8_io


def handle_register_command(args: List[str], console: Optional[Console] = None) -> int:
    """Handles the 'register' command to set up cloud synchronization profile."""
    ensure_utf8_io()
    if console is None:
        console = Console(legacy_windows=False)

    current = UserManager.get_current_user()
    if current:
        console.print(f"[bold #f59e0b]当前设备已注册用户:[/] [bold #00f0ff]@{current.username}[/]")
        console.print("[dim]如需重新注册或切换账号，请先执行 'logout' 后再试。[/]")
        return 0

    username = ""
    email = ""

    # Parse args if provided: register <username> [--email <email>]
    if args:
        username = args[0]
        for i, arg in enumerate(args):
            if arg in ("--email", "-e") and i + 1 < len(args):
                email = args[i + 1]

    # Interactive prompt if username not provided
    if not username:
        console.print("\n[bold #00f0ff]💊 欢迎加入 Kapsel 跨平台云漫游生态[/]")
        console.print("[dim]请设置您的胶囊用户名（用于跨系统配置同步与历史漫游）：[/]")
        try:
            username = prompt("❯ 期望用户名 (例如 meru): ").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]取消注册。[/]")
            return 1

    # Validate username
    if not username or not re.match(r"^[a-zA-Z0-9_\-\.]{2,32}$", username):
        console.print("[bold #f43f5e]✘ 用户名格式不合法[/]: 仅支持 2-32 位字母、数字、下划线、减号或点。")
        return 1

    # Interactive prompt for email if not provided
    if not email:
        try:
            entered_email = prompt("❯ 关联邮箱 [选填，按回车跳过]: ").strip()
            if entered_email:
                email = entered_email
        except (KeyboardInterrupt, EOFError):
            pass

    # Register user
    profile = UserManager.register(username=username, email=email)

    # Render Welcome Card
    render_registration_success(profile, console)
    return 0


def handle_whoami_command(console: Optional[Console] = None) -> int:
    """Handles 'whoami' / 'user' command to show active identity and cloud sync status."""
    ensure_utf8_io()
    if console is None:
        console = Console(legacy_windows=False)

    user = UserManager.get_current_user()
    if not user:
        console.print("[dim]当前尚未注册 Kapsel 用户。[/]")
        console.print("输入 [bold #00f0ff]'register <用户名>'[/] 即可快速创建账号，开启云端多端漫游准备！")
        return 0

    grid = Table.grid(expand=True, padding=(0, 2))
    grid.add_column(style="bold #00f0ff", justify="right", width=18)
    grid.add_column(style="#e4e4e7")
    grid.add_column(style="bold #a855f7", justify="right", width=18)
    grid.add_column(style="#e4e4e7")

    grid.add_row(
        "👤 胶囊用户名:",
        f"[bold #00f0ff]@{user.username}[/]",
        "📧 关联邮箱:",
        f"{user.email}" if user.email else "[dim]未绑定[/]",
    )
    grid.add_row(
        "💻 当前接入设备:",
        f"{user.device_name} [dim]({user.device_os})[/]",
        "🆔 设备指纹 ID:",
        f"[dim]{user.device_id}[/]",
    )
    grid.add_row(
        "🔑 跨端同步秘钥:",
        f"[bold #10b981]{user.sync_key[:14]}...[/] [dim](已加密存储)[/]",
        "🕒 注册时间:",
        f"[dim]{user.created_at}[/]",
    )
    grid.add_row(
        "☁️ 云端同步状态:",
        "[bold #10b981]● 就绪 (Ready for Cloud Sync)[/]",
        "🌐 同步服务地址:",
        f"[dim]{user.cloud_server}[/]",
    )

    content = Table.grid(expand=True, padding=(1, 0))
    content.add_column()

    header = Text()
    header.append("💊 KAPSEL 当前已登录用户信息\n", style="bold #00f0ff")
    header.append("跨端自适应智能终端胶囊 · 多系统漫游账户中心", style="dim italic")

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
    return 0


def handle_logout_command(console: Optional[Console] = None) -> int:
    """Handles 'logout' command."""
    ensure_utf8_io()
    if console is None:
        console = Console(legacy_windows=False)

    user = UserManager.get_current_user()
    if not user:
        console.print("[dim]当前没有已登录的 Kapsel 用户。[/]")
        return 0

    success = UserManager.logout()
    if success:
        console.print(f"[bold #10b981]✔ 用户 @{user.username} 已安全退出，本地凭据已清除。[/]")
    else:
        console.print("[bold #f43f5e]✘ 退出登录失败。[/]")
    return 0


def render_registration_success(profile: UserProfile, console: Console) -> None:
    """Renders high-aesthetic celebration card upon registration."""
    grid = Table.grid(expand=True, padding=(0, 2))
    grid.add_column(style="bold #00f0ff", justify="right", width=18)
    grid.add_column(style="#e4e4e7")

    grid.add_row("👤 胶囊用户名:", f"[bold #00f0ff]@{profile.username}[/]")
    grid.add_row("📧 绑定邮箱:", f"{profile.email}" if profile.email else "[dim]未绑定[/]")
    grid.add_row("💻 注册设备:", f"{profile.device_name} [dim]({profile.device_os})[/]")
    grid.add_row("🆔 唯一设备指纹:", f"[dim]{profile.device_id}[/]")
    grid.add_row("🔑 跨端同步秘钥:", f"[bold #10b981]{profile.sync_key}[/]")
    grid.add_row("📦 凭证存储沙箱:", f"[dim]{get_user_file_path()}[/]")
    grid.add_row("☁️ 多系统漫游:", "[bold #10b981]● 云同步环境已就绪[/]")

    notice = Text()
    notice.append("\n🌟 跨端同步说明:\n", style="bold #a855f7")
    notice.append("  本设备已成功创建唯一数字身份。后续在 macOS、Linux 或其它 Windows 机器上，\n", style="dim")
    notice.append("  可通过您的同步秘钥快速同步 commands.yaml 与漫游历史！\n", style="dim")

    content = Table.grid(expand=True, padding=(1, 0))
    content.add_column()

    header = Text()
    header.append("🎉 恭喜！Kapsel 胶囊账号注册成功\n", style="bold #10b981")
    header.append("已为当前设备生成专属端到端加密同步凭据\n", style="dim italic")

    content.add_row(header)
    content.add_row(grid)
    content.add_row(notice)

    panel = Panel(
        content,
        border_style="#10b981",
        padding=(1, 2),
        expand=False,
    )
    console.print()
    console.print(panel)
    console.print()
