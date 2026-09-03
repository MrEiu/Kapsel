"""
Seed data generator for Kapsel Cloud Hub & Mapping Repository.
Populates Platform -> Software 2-layer command sets (git, scoop, python, npm, docker)
and the dedicated pwsh mapping repository.
"""

from datetime import datetime
import json
import sqlite3
from typing import Any, Dict, List

from kapsel.hub.db import HubRepository, get_hub_db_path

PACKAGES_SEED: List[Dict[str, Any]] = [
    {
        "platform": "universal",
        "software": "git",
        "display_name": "Git 分布式版本控制系统",
        "version": "2.44.0",
        "desc": "全球最流行的分布式代码版本控制系统与协作工具链",
        "category": "vcs",
        "author": "Linus Torvalds / Git Core Team",
        "tags": "git,vcs,version-control,code",
        "commands": [
            {"command_name": "status", "full_alias": "git status", "desc": "查看工作区与暂存区的修改状态", "usage": "git status [options]", "example": "git status -s"},
            {"command_name": "add", "full_alias": "git add", "desc": "将工作区修改内容添加至暂存区", "usage": "git add <pathspec>", "example": "git add ."},
            {"command_name": "commit", "full_alias": "git commit", "desc": "将暂存区内容提交到本地版本库", "usage": "git commit -m <msg>", "example": "git commit -m 'feat: add hub'"},
            {"command_name": "push", "full_alias": "git push", "desc": "推送本地分支最新提交到远程仓库", "usage": "git push [remote] [branch]", "example": "git push origin main"},
            {"command_name": "pull", "full_alias": "git pull", "desc": "从远程仓库拉取最新变更并合并", "usage": "git pull [remote] [branch]", "example": "git pull origin main"},
            {"command_name": "branch", "full_alias": "git branch", "desc": "列出、创建或删除本地及远程分支", "usage": "git branch [-a | -d <branch>]", "example": "git branch -a"},
            {"command_name": "checkout", "full_alias": "git checkout", "desc": "切换分支或检出工作区文件内容", "usage": "git checkout <branch|file>", "example": "git checkout dev"},
            {"command_name": "diff", "full_alias": "git diff", "desc": "比对工作区、暂存区或提交之间的差异", "usage": "git diff [target]", "example": "git diff HEAD~1"},
            {"command_name": "log", "full_alias": "git log", "desc": "查看版本提交历史日志记录", "usage": "git log [--oneline -n <N>]", "example": "git log --oneline -n 5"},
            {"command_name": "clone", "full_alias": "git clone", "desc": "克隆远程仓库至本地全新目录", "usage": "git clone <url>", "example": "git clone https://github.com/owner/repo.git"},
            {"command_name": "init", "full_alias": "git init", "desc": "在当前工作目录初始化空 Git 仓库", "usage": "git init", "example": "git init"},
            {"command_name": "stash", "full_alias": "git stash", "desc": "临时储存当前未提交的工作区改动", "usage": "git stash [pop | list | drop]", "example": "git stash pop"},
        ],
    },
    {
        "platform": "windows",
        "software": "scoop",
        "display_name": "Scoop (Windows 现代化命令行包管理器)",
        "version": "0.3.1",
        "desc": "Windows 开发者最爱的高雅、无侵入命令行应用包管理器",
        "category": "package_manager",
        "author": "Luke Sampson / Scoop Community",
        "tags": "scoop,windows,package-manager,tools",
        "commands": [
            {"command_name": "install", "full_alias": "scoop install", "desc": "一键静默下载并安装指定软件", "usage": "scoop install <app>", "example": "scoop install git neovim"},
            {"command_name": "update", "full_alias": "scoop update", "desc": "更新 scoop 本体或指定已安装应用", "usage": "scoop update [* | <app>]", "example": "scoop update *"},
            {"command_name": "status", "full_alias": "scoop status", "desc": "检查已安装软件中是否有可用的更新版本", "usage": "scoop status", "example": "scoop status"},
            {"command_name": "search", "full_alias": "scoop search", "desc": "在官方与第三方 bucket 中模糊搜索软件包", "usage": "scoop search <query>", "example": "scoop search ripgrep"},
            {"command_name": "list", "full_alias": "scoop list", "desc": "展示当前系统通过 scoop 已安装的应用清单", "usage": "scoop list", "example": "scoop list"},
            {"command_name": "uninstall", "full_alias": "scoop uninstall", "desc": "干净移除指定软件包并清理软链接", "usage": "scoop uninstall <app>", "example": "scoop uninstall nodejs"},
            {"command_name": "bucket", "full_alias": "scoop bucket", "desc": "管理软件扩展源仓库 (Bucket)", "usage": "scoop bucket <add|rm|list>", "example": "scoop bucket add extras"},
            {"command_name": "cleanup", "full_alias": "scoop cleanup", "desc": "清理已过期的旧版本安装包缓存释放磁盘", "usage": "scoop cleanup [* | <app>]", "example": "scoop cleanup *"},
            {"command_name": "info", "full_alias": "scoop info", "desc": "查看某个软件包的详细元信息、主页与依赖", "usage": "scoop info <app>", "example": "scoop info python"},
            {"command_name": "cache", "full_alias": "scoop cache", "desc": "查看或清空 scoop 的本地下载压缩包缓存", "usage": "scoop cache [rm <app> | show]", "example": "scoop cache rm *"},
        ],
    },
    {
        "platform": "universal",
        "software": "python",
        "display_name": "Python 编程语言与生态工具链",
        "version": "3.13.0",
        "desc": "现代化高生产力通用脚本与应用开发语言运行环境",
        "category": "runtime",
        "author": "Python Software Foundation",
        "tags": "python,pip,venv,runtime",
        "commands": [
            {"command_name": "venv", "full_alias": "python -m venv", "desc": "在指定路径创建轻量隔离的 Python 虚拟环境", "usage": "python -m venv <dir>", "example": "python -m venv .venv"},
            {"command_name": "pip-install", "full_alias": "pip install", "desc": "从 PyPI 安装第三方模块依赖包", "usage": "pip install <package>", "example": "pip install fastapi uvicorn"},
            {"command_name": "pip-freeze", "full_alias": "pip freeze", "desc": "导出当前环境安装的依赖版本清单", "usage": "pip freeze > requirements.txt", "example": "pip freeze"},
            {"command_name": "http-server", "full_alias": "python -m http.server", "desc": "快速启动当前目录的本地简易 HTTP 文件服务器", "usage": "python -m http.server [port]", "example": "python -m http.server 8000"},
            {"command_name": "run", "full_alias": "python", "desc": "执行指定 Python 脚本代码文件", "usage": "python <script.py>", "example": "python main.py"},
            {"command_name": "pip-list", "full_alias": "pip list", "desc": "查看当前虚拟环境已安装的所有第三方包", "usage": "pip list", "example": "pip list"},
            {"command_name": "pip-show", "full_alias": "pip show", "desc": "查看某个已安装第三方包的详细元信息", "usage": "pip show <package>", "example": "pip show rich"},
        ],
    },
    {
        "platform": "universal",
        "software": "npm",
        "display_name": "npm (Node.js 官方包管理器)",
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
    {
        "platform": "universal",
        "software": "cargo",
        "display_name": "Cargo (Rust 官方包管理器与构建工具)",
        "version": "1.77.0",
        "desc": "Rust 编程语言工程构建、依赖解析与测试管理工具",
        "category": "package_manager",
        "author": "Rust Language Team",
        "tags": "rust,cargo,build,package-manager",
        "commands": [
            {"command_name": "build", "full_alias": "cargo build", "desc": "编译当前 Rust 项目工程", "usage": "cargo build [--release]", "example": "cargo build --release"},
            {"command_name": "run", "full_alias": "cargo run", "desc": "编译并直接启动运行二进制可执行文件", "usage": "cargo run [-- args]", "example": "cargo run"},
            {"command_name": "check", "full_alias": "cargo check", "desc": "快速语法与类型静态检查（无需完全编译）", "usage": "cargo check", "example": "cargo check"},
            {"command_name": "test", "full_alias": "cargo test", "desc": "运行所有内置单元测试与集成测试用例", "usage": "cargo test", "example": "cargo test"},
            {"command_name": "update", "full_alias": "cargo update", "desc": "更新 Cargo.lock 中解析的依赖包版本", "usage": "cargo update", "example": "cargo update"},
            {"command_name": "clean", "full_alias": "cargo clean", "desc": "清理 target 目录生成的编译构建缓存", "usage": "cargo clean", "example": "cargo clean"},
        ],
    },
    {
        "platform": "universal",
        "software": "repo",
        "display_name": "Kapsel 指令云仓库 (Hub Repository)",
        "version": "1.0.0",
        "desc": "Kapsel 指令云仓库查询、下载与安装工具",
        "category": "system",
        "author": "Kapsel Team",
        "tags": "hub,repo,commands,cloud",
        "commands": [
            {"command_name": "list", "full_alias": "kps repo list", "desc": "列出云仓库中收录的平台与软件指令集清单", "usage": "kps repo list [platform]", "example": "kps repo list windows"},
            {"command_name": "search", "full_alias": "kps repo search", "desc": "在指令云仓库中跨平台全局模糊搜索", "usage": "kps repo search <query>", "example": "kps repo search scoop"},
            {"command_name": "info", "full_alias": "kps repo info", "desc": "查看指定软件（如 scoop, git, python）的指令明细", "usage": "kps repo info <software>", "example": "kps repo info scoop"},
            {"command_name": "pull", "full_alias": "kps repo pull", "desc": "像 pip install 一样拉取云端指令集安装到本地", "usage": "kps repo pull <software>", "example": "kps repo pull scoop"},
            {"command_name": "mappings", "full_alias": "kps repo mappings", "desc": "查看独立收录的面向 pwsh 的原生命令转义库", "usage": "kps repo mappings [shell]", "example": "kps repo mappings pwsh"},
            {"command_name": "admin", "full_alias": "kps repo admin", "desc": "启动独立云仓库 CRUD 运维管理工具", "usage": "kps repo admin [status|pkg|cmd|map]", "example": "kps repo admin status"},
        ],
    },
    {
        "platform": "universal",
        "software": "hub",
        "display_name": "Kapsel 指令云仓库别名 (Hub Repository)",
        "version": "1.0.0",
        "desc": "Kapsel 指令云仓库查询与管理工具",
        "category": "system",
        "author": "Kapsel Team",
        "tags": "hub,repo,commands",
        "commands": [
            {"command_name": "list", "full_alias": "kps hub list", "desc": "列出云仓库中收录的平台与软件指令集清单", "usage": "kps hub list", "example": "kps hub list"},
            {"command_name": "search", "full_alias": "kps hub search", "desc": "在指令云仓库中跨平台全局模糊搜索", "usage": "kps hub search <query>", "example": "kps hub search git"},
            {"command_name": "info", "full_alias": "kps hub info", "desc": "查看指定软件的指令明细", "usage": "kps hub info <software>", "example": "kps hub info git"},
            {"command_name": "pull", "full_alias": "kps hub pull", "desc": "拉取云端指令集安装到本地", "usage": "kps hub pull <software>", "example": "kps hub pull git"},
            {"command_name": "mappings", "full_alias": "kps hub mappings", "desc": "查看原生命令转义库", "usage": "kps hub mappings", "example": "kps hub mappings"},
        ],
    },
]

# Dedicated PWSH Mapping Repository
PWSH_MAPPINGS_SEED: List[Dict[str, Any]] = [
    # Linux-First core filesystem & system mappings
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


def seed_hub_database(repo: HubRepository) -> None:
    """Populates packages, software commands, and pwsh mappings into SQLite."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with repo._get_connection() as conn:
        cursor = conn.cursor()

        # 1. Seed Packages & Commands
        for pkg_data in PACKAGES_SEED:
            cursor.execute(
                """
                INSERT INTO hub_packages (platform, software, display_name, version, desc, category, author, tags, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(platform, software) DO UPDATE SET
                    display_name=excluded.display_name,
                    version=excluded.version,
                    desc=excluded.desc,
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
            # Retrieve package_id
            cursor.execute("SELECT id FROM hub_packages WHERE platform = ? AND software = ?", (pkg_data["platform"], pkg_data["software"]))
            pkg_id = cursor.fetchone()[0]

            # Seed commands under package
            for cmd in pkg_data.get("commands", []):
                cursor.execute(
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

        # 2. Seed Dedicated PWSH Mappings
        for mapping in PWSH_MAPPINGS_SEED:
            cursor.execute(
                """
                INSERT INTO hub_mappings (source_alias, target_shell, target_template, desc, updated_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(source_alias, target_shell) DO UPDATE SET
                    target_template=excluded.target_template,
                    desc=excluded.desc,
                    updated_at=excluded.updated_at
                """,
                (
                    mapping["source_alias"],
                    mapping["target_shell"],
                    mapping["target_template"],
                    mapping["desc"],
                    now,
                ),
            )

        conn.commit()
