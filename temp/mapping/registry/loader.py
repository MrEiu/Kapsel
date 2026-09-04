"""
Kapsel Folder-Based Registry Loader.
Stores command manifests and mapping sets in directory structures matching the Git repository:
~/.kapsel/registry/
  ├── manifests/   (e.g. scoop.json, git.json, docker.json, python.json, npm.json)
  └── mappings/    (e.g. pwsh.json)
"""

import json
from pathlib import Path
import shutil
from typing import Any, Dict, List

from kapsel.storage.logger import get_kapsel_dir, logger


def get_registry_dir() -> Path:
    """Returns ~/.kapsel/registry (or within KAPSEL_HOME)."""
    reg_dir = get_kapsel_dir() / "registry"
    reg_dir.mkdir(parents=True, exist_ok=True)
    return reg_dir


def get_manifests_dir() -> Path:
    d = get_registry_dir() / "manifests"
    d.mkdir(parents=True, exist_ok=True)
    return d


def get_mappings_dir() -> Path:
    d = get_registry_dir() / "mappings"
    d.mkdir(parents=True, exist_ok=True)
    return d


def ensure_registry_populated() -> None:
    """
    Ensures the folder-based registry has baseline manifests and mappings.
    If the directory is empty, copies initial files from KPS-Hub or internal defaults.
    """
    manifests_dir = get_manifests_dir()
    mappings_dir = get_mappings_dir()

    # If manifests exist, nothing needed
    if any(manifests_dir.glob("*.json")):
        return

    # Check if KPS-Hub workspace folder exists to copy from
    workspace_kps_hub = Path(__file__).resolve().parent.parent.parent.parent / "KPS-Hub"
    if (workspace_kps_hub / "manifests").exists():
        for f in (workspace_kps_hub / "manifests").glob("*.json"):
            shutil.copy2(f, manifests_dir / f.name)
        for f in (workspace_kps_hub / "mappings").glob("*.json"):
            shutil.copy2(f, mappings_dir / f.name)
        logger.info("Initialized local registry folder from KPS-Hub workspace files.")
        return

    # Fallback minimal embedded seed
    _seed_minimal_manifests_and_mappings(manifests_dir, mappings_dir)


