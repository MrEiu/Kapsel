"""
Kapsel commands manager.
Manages Linux-First command mappings in ~/.kapsel/commands.yaml.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml

from kapsel.storage.logger import get_kapsel_dir, logger

DEFAULT_COMMANDS: List[Dict[str, Any]] = [
    {
        "alias": "rm -rf",
        "desc": "递归强制删除目录或文件",
        "mapping": {
            "powershell": "Remove-Item -Recurse -Force {{args}}",
            "cmd": "rmdir /S /Q {{args}}",
            "unix": "rm -rf {{args}}",
        },
    },
    {
        "alias": "rm",
        "desc": "删除文件或目录",
        "mapping": {
            "powershell": "Remove-Item {{args}}",
            "cmd": "del /Q {{args}}",
            "unix": "rm {{args}}",
        },
    },
    {
        "alias": "ls -la",
        "desc": "详细列出所有文件（含隐藏文件）",
        "mapping": {
            "zsh": "eza -la --icons {{args}}",
            "powershell": "Get-ChildItem -Force {{args}}",
            "cmd": "dir /Q /A {{args}}",
            "unix": "ls -la {{args}}",
        },
    },
    {
        "alias": "ll",
        "desc": "列表详细显示文件",
        "mapping": {
            "powershell": "Get-ChildItem -Force {{args}}",
            "cmd": "dir /A {{args}}",
            "unix": "ls -la {{args}}",
        },
    },
    {
        "alias": "ls",
        "desc": "列出当前目录内容",
        "mapping": {
            "powershell": "Get-ChildItem {{args}}",
            "cmd": "dir {{args}}",
            "unix": "ls {{args}}",
        },
    },
    {
        "alias": "cat",
        "desc": "查看或连接文件内容",
        "mapping": {
            "powershell": "Get-Content {{args}}",
            "cmd": "type {{args}}",
            "unix": "cat {{args}}",
        },
    },
    {
        "alias": "touch",
        "desc": "创建空文件或更新时间戳",
        "mapping": {
            "powershell": "New-Item -ItemType File -Force {{args}}",
            "cmd": "type nul >> {{args}}",
            "unix": "touch {{args}}",
        },
    },
    {
        "alias": "cp -r",
        "desc": "递归复制目录或文件",
        "mapping": {
            "powershell": "Copy-Item -Recurse -Force {{args}}",
            "cmd": "xcopy /E /I /Y {{args}}",
            "unix": "cp -r {{args}}",
        },
    },
    {
        "alias": "cp",
        "desc": "复制文件",
        "mapping": {
            "powershell": "Copy-Item -Force {{args}}",
            "cmd": "copy /Y {{args}}",
            "unix": "cp {{args}}",
        },
    },
    {
        "alias": "mv",
        "desc": "移动或重命名文件/目录",
        "mapping": {
            "powershell": "Move-Item -Force {{args}}",
            "cmd": "move /Y {{args}}",
            "unix": "mv {{args}}",
        },
    },
    {
        "alias": "mkdir -p",
        "desc": "递归创建多级目录",
        "mapping": {
            "powershell": "New-Item -ItemType Directory -Force {{args}}",
            "cmd": "mkdir {{args}}",
            "unix": "mkdir -p {{args}}",
        },
    },
    {
        "alias": "mkdir",
        "desc": "创建新目录",
        "mapping": {
            "powershell": "New-Item -ItemType Directory {{args}}",
            "cmd": "mkdir {{args}}",
            "unix": "mkdir {{args}}",
        },
    },
    {
        "alias": "ps",
        "desc": "查看当前正在运行的进程列表",
        "mapping": {
            "powershell": "Get-Process {{args}}",
            "cmd": "tasklist {{args}}",
            "unix": "ps aux {{args}}",
        },
    },
    {
        "alias": "kill -9",
        "desc": "强制终止指定进程",
        "mapping": {
            "powershell": "Stop-Process -Force -Id {{args}}",
            "cmd": "taskkill /F /PID {{args}}",
            "unix": "kill -9 {{args}}",
        },
    },
    {
        "alias": "kill",
        "desc": "正常终止进程",
        "mapping": {
            "powershell": "Stop-Process -Id {{args}}",
            "cmd": "taskkill /PID {{args}}",
            "unix": "kill {{args}}",
        },
    },
    {
        "alias": "killall",
        "desc": "按进程名称批量终止进程",
        "mapping": {
            "powershell": "Stop-Process -Force -Name {{args}}",
            "cmd": "taskkill /F /IM {{args}}.exe",
            "unix": "killall {{args}}",
        },
    },
    {
        "alias": "grep",
        "desc": "文本模式匹配与搜索",
        "mapping": {
            "powershell": "Select-String {{args}}",
            "cmd": "findstr {{args}}",
            "unix": "grep {{args}}",
        },
    },
    {
        "alias": "find",
        "desc": "在目录树中搜索匹配文件",
        "mapping": {
            "powershell": "Get-ChildItem -Recurse -Filter {{args}}",
            "cmd": "dir /S /B {{args}}",
            "unix": "find . -name {{args}}",
        },
    },
    {
        "alias": "curl",
        "desc": "发起网络请求",
        "mapping": {
            "powershell": "curl.exe {{args}}",
            "cmd": "curl.exe {{args}}",
            "unix": "curl {{args}}",
        },
    },
    {
        "alias": "which",
        "desc": "查找可执行命令的绝对路径",
        "mapping": {
            "powershell": "Get-Command {{args}}",
            "cmd": "where {{args}}",
            "unix": "which {{args}}",
        },
    },
    {
        "alias": "whereis",
        "desc": "定位可执行程序、源文件与文档",
        "mapping": {
            "powershell": "Get-Command {{args}}",
            "cmd": "where {{args}}",
            "unix": "whereis {{args}}",
        },
    },
    {
        "alias": "df -h",
        "desc": "查看磁盘文件系统空间使用情况",
        "mapping": {
            "powershell": "Get-PSDrive -PSProvider FileSystem",
            "cmd": "wmic logicaldisk get caption,freespace,size",
            "unix": "df -h",
        },
    },
    {
        "alias": "free -m",
        "desc": "查看系统物理与虚拟内存使用量",
        "mapping": {
            "powershell": "Get-CimInstance Win32_OperatingSystem | Select-Object TotalVisibleMemorySize,FreePhysicalMemory",
            "cmd": "systeminfo",
            "unix": "free -m",
        },
    },
    {
        "alias": "clear",
        "desc": "清除终端屏幕内容",
        "mapping": {
            "powershell": "Clear-Host",
            "cmd": "cls",
            "unix": "clear",
        },
    },
    {
        "alias": "ifconfig",
        "desc": "查看或配置网络接口地址",
        "mapping": {
            "powershell": "Get-NetIPAddress",
            "cmd": "ipconfig /all",
            "unix": "ifconfig",
        },
    },
    {
        "alias": "ip a",
        "desc": "显示所有网卡 IP 地址信息",
        "mapping": {
            "powershell": "Get-NetIPAddress",
            "cmd": "ipconfig",
            "unix": "ip a",
        },
    },
    {
        "alias": "env",
        "desc": "查看当前环境变量列表",
        "mapping": {
            "powershell": "Get-ChildItem env:",
            "cmd": "set",
            "unix": "env",
        },
    },
    {
        "alias": "printenv",
        "desc": "打印所有或指定环境变量",
        "mapping": {
            "powershell": "Get-ChildItem env:{{args}}",
            "cmd": "set {{args}}",
            "unix": "printenv {{args}}",
        },
    },
    {
        "alias": "head",
        "desc": "显示文件开头前若干行",
        "mapping": {
            "powershell": "Get-Content -Head 10 {{args}}",
            "cmd": "powershell -NoProfile -Command \"Get-Content -Head 10 {{args}}\"",
            "unix": "head {{args}}",
        },
    },
    {
        "alias": "tail",
        "desc": "显示文件末尾若干行",
        "mapping": {
            "powershell": "Get-Content -Tail 10 {{args}}",
            "cmd": "powershell -NoProfile -Command \"Get-Content -Tail 10 {{args}}\"",
            "unix": "tail {{args}}",
        },
    },
    {
        "alias": "tail -f",
        "desc": "动态实时跟踪查看文件末尾内容",
        "mapping": {
            "powershell": "Get-Content -Wait -Tail 20 {{args}}",
            "cmd": "powershell -NoProfile -Command \"Get-Content -Wait -Tail 20 {{args}}\"",
            "unix": "tail -f {{args}}",
        },
    },
    {
        "alias": "uptime",
        "desc": "查看系统运行时间",
        "mapping": {
            "powershell": "(Get-Date) - (Get-CimInstance Win32_OperatingSystem).LastBootUpTime",
            "cmd": "net statistics workstation",
            "unix": "uptime",
        },
    },
    {
        "alias": "whoami",
        "desc": "查看当前登录用户名与主机",
        "mapping": {
            "powershell": "whoami",
            "cmd": "whoami",
            "unix": "whoami",
        },
    },
    {
        "alias": "pwd",
        "desc": "打印当前工作目录绝对路径",
        "mapping": {
            "powershell": "(Get-Location).Path",
            "cmd": "cd",
            "unix": "pwd",
        },
    },
    {
        "alias": "tar -czvf",
        "desc": "使用 gzip 压缩打包文件或目录",
        "mapping": {
            "powershell": "tar.exe -czvf {{args}}",
            "cmd": "tar.exe -czvf {{args}}",
            "unix": "tar -czvf {{args}}",
        },
    },
    {
        "alias": "tar -xzvf",
        "desc": "解压 tar.gz 归档文件",
        "mapping": {
            "powershell": "tar.exe -xzvf {{args}}",
            "cmd": "tar.exe -xzvf {{args}}",
            "unix": "tar -xzvf {{args}}",
        },
    },
]


@dataclass
class CommandEntry:
    alias: str
    desc: str
    mapping: Dict[str, str]

    def get_template_for_shell(self, shell: str) -> Optional[str]:
        """
        Lookup template with multi-tier fallback:
        1. Exact shell match ('pwsh', 'powershell', 'cmd', 'zsh', 'bash', 'fish')
        2. PowerShell fallback (pwsh -> powershell, powershell -> pwsh)
        3. OS-level fallback ('windows' / 'unix')
        4. Global fallback to unix mapping or first available
        """
        # Exact shell
        if shell in self.mapping:
            return self.mapping[shell]

        # pwsh / powershell alias
        if shell == "pwsh" and "powershell" in self.mapping:
            return self.mapping["powershell"]
        if shell == "powershell" and "pwsh" in self.mapping:
            return self.mapping["pwsh"]

        # Family fallback
        if shell in ("cmd", "powershell", "pwsh"):
            if "windows" in self.mapping:
                return self.mapping["windows"]
        else:
            if "unix" in self.mapping:
                return self.mapping["unix"]

        # Final fallback
        return self.mapping.get("unix") or next(iter(self.mapping.values()), None)


class CommandRegistry:
    def __init__(self, commands: Optional[List[CommandEntry]] = None):
        self.commands: List[CommandEntry] = commands or []
        self._alias_map: Dict[str, CommandEntry] = {c.alias: c for c in self.commands}

    def get(self, alias: str) -> Optional[CommandEntry]:
        return self._alias_map.get(alias)

    def find_best_match(self, input_text: str) -> Optional[tuple[CommandEntry, str]]:
        """
        Matches the longest matching alias from input_text.
        e.g., 'rm -rf node_modules' -> (CommandEntry('rm -rf'), 'node_modules')
        Returns (entry, remainder_args) or None.
        """
        cleaned = input_text.strip()
        # Sort aliases by descending length so "rm -rf" matches before "rm"
        sorted_entries = sorted(self.commands, key=lambda e: len(e.alias), reverse=True)
        for entry in sorted_entries:
            if cleaned == entry.alias:
                return entry, ""
            if cleaned.startswith(entry.alias + " "):
                args = cleaned[len(entry.alias) + 1:].strip()
                return entry, args
        return None

    def list_all(self) -> List[CommandEntry]:
        return self.commands


def get_commands_path() -> Path:
    return get_kapsel_dir() / "commands.yaml"


def load_commands() -> CommandRegistry:
    """Load commands.yaml or initialize with default commands."""
    path = get_commands_path()
    if not path.exists():
        save_default_commands(path)
        entries = [CommandEntry(**item) for item in DEFAULT_COMMANDS]
        return CommandRegistry(entries)

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        raw_list = data.get("commands", [])
        entries = []
        for item in raw_list:
            if isinstance(item, dict) and "alias" in item and "desc" in item and "mapping" in item:
                entries.append(CommandEntry(
                    alias=item["alias"],
                    desc=item["desc"],
                    mapping=item["mapping"],
                ))
        if not entries:
            # Fallback if empty
            entries = [CommandEntry(**item) for item in DEFAULT_COMMANDS]
        return CommandRegistry(entries)
    except Exception as e:
        logger.error(f"Error loading commands from {path}: {e}")
        entries = [CommandEntry(**item) for item in DEFAULT_COMMANDS]
        return CommandRegistry(entries)


def save_default_commands(path: Path) -> None:
    try:
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump({"commands": DEFAULT_COMMANDS}, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        logger.info(f"Initialized default commands at {path}")
    except Exception as e:
        logger.error(f"Failed to write default commands: {e}")
