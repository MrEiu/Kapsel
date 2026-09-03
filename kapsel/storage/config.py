"""
Kapsel configuration loader and generator.
Manages ~/.kapsel/config.yaml with comprehensive options and comments.
"""

from dataclasses import asdict, dataclass, field
import os
from pathlib import Path
import subprocess
import sys
from typing import Any, Dict, Optional
import yaml

from kapsel.storage.logger import get_kapsel_dir, logger

DEFAULT_CONFIG: Dict[str, Any] = {
    "version": "1.1",
    "interaction": {
        "autosuggest_tap_mode": "word",        # "word" (逐词采纳) 或 "full" (一键采纳整行)
        "autosuggest_hold_action": "full",     # "full" (长按/连按整行采纳)
        "autosuggest_sensitivity": 0.25,       # 连按/长按判定时间敏感度阈值 (秒)
        "consecutive_press_threshold": 2,      # 判定为连续长按的击键次数
    },
    "ui": {
        "enable_banner": True,
        "enable_timing": True,
        "enable_autosuggest": True,
        "enable_card_border": True,
        "show_git_branch": True,
        "show_shell_badge": True,
        "show_timestamp": True,
        "prompt_symbols": {
            "top": "╭─",
            "bottom": "╰─",
            "arrow": "❯",
            "capsule": "💊",
            "branch": "",
            "folder": "📁",
            "success": "✔",
            "failure": "✘",
            "clock": "⏱",
        },
    },
    "theme": {
        "name": "cyber_dark",
        "primary": "#00f0ff",      # Cyan accent
        "primary_dim": "#0891b2",
        "secondary": "#a855f7",    # Purple accent
        "success": "#10b981",      # Emerald green
        "warning": "#f59e0b",      # Amber
        "error": "#f43f5e",        # Neon red
        "dim": "#6b7280",          # Dark gray
    },
    "routing": {
        "prefer_modern_tools": True,
        "default_fallback_shell": "unix",
        "auto_strip_spaces": True,
    },
    "history": {
        "max_memory_entries": 20,
        "frequency_learning": True,
    },
    "cloud": {
        "hub_repo_url": "https://raw.githubusercontent.com/kapsel/KPS-Hub/main",
        "server_endpoint": "http://127.0.0.1:8000",
        "auto_check_update": False,
    },
    "sync": {
        "enable_auto_sync": False,
        "sync_timeout_seconds": 5,
    },
}