def _seed_minimal_manifests_and_mappings(manifests_dir: Path, mappings_dir: Path) -> None:
    default_scoop = {
        "platform": "windows",
        "software": "scoop",
        "display_name": "Scoop (Windows 命令行包管理器)",
        "version": "0.3.1",
        "desc": "Windows 开发者最爱的高雅、无污染、用户目录级包管理器",
        "category": "package_manager",
        "author": "Scoop Community",
        "commands": [
            {"command_name": "install", "full_alias": "scoop install", "desc": "一键静默下载并安装指定软件", "example": "scoop install git"},
            {"command_name": "update", "full_alias": "scoop update", "desc": "更新 scoop 本体或指定已安装应用", "example": "scoop update *"},
            {"command_name": "status", "full_alias": "scoop status", "desc": "检查已安装软件中是否有可用更新", "example": "scoop status"},
            {"command_name": "list", "full_alias": "scoop list", "desc": "展示当前系统通过 scoop 已安装的应用清单", "example": "scoop list"},
            {"command_name": "search", "full_alias": "scoop search", "desc": "在官方与第三方 bucket 中模糊搜索软件包", "example": "scoop search ripgrep"},
        ],
    }
    with open(manifests_dir / "scoop.json", "w", encoding="utf-8") as f:
        json.dump(default_scoop, f, indent=2, ensure_ascii=False)

    default_git = {
        "platform": "universal",
        "software": "git",
        "display_name": "Git 分布式版本控制系统",
        "version": "2.44.0",
        "desc": "全球最流行的分布式代码版本管理工具",
        "category": "vcs",
        "author": "Git Community",
        "commands": [
            {"command_name": "status", "full_alias": "git status", "desc": "查看当前工作区与暂存区状态", "example": "git status -sb"},
            {"command_name": "add", "full_alias": "git add", "desc": "将工作区修改添加至暂存区", "example": "git add ."},
            {"command_name": "commit", "full_alias": "git commit", "desc": "将暂存区内容持久化提交", "example": "git commit -m 'feat: update'"},
            {"command_name": "push", "full_alias": "git push", "desc": "推送本地提交至远程仓库", "example": "git push origin main"},
            {"command_name": "pull", "full_alias": "git pull", "desc": "拉取最新改动并自动合并", "example": "git pull --rebase"},
        ],
    }
    with open(manifests_dir / "git.json", "w", encoding="utf-8") as f:
        json.dump(default_git, f, indent=2, ensure_ascii=False)

    default_pwsh = [
        {"source_alias": "rm -rf", "target_shell": "pwsh", "target_template": "Remove-Item -Recurse -Force {{args}}", "desc": "递归强制删除目录或文件"},
        {"source_alias": "rm", "target_shell": "pwsh", "target_template": "Remove-Item {{args}}", "desc": "安全删除文件或目录"},
        {"source_alias": "ls -la", "target_shell": "pwsh", "target_template": "Get-ChildItem -Force {{args}}", "desc": "详细列出所有文件（含隐藏文件）"},
        {"source_alias": "ll", "target_shell": "pwsh", "target_template": "Get-ChildItem -Force {{args}}", "desc": "详细列表显示文件"},
        {"source_alias": "ls", "target_shell": "pwsh", "target_template": "Get-ChildItem {{args}}", "desc": "列出当前工作目录内容"},
        {"source_alias": "cat", "target_shell": "pwsh", "target_template": "Get-Content {{args}}", "desc": "查看或连接输出文件内容"},
        {"source_alias": "touch", "target_shell": "pwsh", "target_template": "New-Item -ItemType File -Force {{args}}", "desc": "创建空文件或更新时间戳"},
        {"source_alias": "cp -r", "target_shell": "pwsh", "target_template": "Copy-Item -Recurse -Force {{args}}", "desc": "递归复制目录或文件"},
        {"source_alias": "clear", "target_shell": "pwsh", "target_template": "Clear-Host", "desc": "清除当前终端屏幕"},
    ]
    with open(mappings_dir / "pwsh.json", "w", encoding="utf-8") as f:
        json.dump(default_pwsh, f, indent=2, ensure_ascii=False)


def load_all_manifests() -> List[Dict[str, Any]]:
    """Loads all software manifests (*.json) from registry/manifests/."""
    ensure_registry_populated()
    packages = []
    for f in sorted(get_manifests_dir().glob("*.json")):
        try:
            with open(f, "r", encoding="utf-8") as fp:
                data = json.load(fp)
                if isinstance(data, dict):
                    packages.append(data)
        except Exception as e:
            logger.error(f"Failed to load manifest {f}: {e}")
    return packages


def load_all_mappings(shell: str = "pwsh") -> List[Dict[str, Any]]:
    """Loads all shell mappings from registry/mappings/."""
    ensure_registry_populated()
    mappings = []
    mapping_file = get_mappings_dir() / f"{shell}.json"
    if mapping_file.exists():
        try:
            with open(mapping_file, "r", encoding="utf-8") as fp:
                data = json.load(fp)
                if isinstance(data, list):
                    mappings.extend(data)
        except Exception as e:
            logger.error(f"Failed to load mapping {mapping_file}: {e}")
    return mappings


def save_manifest(pkg: Dict[str, Any]) -> Path:
    """Saves a software package manifest into registry/manifests/<software>.json."""
    ensure_registry_populated()
    software = pkg.get("software", "").lower()
    path = get_manifests_dir() / f"{software}.json"
    with open(path, "w", encoding="utf-8") as fp:
        json.dump(pkg, fp, indent=2, ensure_ascii=False)
    return path
