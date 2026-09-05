# 💊 Kapsel：跨平台自适应智能终端胶囊

<p align="center">
  <b>Wrap complexity, expose simplicity. 包裹复杂，暴露极简。</b><br>
  现代化 UI 体验的跨平台交互式终端增强包装器（CLI Wrapper）。
</p>

---

## 📝 产品理念 (Philosophy)

**Kapsel**（德语“胶囊”）是一款具有现代化 UI 体验的跨平台交互式终端包装器（CLI Wrapper）。

它的核心理念是**“包裹复杂，暴露极简”**。Kapsel 完全接管终端输入流，**不侵入任何操作系统原生配置**（无需修改 `.bashrc`、`config.fish` 或 PowerShell Profile）。它以 **Linux 原生命令** 为主导肌肉记忆，结合**双态智能引擎**，让开发者在 Windows、macOS 和 Linux 上都能享受高度一致、极致优雅的命令行体验。

---

## 📦 快速安装与启动 (Quick Start)

### 1. 安装 Kapsel-CLI

```bash
# 推荐全局隔离安装 (pipx)
pipx install kapsel-cli

# 或通过 pip 全局/用户安装
pip install --upgrade kapsel-cli
```

### 2. 启动交互式终端胶囊

```bash
kapsel
# 或使用快捷别名
kps
```

### 3. 开箱即用：1,000+ 命令自动补全引擎 (Carapace)