DEFAULT_CONFIG_COMMENTED_YAML = """# ==============================================================================
#  💊 Kapsel 终端胶囊系统全局总核心配置文件
#  文件位置: ~/.kapsel/config.yaml
#  说明: 修改本文件后可通过 'config reload' 即刻生效，无需重启终端。
# ==============================================================================

version: "1.2"

# ------------------------------------------------------------------------------
# 1. 交互与右箭头灵敏度行为 (Interaction & Sensitivity)
# ------------------------------------------------------------------------------
interaction:
  # 右方向键 (→) 历史预测单次点按 (Tap) 模式:
  #   - "word": 单次轻按逐词采纳 (Word-by-word，方便部分复用历史参数)
  #   - "full": 单次轻按直接一键采纳整行命令
  autosuggest_tap_mode: "word"

  # 右方向键 (→) 长按/连续按 (Hold / Continuous Press) 触发行为:
  #   - "full": 长按直接一键采纳整行完整命令
  autosuggest_hold_action: "full"

  # 连按/长按判定敏感度阈值 (单位: 秒, 建议 0.15 ~ 0.40):
  # 两次按键时间间隔小于此阈值即判定为长按或连续按，触发 autosuggest_hold_action。
  autosuggest_sensitivity: 0.25

  # 判定为长按/连按所需达到的连续击键次数 (默认 2 次)
  consecutive_press_threshold: 2

# ------------------------------------------------------------------------------
# 2. 界面与视觉封装控制 (UI & Visuals)
# ------------------------------------------------------------------------------
ui:
  # 是否在启动时显示极简胶囊 Logo 徽标
  enable_banner: true

  # 是否在命令执行完成后显示耗时 (ms/s) 与状态徽章 (✔/✘)
  enable_timing: true

  # 是否启用基于历史记录的暗灰色行内实时预测 (Autosuggestion)
  enable_autosuggest: true

  # 是否启用闭环卡片边框 (╭─ ❯ 与 ╰─)
  enable_card_border: true

  # 提示行是否显示当前 Git 激活分支
  show_git_branch: true

  # 提示行是否显示当前外层 Shell 徽章 (如 [pwsh], [cmd])
  show_shell_badge: true

  # 提示行是否显示当前执行时间戳
  show_timestamp: true

  # 提示行与卡片边框连线符号设置
  prompt_symbols:
    top: "╭─"
    bottom: "╰─"
    arrow: "❯"
    capsule: "💊"
    branch: ""
    folder: "📁"
    success: "✔"
    failure: "✘"
    clock: "⏱"

# ------------------------------------------------------------------------------
# 3. 颜色主题调色板 (Theme Palette)
# ------------------------------------------------------------------------------
theme:
  name: "cyber_dark"
  primary: "#00f0ff"        # 核心主色 (电光青蓝)
  primary_dim: "#0891b2"    # 边框深青
  secondary: "#a855f7"      # 辅助高亮 (霓虹紫)
  success: "#10b981"        # 成功徽标 (翡翠绿)
  warning: "#f59e0b"        # 警告/权限 (琥珀黄)
  error: "#f43f5e"          # 错误退出 (霓虹红)
  dim: "#6b7280"            # 暗灰注释/时间戳

# ------------------------------------------------------------------------------
# 4. 终端路由与命令降级 (Terminal Routing)
# ------------------------------------------------------------------------------
routing:
  # 优先采用现代化替代工具 (如检测到时优先采用 eza 代替 ls，bat 代替 cat)
  prefer_modern_tools: true

  # 未精准匹配时的默认回退 Shell 族 ('unix' 或 'windows')
  default_fallback_shell: "unix"

  # 自动清理参数替换中的多余空字符
  auto_strip_spaces: true

# ------------------------------------------------------------------------------
# 5. 独立历史记录漫游库 (History Storage)
# ------------------------------------------------------------------------------
history:
  # 跨会话保留与加载的最近历史记录条数 (默认 20 条，可自由配置)
  max_memory_entries: 20

  # 是否开启高频命令智能权重学习 (高频命令在补全中优先置顶)
  frequency_learning: true

# ------------------------------------------------------------------------------
# 6. 云端服务与仓库源设置 (Cloud Hub & Service)
# ------------------------------------------------------------------------------
cloud:
  # KPS-Hub 公共指令集源地址 (GitHub Raw 或加速 CDN)
  hub_repo_url: "https://raw.githubusercontent.com/kapsel/KPS-Hub/main"

  # KPS-Server 私有漫游用户服务网关地址
  server_endpoint: "http://127.0.0.1:8000"

  # 是否在客户端启动时异步检查指令库最新版本
  auto_check_update: false

# ------------------------------------------------------------------------------
# 7. 跨端漫游与加密同步 (Sync Settings)
# ------------------------------------------------------------------------------
sync:
  # 是否开启多设备配置与历史自动漫游
  enable_auto_sync: false

  # 同步网络请求超时秒数
  sync_timeout_seconds: 5
"""


