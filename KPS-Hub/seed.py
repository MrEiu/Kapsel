"""
KPS-Hub Initial Seed Data.
Seeds the server-side database with baseline packages, commands, and pwsh mappings.
"""

from datetime import datetime
from typing import Any, Dict, List

from db import HubRepository

PACKAGES_SEED: List[Dict[str, Any]] = [
    {
        "platform": "windows",
        "software": "scoop",
        "display_name": "Scoop (Windows 现代化命令行包管理器)",
        "version": "0.3.1",
        "desc": "Windows 开发者最爱的高雅、无污染、用户目录级命令行包管理器",
        "category": "package_manager",
        "author": "Luke Sampson / Scoop Community",
        "tags": "scoop,windows,package-manager,dev-tools",
        "commands": [
            {"command_name": "install", "full_alias": "scoop install", "desc": "一键静默下载并安装指定软件", "usage": "scoop install <app>", "example": "scoop install git neovim"},
            {"command_name": "update", "full_alias": "scoop update", "desc": "更新 scoop 本体或指定已安装应用", "usage": "scoop update [*|app]", "example": "scoop update *"},
            {"command_name": "status", "full_alias": "scoop status", "desc": "检查已安装软件中是否有可用的版本升级", "usage": "scoop status", "example": "scoop status"},
            {"command_name": "search", "full_alias": "scoop search", "desc": "在官方与第三方 bucket 中模糊搜索软件包", "usage": "scoop search <query>", "example": "scoop search ripgrep"},
            {"command_name": "list", "full_alias": "scoop list", "desc": "展示当前系统通过 scoop 已安装的应用清单", "usage": "scoop list", "example": "scoop list"},
            {"command_name": "uninstall", "full_alias": "scoop uninstall", "desc": "干净移除指定软件包并清理软链接", "usage": "scoop uninstall <app>", "example": "scoop uninstall nodejs"},
            {"command_name": "bucket", "full_alias": "scoop bucket", "desc": "管理软件扩展源仓库 (Bucket)", "usage": "scoop bucket [add|rm|list]", "example": "scoop bucket add extras"},
            {"command_name": "cleanup", "full_alias": "scoop cleanup", "desc": "清理已过期的旧版本安装包缓存以释放磁盘", "usage": "scoop cleanup [*|app]", "example": "scoop cleanup *"},
            {"command_name": "info", "full_alias": "scoop info", "desc": "查看某个软件包的详细元信息、主页与依赖", "usage": "scoop info <app>", "example": "scoop info python"},
            {"command_name": "cache", "full_alias": "scoop cache", "desc": "查看或清空 scoop 的本地下载压缩包缓存", "usage": "scoop cache [show|rm *]", "example": "scoop cache rm *"},
        ],
    },
    {
        "platform": "universal",
        "software": "git",
        "display_name": "Git 分布式版本控制系统",
        "version": "2.44.0",
        "desc": "全球最流行的分布式代码版本管理与团队协同工具",
        "category": "vcs",
        "author": "Linus Torvalds / Software Freedom Conservancy",
        "tags": "git,vcs,source-control,collaboration",
        "commands": [
            {"command_name": "status", "full_alias": "git status", "desc": "查看当前工作区、暂存区与分支同步状态", "usage": "git status [-s]", "example": "git status -sb"},
            {"command_name": "add", "full_alias": "git add", "desc": "将工作区修改添加至暂存区", "usage": "git add <pathspec>", "example": "git add ."},
            {"command_name": "commit", "full_alias": "git commit", "desc": "将暂存区内容持久化提交到本地仓库", "usage": "git commit -m '<msg>'", "example": "git commit -m 'feat: add hub'"},
            {"command_name": "push", "full_alias": "git push", "desc": "推送本地提交至远程仓库分支", "usage": "git push [remote] [branch]", "example": "git push origin main"},
            {"command_name": "pull", "full_alias": "git pull", "desc": "从远程仓库抓取最新改动并自动合并", "usage": "git pull [--rebase]", "example": "git pull --rebase"},
            {"command_name": "checkout", "full_alias": "git checkout", "desc": "检出分支或恢复工作区目标文件", "usage": "git checkout <branch|file>", "example": "git checkout -b dev"},
            {"command_name": "branch", "full_alias": "git branch", "desc": "列出、创建、重命名或删除本地分支", "usage": "git branch [-a|-d <name>]", "example": "git branch -a"},
            {"command_name": "diff", "full_alias": "git diff", "desc": "比对工作区、暂存区或历史提交之间的改动", "usage": "git diff [commit]", "example": "git diff HEAD~1"},
            {"command_name": "log", "full_alias": "git log", "desc": "以时间线翻阅历史版本提交日志", "usage": "git log [--oneline -n <N>]", "example": "git log --oneline -n 5"},
            {"command_name": "clone", "full_alias": "git clone", "desc": "克隆指定远程版本库到本地新目录", "usage": "git clone <url> [dir]", "example": "git clone https://..."},
            {"command_name": "init", "full_alias": "git init", "desc": "在当前工作目录下初始化全新 Git 仓库", "usage": "git init [dir]", "example": "git init"},
            {"command_name": "stash", "full_alias": "git stash", "desc": "暂存未提交的工作区变更以便临时切换分支", "usage": "git stash [pop|list]", "example": "git stash pop"},
        ],
    },
    {
        "platform": "universal",
        "software": "python",
        "display_name": "Python 编程语言与生态运行环境",
        "version": "3.13.0",
        "desc": "现代化高效率通用脚本、后端与人工智能标准语言生态",
        "category": "runtime",
        "author": "Python Software Foundation",
        "tags": "python,pip,venv,runtime,ai",
        "commands": [
            {"command_name": "venv", "full_alias": "python -m venv", "desc": "在指定路径创建轻量隔离的 Python 虚拟环境", "usage": "python -m venv <dir>", "example": "python -m venv .venv"},
            {"command_name": "pip-install", "full_alias": "pip install", "desc": "从 PyPI 安装第三方模块包或本地工程", "usage": "pip install <package>", "example": "pip install fastapi uvicorn"},
            {"command_name": "pip-freeze", "full_alias": "pip freeze", "desc": "导出当前环境中已安装模块清单至 requirements.txt", "usage": "pip freeze > requirements.txt", "example": "pip freeze > requirements.txt"},
            {"command_name": "http-server", "full_alias": "python -m http.server", "desc": "在当前目录下快速启动轻量静态 HTTP 文件服务器", "usage": "python -m http.server [port]", "example": "python -m http.server 8080"},
            {"command_name": "run", "full_alias": "python", "desc": "直接执行 Python 脚本文件", "usage": "python <script.py>", "example": "python main.py"},
            {"command_name": "pip-list", "full_alias": "pip list", "desc": "格式化展示当前环境安装的所有第三方库与版本", "usage": "pip list", "example": "pip list"},
            {"command_name": "pip-show", "full_alias": "pip show", "desc": "查看某个已安装库的详细元信息、安装路径与依赖", "usage": "pip show <package>", "example": "pip show rich"},
        ],
    },
    {
        "platform": "universal",
        "software": "npm",
        "display_name": "NPM (Node Package Manager)",
        "version": "10.5.0",
        "desc": "前端与全栈 JavaScript / TypeScript 生态标准包依赖管理与执行引擎",
        "category": "package_manager",
        "author": "GitHub / npm, Inc.",
        "tags": "npm,node,javascript,typescript,web",
        "commands": [
            {"command_name": "install", "full_alias": "npm install", "desc": "根据 package.json 自动安装所有依赖", "usage": "npm install [pkg]", "example": "npm install"},
            {"command_name": "run", "full_alias": "npm run", "desc": "运行 package.json 中配置的 script 脚本", "usage": "npm run <script>", "example": "npm run build"},
            {"command_name": "dev", "full_alias": "npm run dev", "desc": "启动前端本地热重载开发调试服务", "usage": "npm run dev", "example": "npm run dev"},
            {"command_name": "build", "full_alias": "npm run build", "desc": "执行生产环境编译、打包与静态资源压缩", "usage": "npm run build", "example": "npm run build"},
            {"command_name": "test", "full_alias": "npm test", "desc": "执行项目自动化单元测试用例", "usage": "npm test", "example": "npm test"},
            {"command_name": "init", "full_alias": "npm init", "desc": "引导式初始化创建崭新的 package.json 文件", "usage": "npm init [-y]", "example": "npm init -y"},
            {"command_name": "outdated", "full_alias": "npm outdated", "desc": "检查项目依赖包是否存在更新版本", "usage": "npm outdated", "example": "npm outdated"},
            {"command_name": "list", "full_alias": "npm list", "desc": "以树状结构展示已安装的依赖层次", "usage": "npm list [--depth=0]", "example": "npm list --depth=0"},
            {"command_name": "cache", "full_alias": "npm cache", "desc": "管理与清理 npm 本地下载缓存", "usage": "npm cache clean --force", "example": "npm cache clean --force"},
        ],
    },
    {
        "platform": "universal",
        "software": "docker",
        "display_name": "Docker 容器化应用运行时与引擎",
        "version": "26.0.0",
        "desc": "现代化轻量级容器生命周期管理与编排工具",
        "category": "container",
        "author": "Docker Inc.",
        "tags": "docker,container,devops,runtime",
        "commands": [
            {"command_name": "ps", "full_alias": "docker ps", "desc": "列出当前正在运行的容器实例", "usage": "docker ps [-a]", "example": "docker ps -a"},
            {"command_name": "run", "full_alias": "docker run", "desc": "创建并在全新隔离容器中启动运行镜像", "usage": "docker run [opts] <image>", "example": "docker run -d -p 80:80 nginx"},
            {"command_name": "build", "full_alias": "docker build", "desc": "根据 Dockerfile 构建容器镜像", "usage": "docker build -t <name> .", "example": "docker build -t myapp ."},
            {"command_name": "exec", "full_alias": "docker exec", "desc": "进入并在运行中的容器内部执行命令", "usage": "docker exec -it <id> <sh>", "example": "docker exec -it web bash"},
            {"command_name": "stop", "full_alias": "docker stop", "desc": "平稳停止一个或多个运行中的容器", "usage": "docker stop <id...>", "example": "docker stop myapp"},
            {"command_name": "start", "full_alias": "docker start", "desc": "启动一个或多个已停止的容器", "usage": "docker start <id...>", "example": "docker start myapp"},
            {"command_name": "images", "full_alias": "docker images", "desc": "查看本地已缓存或构建的镜像列表", "usage": "docker images", "example": "docker images"},
            {"command_name": "logs", "full_alias": "docker logs", "desc": "实时查看并跟踪容器的标准输出日志", "usage": "docker logs -f <id>", "example": "docker logs -f web"},
            {"command_name": "compose", "full_alias": "docker compose", "desc": "多容器编排定义与自动化部署工具", "usage": "docker compose [up|down]", "example": "docker compose up -d"},
        ],
    },
]

