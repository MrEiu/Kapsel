"""
Kapsel Dual-State Completer.
Seamlessly transitions between Native path completion and Kapsel rich Linux-First mappings.
"""

from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

from prompt_toolkit.completion import CompleteEvent, Completer, Completion, PathCompleter
from prompt_toolkit.document import Document
from prompt_toolkit.formatted_text import HTML

from kapsel.storage.commands import CommandEntry, CommandRegistry
from kapsel.storage.history import HistoryManager


_SUBCOMMAND_CACHE: Dict[str, List[Tuple[str, str]]] = {}


def get_subcommands_for_tool(tool: str) -> List[Tuple[str, str]]:
    """
    Dynamically loads tool subcommands from the local Hub SQLite database.
    Strictly follows the architectural manifesto:
    Zero hardcoding in code; data is stored in the Hub repository,
    synced to local SQLite, and loaded with in-memory caching (<1ms).
    """
    tool_lower = tool.lower()
    if tool_lower in _SUBCOMMAND_CACHE:
        return _SUBCOMMAND_CACHE[tool_lower]

    try:
        from kapsel.hub.hub_cmd import get_initialized_repo
        repo = get_initialized_repo()
        cmds = repo.get_commands_for_software(tool_lower)
        if cmds:
            result = [(c["command_name"], c["desc"]) for c in cmds]
            _SUBCOMMAND_CACHE[tool_lower] = result
            return result
    except Exception:
        pass
    return []