@dataclass
class KapselConfig:
    raw: Dict[str, Any] = field(default_factory=lambda: DEFAULT_CONFIG.copy())

    @property
    def interaction(self) -> Dict[str, Any]:
        return self.raw.get("interaction", DEFAULT_CONFIG["interaction"])

    @property
    def theme(self) -> Dict[str, str]:
        return self.raw.get("theme", DEFAULT_CONFIG["theme"])

    @property
    def ui(self) -> Dict[str, Any]:
        return self.raw.get("ui", DEFAULT_CONFIG["ui"])

    @property
    def symbols(self) -> Dict[str, str]:
        return self.ui.get("prompt_symbols", DEFAULT_CONFIG["ui"]["prompt_symbols"])

    @property
    def enable_banner(self) -> bool:
        return self.ui.get("enable_banner", True)

    @property
    def enable_timing(self) -> bool:
        return self.ui.get("enable_timing", True)

    @property
    def enable_autosuggest(self) -> bool:
        return self.ui.get("enable_autosuggest", True)

    @property
    def enable_card_border(self) -> bool:
        return self.ui.get("enable_card_border", True)

    @property
    def autosuggest_tap_mode(self) -> str:
        return self.interaction.get("autosuggest_tap_mode", "word")

    @property
    def autosuggest_sensitivity(self) -> float:
        return float(self.interaction.get("autosuggest_sensitivity", 0.25))

    @property
    def consecutive_press_threshold(self) -> int:
        return int(self.interaction.get("consecutive_press_threshold", 2))

    @property
    def history_entries(self) -> int:
        return int(self.raw.get("history", {}).get("max_memory_entries", 20))


def get_config_path() -> Path:
    return get_kapsel_dir() / "config.yaml"


def load_config() -> KapselConfig:
    """Load config.yaml from sandbox directory or generate with default values."""
    config_path = get_config_path()
    if not config_path.exists():
        save_default_config(config_path)
        return KapselConfig(DEFAULT_CONFIG)

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        # Deep merge defaults
        merged = _deep_copy_dict(DEFAULT_CONFIG)
        _deep_merge(merged, data)
        return KapselConfig(merged)
    except Exception as e:
        logger.error(f"Failed to load config from {config_path}: {e}")
        return KapselConfig(DEFAULT_CONFIG)


def save_default_config(path: Path) -> None:
    """Save commented default config to the given path."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(DEFAULT_CONFIG_COMMENTED_YAML)
        logger.info(f"Initialized commented default config at {path}")
    except Exception as e:
        logger.error(f"Failed to write default config: {e}")


def update_config_value(section_or_key: str, subkey_or_value: Any, value: Optional[Any] = None) -> bool:
    """
    Updates a config key and writes back to ~/.kapsel/config.yaml.
    Supports either (section, key, val) e.g. update_config_value('interaction', 'autosuggest_sensitivity', 0.2)
    or shortcut (key, val) e.g. update_config_value('autosuggest_sensitivity', 0.2)
    """
    path = get_config_path()
    if not path.exists():
        save_default_config(path)

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        if value is not None:
            section = section_or_key
            key = subkey_or_value
            val = value
            if section not in data or not isinstance(data[section], dict):
                data[section] = {}
            data[section][key] = val
        else:
            # Look for key in top-level or sub-dictionaries
            key = section_or_key
            val = subkey_or_value
            found = False
            for sec, subdict in data.items():
                if isinstance(subdict, dict) and key in subdict:
                    subdict[key] = val
                    found = True
                    break
            if not found:
                data[key] = val

        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        return True
    except Exception as e:
        logger.error(f"Failed to update config: {e}")
        return False


def _deep_copy_dict(d: Dict[str, Any]) -> Dict[str, Any]:
    res = {}
    for k, v in d.items():
        if isinstance(v, dict):
            res[k] = _deep_copy_dict(v)
        elif isinstance(v, list):
            res[k] = list(v)
        else:
            res[k] = v
    return res


def _deep_merge(source: Dict[str, Any], destination: Dict[str, Any]) -> Dict[str, Any]:
    for k, v in destination.items():
        if isinstance(v, dict) and k in source and isinstance(source[k], dict):
            _deep_merge(source[k], v)
        else:
            source[k] = v
    return source