PWSH_MAPPINGS_SEED: List[Dict[str, Any]] = [
    {"source_alias": "rm -rf", "target_shell": "pwsh", "target_template": "Remove-Item -Recurse -Force {{args}}", "desc": "递归强制删除目录或文件"},
    {"source_alias": "rm", "target_shell": "pwsh", "target_template": "Remove-Item {{args}}", "desc": "安全删除文件或目录"},
    {"source_alias": "ls -la", "target_shell": "pwsh", "target_template": "Get-ChildItem -Force {{args}}", "desc": "详细列出所有文件（含隐藏文件）"},
    {"source_alias": "ll", "target_shell": "pwsh", "target_template": "Get-ChildItem -Force {{args}}", "desc": "详细列表显示文件"},
    {"source_alias": "ls", "target_shell": "pwsh", "target_template": "Get-ChildItem {{args}}", "desc": "列出当前工作目录内容"},
    {"source_alias": "cat", "target_shell": "pwsh", "target_template": "Get-Content {{args}}", "desc": "查看或连接输出文件内容"},
    {"source_alias": "touch", "target_shell": "pwsh", "target_template": "New-Item -ItemType File -Force {{args}}", "desc": "创建空文件或更新时间戳"},
    {"source_alias": "cp -r", "target_shell": "pwsh", "target_template": "Copy-Item -Recurse -Force {{args}}", "desc": "递归复制目录或文件"},
    {"source_alias": "cp", "target_shell": "pwsh", "target_template": "Copy-Item {{args}}", "desc": "复制文件到目标路径"},
    {"source_alias": "mv", "target_shell": "pwsh", "target_template": "Move-Item -Force {{args}}", "desc": "移动或重命名文件/目录"},
    {"source_alias": "mkdir -p", "target_shell": "pwsh", "target_template": "New-Item -ItemType Directory -Force {{args}}", "desc": "递归创建多级目录"},
    {"source_alias": "mkdir", "target_shell": "pwsh", "target_template": "New-Item -ItemType Directory {{args}}", "desc": "创建新目录"},
    {"source_alias": "ps", "target_shell": "pwsh", "target_template": "Get-Process {{args}}", "desc": "查看当前正在运行的进程列表"},
    {"source_alias": "kill -9", "target_shell": "pwsh", "target_template": "Stop-Process -Force -Id {{args}}", "desc": "按 PID 强制终止指定进程"},
    {"source_alias": "kill", "target_shell": "pwsh", "target_template": "Stop-Process -Id {{args}}", "desc": "终止指定进程"},
    {"source_alias": "grep", "target_shell": "pwsh", "target_template": "Select-String {{args}}", "desc": "正则模式与文本关键字过滤匹配"},
    {"source_alias": "find", "target_shell": "pwsh", "target_template": "Get-ChildItem -Recurse -Filter {{args}}", "desc": "在目录树中递归搜索文件"},
    {"source_alias": "which", "target_shell": "pwsh", "target_template": "Get-Command {{args}}", "desc": "查找可执行程序或别名的绝对路径"},
    {"source_alias": "df -h", "target_shell": "pwsh", "target_template": "Get-PSDrive -PSProvider FileSystem", "desc": "查看所有驱动器磁盘使用空间"},
    {"source_alias": "free -m", "target_shell": "pwsh", "target_template": "Get-CimInstance Win32_OperatingSystem | Select-Object @{N='TotalMemoryMB';E={[math]::Round($_.TotalVisibleMemorySize/1024)}},@{N='FreeMemoryMB';E={[math]::Round($_.FreePhysicalMemory/1024)}}", "desc": "查看系统物理内存与空闲容量"},
    {"source_alias": "clear", "target_shell": "pwsh", "target_template": "Clear-Host", "desc": "清除当前终端屏幕"},
    {"source_alias": "env", "target_shell": "pwsh", "target_template": "Get-ChildItem env:", "desc": "查看当前会话环境变量列表"},
    {"source_alias": "head", "target_shell": "pwsh", "target_template": "Get-Content -Head {{args}}", "desc": "查看文件前 N 行内容"},
    {"source_alias": "tail", "target_shell": "pwsh", "target_template": "Get-Content -Tail {{args}}", "desc": "查看文件末尾 N 行内容"},
    {"source_alias": "uname -a", "target_shell": "pwsh", "target_template": "Get-CimInstance Win32_OperatingSystem | Select-Object Caption, Version, OSArchitecture", "desc": "查看操作系统版本与架构详情"},
    {"source_alias": "ifconfig", "target_shell": "pwsh", "target_template": "Get-NetIPAddress -AddressFamily IPv4 | Format-Table InterfaceAlias, IPAddress", "desc": "查看本地网卡与 IPv4 地址配置"},
    {"source_alias": "ip a", "target_shell": "pwsh", "target_template": "Get-NetIPAddress | Format-Table InterfaceAlias, IPAddress", "desc": "查看所有网络接口 IP 地址"},
    {"source_alias": "open", "target_shell": "pwsh", "target_template": "Invoke-Item {{args}}", "desc": "使用系统默认程序打开文件或目录"},
    {"source_alias": "pwd", "target_shell": "pwsh", "target_template": "Get-Location", "desc": "输出当前工作目录绝对路径"},
    {"source_alias": "tar -czvf", "target_shell": "pwsh", "target_template": "tar.exe -czvf {{args}}", "desc": "打包并用 gzip 压缩指定目录或文件"},
    {"source_alias": "tar -xzvf", "target_shell": "pwsh", "target_template": "tar.exe -xzvf {{args}}", "desc": "解压 tar.gz 压缩包"},
    {"source_alias": "curl -O", "target_shell": "pwsh", "target_template": "curl.exe -O {{args}}", "desc": "下载远程文件至当前本地路径"},
]