class DualStateCompleter(Completer):
    """
    Dual-State Completer:
    - Native Mode: Builtins, CLI subcommands (git/npm/docker/pip), and filesystem paths.
    - Kapsel Mode ('kps '): Rich perception menu with Chinese description and native preview.
    """

    def __init__(
        self,
        registry: CommandRegistry,
        history_mgr: HistoryManager,
        current_shell: str = "pwsh",
    ):
        self.registry = registry
        self.history_mgr = history_mgr
        self.current_shell = current_shell
        self.path_completer = PathCompleter(expanduser=True)

    def set_shell(self, shell: str) -> None:
        self.current_shell = shell

    def get_completions(
        self, document: Document, complete_event: CompleteEvent
    ) -> Iterable[Completion]:
        text_before = document.text_before_cursor
        stripped = text_before.lstrip()

        # 1. User is typing 'kps' (offer transition to Kapsel Mode)
        if stripped in ("k", "kp", "kps"):
            yield Completion(
                text="kps ",
                start_position=-len(stripped),
                display="kps ",
                display_meta="💊 进入跨平台智能胶囊模式",
            )
            return

        # 2. Kapsel Mode: starts with 'kps '
        if stripped.startswith("kps "):
            sub = stripped[4:]  # Text after 'kps '

            # Check if an existing alias already fully matches and there are trailing arguments
            match = self.registry.find_best_match(sub)
            if match and " " in sub:
                entry, raw_args = match
                if sub.startswith(entry.alias + " "):
                    for c in self.path_completer.get_completions(document, complete_event):
                        yield Completion(
                            text=c.text,
                            start_position=c.start_position,
                            display=c.display,
                            display_meta="📁 [参数路径]",
                        )
                    return

            # Otherwise, offer Kapsel command menu
            weights = self.history_mgr.get_command_weights()
            query = sub.lower()

            candidates = []
            for entry in self.registry.list_all():
                if query in entry.alias.lower() or not query:
                    score = weights.get(entry.alias, 0)
                    if entry.alias.lower().startswith(query):
                        score += 100
                    candidates.append((score, entry))

            # Include help, status, config, repo in kps mode if matching
            if not query or "help".startswith(query):
                candidates.append((150, CommandEntry(alias="help", desc="查看完整帮助手册与速查表", mapping={})))
            if not query or "status".startswith(query):
                candidates.append((140, CommandEntry(alias="status", desc="查看终端、权限与沙箱详细状态", mapping={})))
            if not query or "config".startswith(query):
                candidates.append((130, CommandEntry(alias="config", desc="查看、编辑与修改系统配置", mapping={})))
            if not query or "repo".startswith(query):
                candidates.append((128, CommandEntry(alias="repo", desc="📦 访问指令云仓库与拉取扩展", mapping={})))
            if not query or "register".startswith(query):
                candidates.append((125, CommandEntry(alias="register", desc="注册胶囊账户以备多端云同步", mapping={})))
            if not query or "whoami".startswith(query):
                candidates.append((120, CommandEntry(alias="whoami", desc="查看当前设备登录用户与同步状态", mapping={})))

            candidates.sort(key=lambda item: (item[0], -len(item[1].alias)), reverse=True)

            for _, entry in candidates:
                template = entry.get_template_for_shell(self.current_shell) or ""
                clean_preview = template.replace("{{args}}", "").strip()
                meta_text = f"💊 [胶囊] {entry.desc}  ➜  {clean_preview}" if clean_preview else f"🛠️ [内置] {entry.desc}"
                yield Completion(
                    text=entry.alias,
                    start_position=-len(sub),
                    display=entry.alias,
                    display_meta=meta_text,
                )
            return

        # 3. Native Mode: Check internal builtins first (only on the first word)
        words = stripped.split()
        if len(words) <= 1 and not text_before.endswith(" "):
            builtins = [
                ("help", "🛠️ [内置] 显示 Kapsel 帮助指南与命令手册"),
                ("status", "🛠️ [内置] 查看宿主Shell、权限与沙箱状态"),
                ("repo", "📦 [云仓库] 查询与拉取指令集 (类似 pip/scoop)"),
                ("hub", "📦 [云仓库] 指令与映射仓库管理"),
                ("config", "🛠️ [内置] 查看、编辑与修改核心配置 (~/.kapsel/config.yaml)"),
                ("register", "🛠️ [内置] 注册胶囊用户身份，为跨端云同步做准备"),
                ("whoami", "🛠️ [内置] 查看当前登录的胶囊用户与设备秘钥"),
                ("logout", "🛠️ [内置] 退出当前胶囊用户登录状态"),
                ("info", "🛠️ [内置] 查看系统与运行环境详细状态"),
                ("clear", "🛠️ [内置] 清除屏幕并重绘胶囊徽标"),
                ("exit", "🛠️ [内置] 退出 Kapsel 终端胶囊"),
            ]
            for cmd_name, desc in builtins:
                if stripped and cmd_name.startswith(stripped.lower()):
                    yield Completion(
                        text=cmd_name,
                        start_position=-len(stripped),
                        display=cmd_name,
                        display_meta=desc,
                    )

        # 4. Native Mode: Check CLI subcommands (dynamic from Hub SQLite database)
        if len(words) == 1 and text_before.endswith(" "):
            cmd = words[0].lower()
            subcmds = get_subcommands_for_tool(cmd)
            if subcmds:
                for subcmd, desc in subcmds:
                    yield Completion(
                        text=subcmd,
                        start_position=0,
                        display=subcmd,
                        display_meta=f"⚡ [{cmd}] {desc}",
                    )
                return
        elif len(words) == 2 and not text_before.endswith(" "):
            cmd = words[0].lower()
            sub_query = words[1].lower()
            subcmds = get_subcommands_for_tool(cmd)
            if subcmds:
                for subcmd, desc in subcmds:
                    if subcmd.lower().startswith(sub_query):
                        yield Completion(
                            text=subcmd,
                            start_position=-len(words[1]),
                            display=subcmd,
                            display_meta=f"⚡ [{cmd}] {desc}",
                        )
                return

        # 5. Native Mode: Delegate to native filesystem path completion
        for c in self.path_completer.get_completions(document, complete_event):
            yield Completion(
                text=c.text,
                start_position=c.start_position,
                display=c.display,
                display_meta="📁 [原生路径]",
            )

