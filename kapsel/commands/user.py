"""
Kapsel User Registration and Identity CLI command handlers.
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

from kapsel.storage.user_db import get_user_db
from kapsel.sync.client import SyncClient
from kapsel.sync.device import generate_sync_key, get_device_id
from kapsel.ui.banner import ensure_utf8_io


def handle_register_command(args: List[str], console: Optional[Console] = None) -> int:
    """Handles the 'register' command to set up cloud synchronization profile."""
    ensure_utf8_io()
    con = console or Console(legacy_windows=False)

    user_db = get_user_db()
    current = user_db.get_active_user()
    if current:
        con.print(f"[bold #f59e0b]当前设备已注册用户:[/] [bold #00f0ff]@{current['username']}[/]")
        con.print("[dim]如需重新注册或切换账号，请先执行 'logout' 后再试。[/]")
        return 0

    username = ""
    email = ""

    if args:
        username = args[0]
        for i, arg in enumerate(args):
            if arg in ("--email", "-e") and i + 1 < len(args):
                email = args[i + 1]

    if not username:
        con.print("\n[bold #00f0ff]💊 欢迎加入 Kapsel 跨平台云漫游生态[/]")
        con.print("[dim]请设置您的胶囊用户名（用于跨系统配置同步与历史漫游）：[/]")
        try:
            if sys.stdin.isatty():
                username = prompt("❯ 期望用户名 (例如 meru): ").strip()
            else:
                username = input("❯ 期望用户名: ").strip()
        except (KeyboardInterrupt, EOFError):
            con.print("\n[dim]取消注册。[/]")
            return 1
        except Exception:
            username = "user"

    if not username or not re.match(r"^[a-zA-Z0-9_\-\.]{2,32}$", username):
        con.print("[bold #f43f5e]✘ 用户名格式不合法[/]: 仅支持 2-32 位字母、数字、下划线、减号或点。")
        return 1

    if not email and sys.stdin.isatty():
        try:
            entered_email = prompt("❯ 关联邮箱 [选填，按回车跳过]: ").strip()
            if entered_email:
                email = entered_email
        except Exception:
            pass

    sync_key = generate_sync_key()
    device_id = get_device_id()

    # Save to centralized user.db
    user_db.save_user(username=username, sync_key=sync_key, device_id=device_id, email=email)

    # Attempt cloud server registration
    client = SyncClient()
    cloud_res = client.register_user(username=username, sync_key=sync_key, device_id=device_id, email=email)

    profile_dict = {
        "username": username,
        "email": email,
        "device_id": device_id,
        "sync_key": sync_key,
        "cloud_status": cloud_res.get("success", False),
    }

    render_registration_success(profile_dict, con)
    return 0


def handle_whoami_command(args: List[str], console: Optional[Console] = None) -> int:
    """Handles 'whoami' or 'user' command to inspect active digital credentials."""
    ensure_utf8_io()
    con = console or Console(legacy_windows=False)

    user_db = get_user_db()
    current = user_db.get_active_user()

    if not current:
        con.print("\n[bold #f59e0b]当前设备尚未登录或注册胶囊账号。[/]")
        con.print("[dim]您可运行 'register <username>' 立即创建身份并开启跨端云同步。\n[/]")
        return 0

    grid = Table.grid(expand=True, padding=(0, 2))
    grid.add_column(style="bold #00f0ff", justify="right", width=18)
    grid.add_column(style="#e4e4e7")

    grid.add_row("👤 胶囊用户名:", f"[bold #00f0ff]@{current['username']}[/]")
    grid.add_row("📧 关联邮箱:", current["email"] or "[dim]未绑定[/]")
    grid.add_row("🖥️ 硬件设备指纹:", f"[bold #a855f7]{current['device_id']}[/] [dim](自动绑定当前机器)[/]")
    grid.add_row("🔑 漫游同步秘钥:", f"[bold #10b981]{current['sync_key'][:16]}****************[/] [dim](AES-256 加密凭据)[/]")
    grid.add_row("📅 注册激活时间:", str(current["registered_at"]))
    grid.add_row("☁️ 存储位置:", f"[dim]{user_db.db_path} (SQLite)[/]")

    header = Text()
    header.append("🛡️ KAPSEL 用户身份与漫游凭证面板\n", style="bold #00f0ff")
    header.append("数据已在本地加密沙箱存储，秘钥请妥善保管，切勿泄露给第三方。\n", style="dim #6b7280")

    content = Table.grid(expand=True, padding=(1, 0))
    content.add_column()
    content.add_row(header)
    content.add_row(grid)

    panel = Panel(
        content,
        border_style="#0891b2",
        padding=(1, 2),
        expand=False,
    )
    con.print()
    con.print(panel)
    con.print()
    return 0


def handle_logout_command(args: List[str], console: Optional[Console] = None) -> int:
    """Handles 'logout' command to sign out of the active capsule roaming profile."""
    ensure_utf8_io()
    con = console or Console(legacy_windows=False)

    user_db = get_user_db()
    current = user_db.get_active_user()
    if not current:
        con.print("[dim]当前未登录任何账号。[/]")
        return 0

    success = user_db.logout_active_user()
    if success:
        con.print(f"[bold #10b981]✔ 已成功退出当前胶囊漫游身份 (@{current['username']})！[/]")
        con.print("[dim]本地执行历史与映射保留，随时可通过 'register' 重新配对。[/]")
    return 0


def render_registration_success(profile: dict, console: Console) -> None:
    cloud_status_msg = "[bold #10b981]● 云端服务注册成功[/]" if profile.get("cloud_status") else "[dim]○ 本地沙箱注册成功 (等待云服务上线)[/]"

    grid = Table.grid(expand=True, padding=(0, 2))
    grid.add_column(style="bold #00f0ff", justify="right", width=18)
    grid.add_column(style="#e4e4e7")

    grid.add_row("👤 胶囊用户名:", f"[bold #00f0ff]@{profile['username']}[/]")
    grid.add_row("📧 绑定邮箱:", profile.get("email") or "[dim]未绑定[/]")
    grid.add_row("🖥️ 硬件设备指纹:", f"[bold #a855f7]{profile['device_id']}[/] [dim](本机唯一标识)[/]")
    grid.add_row("🔑 漫游同步秘钥:", f"[bold #10b981]{profile['sync_key']}[/]")
    grid.add_row("☁️ 同步连接状态:", cloud_status_msg)

    header = Text()
    header.append("🎉 恭喜！Kapsel 胶囊漫游账号创建成功\n", style="bold #10b981")
    header.append("您的设备指纹与端到端加密同步秘钥已在本地 user.db 数据库安全就绪。\n", style="dim #6b7280")

    content = Table.grid(expand=True, padding=(1, 0))
    content.add_column()
    content.add_row(header)
    content.add_row(grid)

    panel = Panel(
        content,
        border_style="#10b981",
        padding=(1, 2),
        expand=False,
    )
    console.print()
    console.print(panel)
    console.print()