def seed_database(repo: HubRepository) -> None:
    """Populates packages, software commands, and pwsh mappings."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with repo._get_connection() as conn:
        cur = conn.cursor()

        for pkg_data in PACKAGES_SEED:
            cur.execute(
                """
                INSERT INTO hub_packages (platform, software, display_name, version, desc, category, author, tags, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(platform, software) DO UPDATE SET
                    display_name=excluded.display_name,
                    version=excluded.version,
                    desc=excluded.desc,
                    category=excluded.category,
                    author=excluded.author,
                    tags=excluded.tags,
                    updated_at=excluded.updated_at
                """,
                (
                    pkg_data["platform"],
                    pkg_data["software"],
                    pkg_data["display_name"],
                    pkg_data["version"],
                    pkg_data["desc"],
                    pkg_data["category"],
                    pkg_data["author"],
                    pkg_data["tags"],
                    now,
                ),
            )
            pkg_id = cur.lastrowid or 1

            for cmd in pkg_data.get("commands", []):
                cur.execute(
                    """
                    INSERT INTO hub_commands (package_id, platform, software, command_name, full_alias, desc, usage, example)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(platform, software, command_name) DO UPDATE SET
                        full_alias=excluded.full_alias,
                        desc=excluded.desc,
                        usage=excluded.usage,
                        example=excluded.example
                    """,
                    (
                        pkg_id,
                        pkg_data["platform"],
                        pkg_data["software"],
                        cmd["command_name"],
                        cmd["full_alias"],
                        cmd["desc"],
                        cmd.get("usage", ""),
                        cmd.get("example", ""),
                    ),
                )

        for mapping in PWSH_MAPPINGS_SEED:
            cur.execute(
                """
                INSERT INTO hub_mappings (source_alias, target_shell, target_template, flags_json, desc, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(source_alias, target_shell) DO UPDATE SET
                    target_template=excluded.target_template,
                    flags_json=excluded.flags_json,
                    desc=excluded.desc,
                    updated_at=excluded.updated_at
                """,
                (
                    mapping["source_alias"],
                    mapping["target_shell"],
                    mapping["target_template"],
                    mapping.get("flags_json", "{}"),
                    mapping["desc"],
                    now,
                ),
            )

        conn.commit()


if __name__ == "__main__":
    repo = HubRepository()
    seed_database(repo)
    print("KPS-Hub server database seeded successfully!")