Kapsel 深度整合了 [Carapace](https://carapace.sh) 作为核心多 Shell 深度上下文自动补全引擎（原生支持 `git`, `docker`, `kubectl`, `cargo`, `npm`, `pnpm`, `python` 等 1000+ 原生命令的分支、标签、容器名与选项补全）：

- **首次启动全自动无感就绪（零操作、免 root）**：
  首次输入 `kapsel` 启动终端时，系统将**自动检测并静默拉取**匹配当前系统架构的官方二进制到 `~/.kapsel/bin/`，完全不需要手动执行任何命令，开箱即用！
- **手动诊断或修复**：
  若在离线环境下使用或需要手动重新下载，可随时运行维护指令：
  ```bash
  kapsel setup-completion [--force]
  ```
- **备用一键安装脚本**：
  - Linux / macOS 服务器脚本：`curl -fsSL https://raw.githubusercontent.com/MrEiu/Kapsel/master/scripts/install_carapace.sh | bash`
  - Windows PowerShell 脚本：`irm https://raw.githubusercontent.com/MrEiu/Kapsel/master/scripts/install_carapace.ps1 | iex`

---

## 🚀 核心特性

### 1. 核心交互：双态智能引擎 (Dual-State Engine)

在同一个输入框内实现无缝、克制的双态切换：

- **默认态：安静的终端增强器 (Native Mode)**
  - **原生无感透传**：原汁原味地执行当前系统的原生命令（如 `git push`, `npm run dev`, `vim`, `python`），绝不拦截，完美兼容交互式程序与标准输入输出。
  - **历史智能预测 (Autosuggestion)**：基于独立的本地历史数据库，在光标后方以暗灰色文本实时预测命令，按 **`→` (右方向键)** 一键采纳。
  - **原生路径补全**：输入 `cd ` 并按下 **Tab**，自动读取当前操作系统的真实目录和文件进行智能补全。

- **映射态：跨平台翻译胶囊 (Kapsel Mode)**
  - **动态无缝切入**：输入 `kps ` 加空格瞬间进入“胶囊模式”，补全数据源即刻切换为跨平台指令集。
  - **Linux-First 肌肉记忆**：完全采用熟悉的 Linux 基础命令作为触发词（如 `kps rm -rf`, `kps ls -la`, `kps ps`, `kps grep`）。
  - **富文本感知菜单**：下拉菜单展示匹配的 Linux 映射指令，附带高亮中文说明，并在右侧实时预览即将执行的底层真实代码。
  - **剥离与派发**：按下回车后，Kapsel 自动剥离 `kps ` 前缀，提取核心参数，将其翻译为当前终端的最佳原生指令并执行。

### 2. 终端级精细化路由与降级 (Terminal-Level Routing)

Kapsel 实现了比“操作系统级”更硬核的终端（Shell）级精细化路由与降级回退机制：

- **环境深度嗅探**：启动时精准识别外层宿主是 `pwsh`, `powershell`, `cmd`, `bash`, `zsh` 还是 `fish`。
- **多级降级匹配**：例如指令 `kps ls -la`：
  - 检测到 `zsh`：优先执行美化版指令 `eza -la --icons`
  - 检测到 `powershell` / `pwsh`：执行 `Get-ChildItem -Force`
  - 检测到 `cmd`：执行 `dir /Q /A`
  - 通用 Unix 环境：执行 `ls -la`
- **智能参数注入 (`{{args}}`)**：输入 `kps rm -rf node_modules` 时，Kapsel 自动提取参数并无缝注入到 YAML 配置的占位符中（如 `Remove-Item -Recurse -Force node_modules`）。

### 3. 独立沙箱化的用户状态 (Isolated State DB)

- **历史无缝漫游**：统一将历史输入写入外部的 SQLite 数据库 `~/.kapsel/history.db`。无论昨天在 Windows CMD 还是今天在 pwsh 中，都能随时调出完整的跨平台历史记录。
- **频次权重学习**：基于 SQLite 自动记录命令使用频次，高频映射指令在补全菜单中享有最高优先级排序。

### 4. 现代美学界面 (Aesthetic UI/UX)

- **区块化视觉封装**：采用现代符号连线（`╭─ ❯` 和 `╰─`），将“输入 -> 耗时执行 -> 输出结果”在终端里视觉化为一个独立、闭合的卡片区块。
- **优雅的状态反馈**：执行结束后自动返回鲜明的状态标识（绿色的 `✔ 0` 或标红的退出码 `✘ exit 1`）以及毫秒级执行耗时（`⏱ 42ms`）。
- **动态环境欢迎页**：启动时展示圆角边框面板，智能播报当前检测到的宿主终端、提权状态（Root / Admin / User）及配置文件加载情况。

---

## 📁 规范化数据沙箱设计

安装运行后，Kapsel 将在用户主目录自动生成标准化的数据目录：

```text
~/.kapsel/
├── config.yaml       # 系统级 UI 配置 (主题颜色、符号样式、动画开关等)
├── commands.yaml     # Linux-First 自适应映射指令集 (支持团队 Git 共享)
├── history.db        # 跨平台的独立用户历史输入与频次分析数据库 (SQLite)
└── logs/             # Kapsel 自身的运行报错与调试日志
```

### `commands.yaml` 配置示例

```yaml
commands:
  - alias: "rm -rf"
    desc: "递归强制删除目录或文件"
    mapping:
      powershell: "Remove-Item -Recurse -Force {{args}}"
      cmd: "rmdir /S /Q {{args}}"
      unix: "rm -rf {{args}}"

  - alias: "ls -la"
    desc: "详细列出所有文件（含隐藏文件）"
    mapping:
      zsh: "eza -la --icons {{args}}"
      powershell: "Get-ChildItem -Force {{args}}"
      cmd: "dir /Q /A {{args}}"
      unix: "ls -la {{args}}"
```

---

## 🛠️ 安装与快速开始

### 本地开发安装

```bash
git clone <repo-url> kapsel
cd kapsel
pip install -e .
```

### 使用方式

1. **交互式全屏胶囊模式 (`kapsel`)**：
   ```bash
   kapsel
   ```
   进入 Kapsel 交互终端，即可体验双态补全、现代卡片包装和历史漫游。
   - 输入 `help`：随时调出完整使用指南与指令速查手册。
   - 输入 `status` 或 `info`：查看当前宿主 Shell、运行权限、数据沙箱与系统详细状态面板。
   - 输入 `clear`：清除屏幕并重绘胶囊徽标。
   - 输入 `exit`：无痕退出胶囊。

2. **单次快速命令转换 (`kps`)**：
   ```bash
   kps rm -rf dist/
   kps ls -la
   kps ps
   kps help
   kps status
   ```
   直接在您现有的任意 Shell（PowerShell、CMD、Bash）中调用 `kps`，即刻转换并执行。

---

## 🛠️ 内置控制台指令

| 指令 | 别名 | 功能说明 |
| :--- | :--- | :--- |
| `help` | `kps help`, `--help` | 显示详尽的使用指南、交互机制与常用指令速查手册 |
| `status` | `info`, `kps status` | 查看当前宿主 Shell、运行权限、操作系统、数据沙箱与历史库统计 |
| `config` | `kps config` | 查看系统核心配置看板、快速调节灵敏度与功能开关 |
| `config path` | - | 打印配置文件 `~/.kapsel/config.yaml` 的完整绝对路径 |
| `config edit` | - | 调用系统关联编辑器直接打开并编辑 `config.yaml` |
| `config set <k> <v>` | - | 命令行快速修改某项配置（如 `config set sensitivity 0.2`） |
| `config reload` | - | 即刻热重载最新配置文件，无需重启终端 |
| `repo [subcmd]` | `kps repo`, `hub` | 📦 访问指令云仓库（支持 `list`, `search`, `info`, `pull`, `mappings`） |
| `register [user]` | `kps register` | 注册胶囊用户身份，生成专属设备指纹与加密云同步秘钥 |
| `whoami` | `user`, `kps whoami` | 查看当前设备登录的胶囊用户、绑定邮箱与云同步就绪状态 |
| `logout` | `kps logout` | 安全退出当前用户身份并清除本地凭证 |
| `cd` | - | 智能切换工作目录（支持 `cd ~` 家目录、`cd -` 快速返回、`cd ..` 上级目录） |
| `clear` | `cls` | 清屏并重新绘制极简胶囊徽标 |
| `exit` | `quit` | 安全退出 Kapsel，无痕返回当前原生 Shell |

---

## 📦 指令云仓库 (Hub Repository)：两层指令集与 PWSH 独立映射

为了让终端开发者能像使用 `pip`、`scoop` 或 `brew` 那样轻松获取、共享和安装各类命令行工具指令集，Kapsel 内置了基于 SQLite 的指令云仓库体系 (`kapsel/hub/registry.db`)：

```
                           ┌── hub_packages (平台 -> 软件元数据)
 Kapsel Hub (SQLite 仓库) ─┼── hub_commands (具体软件收录的丰富子命令集)
                           └── hub_mappings (独立终端转义映射仓库，优先聚焦 pwsh)
```

### 1. 两层架构：平台 (Platform) ➜ 软件 (Software)
- **第一层：平台环境**：如 `windows`、`universal`（跨平台通用）、`linux`。
- **第二层：软件工具链**：
  - 🧰 **`scoop`** (Windows 专属)：收录 `install`, `update`, `status`, `search`, `list`, `uninstall`, `bucket`, `cleanup`, `info`, `cache` 等常用指令与用例。
  - 🌿 **`git`** (通用)：收录 `status`, `add`, `commit`, `push`, `pull`, `checkout`, `branch`, `diff`, `log`, `clone`, `init`, `stash` 等。
  - 🐍 **`python`** (通用)：收录 `venv`, `pip-install`, `pip-freeze`, `http-server`, `run`, `pip-list`, `pip-show`。
  - 📦 **`npm`** (通用)：收录 `install`, `run`, `dev`, `build`, `test`, `init`, `outdated`, `list`, `cache`。

### 2. 独立映射仓库 (Focused on `pwsh`)
- 独立于软件具体业务指令，专门收录 Linux 原生命令到 **PowerShell Core / Windows PowerShell** 的精准 Cmdlet 映射模板（当前收录 32+ 条核心系统转义）。

### 3. 像 `pip` / `scoop` 一样使用云仓库指令
| 指令 | 作用描述 | 类似 pip/scoop 概念 |
| :--- | :--- | :--- |
| **`kps repo list`** | 按平台分类展示所有可用的软件包清单 | `pip list` / `scoop bucket list` |
| **`kps repo search <词>`** | 跨平台全局模糊搜索软件包、子命令或中文说明 | `pip search` / `scoop search` |
| **`kps repo info <软件名>`** | 审查该软件收录的所有指令明细、语法与示例（如 `kps repo info scoop`） | `pip show` / `scoop info` |
| **`kps repo pull <软件名>`** | **一键拉取并安装该软件指令集**至本地活跃 `commands.yaml` | **`pip install`** / **`scoop install`** |
| **`kps repo mappings`** | 查看独立收录的面向 pwsh 的原生命令转义库 | 查看底层原生适配表 |
| **`kps-hub`** / **`kps repo admin`** | **独立的云仓库 CRUD 运维管理工具**（增删改查软件包、指令、映射） | 仓库源管理员工具 |

#### 独立云仓库运维工具 (`kps-hub`) 快速用法：
```bash
# 查看云仓库统计与数据库状态
kps-hub status

# 管理软件包 (增删查)
kps-hub pkg list
kps-hub pkg add docker -d "Docker 容器引擎" --platform universal --category container
kps-hub pkg del docker

# 管理具体软件的指令集 (增删查)
kps-hub cmd list scoop
kps-hub cmd add scoop bucket "scoop bucket" -d "管理扩展 Bucket 源" --example "scoop bucket add extras"
kps-hub cmd del scoop bucket

# 管理独立 pwsh 原生映射库 (增删查)
kps-hub map list --shell pwsh
kps-hub map add "docker-ps" "docker.exe ps" -d "Docker 进程列表" --shell pwsh

# 整个仓库导出与导入
kps-hub export -o backup.json
kps-hub import backup.json
```

---

## ☁️ 胶囊用户身份与多端云漫游体系

为了在 Windows、macOS 和 Linux 之间实现**无缝的个人工作流漫游**，Kapsel 现已内置端到端加密的数字身份系统，为后续全量云端多系统同步提供基础支撑：

### 1. 凭据与设备指纹
- **存储路径**：`~/.kapsel/user.json`
- **安全体系**：每个设备在注册时，均会基于硬件环境生成独立的 `device_id`，并签发专属的跨端加密同步秘钥（`kps_sync_...`），无需侵入系统密钥环。
- **漫游就绪**：后续在任一台新设备（macOS / Linux / Windows）上通过您的秘钥接入，即可自动拉取并双向同步：
  - 📂 您的自定义 Linux-First 指令映射表 (`commands.yaml`)
  - ⚙️ 您量身定制的终端主题与交互灵敏度参数 (`config.yaml`)
  - 🧠 跨 Shell 的历史输入库与高频频次学习权重 (`history.db`)

### 2. 账号管理常用指令
```bash
# 1. 交互式或单行注册胶囊账号
kps register meru --email user@example.com

# 2. 查看当前登录用户信息与设备秘钥
kps whoami

# 3. 查看系统状态看板（联动显示当前用户）
kps status

# 4. 退出登录
kps logout
```

---

## ⚙️ 配置文件与右箭头灵敏交互

### 1. 配置文件位置
Kapsel 的所有个性化设置均集中在外部沙箱的 YAML 文件中：
- **物理路径**：`~/.kapsel/config.yaml`（在 Windows 上通常为 `C:\Users\<当前用户>\.kapsel\config.yaml`）
- 文件内部提供全中文详尽注释，涵盖：交互灵敏度、UI 主题调色板、提示行符号、终端路由降级规则及历史漫游深度。

### 2. 右箭头 (`→`) 灵敏交互设计：单按 vs 长按
为了解决传统终端“一次性填满整行无法部分复用”的痛点，Kapsel 引入了基于按键时间敏感度的多态采纳引擎：
- **单次轻按 (Tap)**：**逐词采纳 (Word-by-word)**。例如历史命令为 `git commit -m "update" -a`，按一下输入 `git`，再按一下输入 `commit`，方便开发者精确截取历史参数并微调。
- **长按 / 连按 (Hold)**：**一键整行采纳 (Full Accept)**。当连续击键或长按时，系统自动判定为连按意图，瞬间将剩余全部命令一键填满！
- **可配参数**：
  - `autosuggest_tap_mode`: 可设为 `"word"`（逐词，默认）或 `"full"`（单按直接整行）。
  - `autosuggest_sensitivity`: 长按/连按判定敏感度阈值（单位秒，默认 `0.25`）。两次按键时间间隔在此阈值内即判定为连续长按。
  - `consecutive_press_threshold`: 触发整行长按所需的连续击键次数（默认 `2` 次）。

#### 快速调参示例
```bash
# 查看当前所有重要配置
kps config

# 快速打开配置文件编辑
kps config edit
```

### 3. 数据存储目录自定义与无痕迁移 (`kps datadir`)
Kapsel 默认将配置文件、本地 SQLite 历史库与指令仓库保存在 `~/.kapsel`。若您希望将其存放在非系统盘（如 D盘）、外部挂载盘或同步盘中，可随时一键迁移：
- **查看当前存储状态**：
  ```bash
  kps datadir
  ```
- **迁移到自定义路径 (自动搬迁且旧目录不留)**：
  ```bash
  kps datadir D:\KapselData
  ```
  *系统会自动转移全部 SQLite 历史记录、`config.yaml` 配置文件和指令仓库，并在搬迁完毕后彻底清理旧目录，全局永久生效。*
- **一键恢复为系统默认路径**：
  ```bash
  kps datadir default
  ```

### 4. 上下方向键重构：以当前输入为原点的双向流转机制 (Origin-Centered Navigation)
为了让开发者的双手不离开方向键即可完成最核心的高频操作，Kapsel 创新性地设计了**以当前输入为原点**的上下流转交互：

```
                ▲ 向上漫游更早历史
                │
     ┌──────────────────────┐
     │ 历史模式 (History)   │ ── 按【↓】往回翻看较新历史，直到回到原点
     └──────────────────────┘
                ▲
    [按 ↑ 进入] │ [按 ↓ 回到原点]
 ───────────────┼───────────────────────────  (当前正在输入的命令行 · 原点)
    [按 ↑ 回到] │ [按 ↓ 进入]
                ▼
     ┌──────────────────────┐
     │ 补全模式 (Completion)│ ── 按【↑】往回选择上一个词条，直到回到原点
     └──────────────────────┘
                │
                ▼ 向下选择下一个候选词
```

- **从原点出发**：
  - **`↑` (上方向键)**：向上进入【历史漫游模式】，调出 SQLite 历史库中的上一条输入；
  - **`↓` (下方向键)**：向下进入【补全候选模式】，一键唤起并自动选中第一个补全词！
- **在模式内部可自由来回切换，回到原点才能进入下一个模式**：
  - **在历史模式中**：按 `↑` 查更早历史、按 `↓` 查较新历史；一路按 `↓` **回到原点**后，再次按 `↓` 即可无缝切换进入补全模式！
  - **在补全模式中**：按 `↓` 选下一个词条、按 `↑` 选上一个词条；一路按 `↑` **回到原点**（恢复原始输入）后，再次按 `↑` 即可无缝切换进入历史模式！
  - **选词采纳 vs 提交执行（Enter 回车键智能分流）**：
    - 当通过向下键选中了某个子命令或 Flag 时，按下 **`Enter`**（或 `Tab`）会**确认采纳该词条**，自动在末尾补全空格，光标停留在末尾——**绝对不会直接执行裸命令**，方便您立刻接着敲入后续参数（如 `-m "update"` 或目录名）！
    - 只有当没有选词时，按下 `Enter` 才会提交整行命令执行。
  - **绝对不是死板的“只能一味上一味下”**，双手不离方向键，自由丝滑来回穿梭！

---

## 📋 预置常用命令一览

| Linux 命令 | 功能说明 | PowerShell 映射 | CMD 映射 |
| :--- | :--- | :--- | :--- |
| `rm -rf` | 递归强制删除 | `Remove-Item -Recurse -Force` | `rmdir /S /Q` |
| `rm` | 删除文件 | `Remove-Item` | `del /Q` |
| `ls -la` / `ll` | 详细列出文件 | `Get-ChildItem -Force` | `dir /Q /A` |
| `cat` | 查看文件内容 | `Get-Content` | `type` |
| `touch` | 创建空文件 | `New-Item -ItemType File -Force` | `type nul >>` |
| `cp -r` | 递归复制 | `Copy-Item -Recurse -Force` | `xcopy /E /I /Y` |
| `mv` | 移动/重命名 | `Move-Item -Force` | `move /Y` |
| `mkdir -p` | 递归建目录 | `New-Item -ItemType Directory -Force` | `mkdir` |
| `ps` | 查看进程列表 | `Get-Process` | `tasklist` |
| `kill -9` | 强制终止进程 | `Stop-Process -Force -Id` | `taskkill /F /PID` |
| `grep` | 文本模式匹配 | `Select-String` | `findstr` |
| `find` | 递归查找文件 | `Get-ChildItem -Recurse -Filter` | `dir /S /B` |
| `which` | 查找程序路径 | `Get-Command` | `where` |
| `df -h` | 磁盘空间统计 | `Get-PSDrive -PSProvider FileSystem` | `wmic logicaldisk ...` |
| `clear` | 清屏 | `Clear-Host` | `cls` |
| `ifconfig` / `ip a` | 查看网卡信息 | `Get-NetIPAddress` | `ipconfig /all` |
| `env` | 环境变量列表 | `Get-ChildItem env:` | `set` |
| `head` | 查看前 10 行 | `Get-Content -Head 10` | `powershell ...` |
| `tail` | 查看后 10 行 | `Get-Content -Tail 10` | `powershell ...` |

---

## 🔮 未来规划 (Roadmap)

- **非侵入式交互看板 (Context Stream)**：
  - 在后续版本中，计划将交互底栏演进为可插拔关键信息看板：
    - **Git 状态流**：实时反映未暂存修改、未推送 Commit 计数
    - **环境上下文**：Python 虚拟环境 (`venv`/`conda`)、Node 运行时版本自动感知
    - **后台与性能监控**：耗时后台任务执行进度、系统资源告警
    - **AI 智能建议**：基于历史错误码的自适应修复提示
- **配置云漫游与团队共享**：支持通过用户数字凭据一键跨设备同步指令集与历史漫游。
- **自定义指令热重载**：在外部修改 `~/.kapsel/commands.yaml` 时无感知热重载。
- 📖 **深度技术白皮书**：详细架构与演进方案已整理至 [《Kapsel 指令存储与映射架构分析与全方位优化方案》](docs/command_storage_and_mapping_architecture.md)。
- 🛠️ **开发架构规范 (DEVELOPMENT.md)**：开发守则与核心铁律已写入 [《Kapsel 架构设计与开发规范》](DEVELOPMENT.md)（坚决杜绝代码硬编码，杜绝配置文件堆叠，坚持云仓库集中、客户端同步、本地高速读取）。
- 📡 **云端与本地通信架构提案**：详见 [《Kapsel 本地与云端通信方案调研与架构选型报告》](docs/local_cloud_communication_proposals.md)（深度对比 REST API、Git CDN、SQLite Changeset、gRPC 与混合架构五大方案）。

## 🙏 特别致谢 (Acknowledgments)

- **Carapace (`carapace-sh/carapace-bin`)**：
  为 Kapsel 提供了强大、现代化且深度支持 1,000+ 原生命令的动态上下文自动补全引擎支持。
- **Fig / Amazon Q (`withfig/autocomplete`)**：
  为 Kapsel 早期的补全架构设计与交互提供了宝贵的先驱灵感。

---

## 📄 License

MIT License.

