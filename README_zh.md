<div align="center">

# ⚡ Kapsel

**新一代跨平台智能终端胶囊与人机工程学命令多路复用器**

[![Python Version](https://img.shields.io/badge/Python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-3776AB.svg?style=flat-square&logo=python&logoColor=white)](https://pypi.org/project/kapsel-cli/)
[![Platform Support](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-4D4D4D.svg?style=flat-square&logo=linux&logoColor=white)](https://github.com/MrEiu/Kapsel)
[![License](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](LICENSE)

<p align="center">
  <i>"封装复杂度，暴露纯粹度。"</i><br>
  零环境污染、上下文感知的命令抽象层与极速交互胶囊终端环境。<br>
  为 Windows PowerShell、macOS Zsh 与 Linux Bash 带来统一、丝滑的现代化开发者终端体验。
</p>

---

[核心亮点](#-核心亮点) •
[快速安装](#-快速安装) •
[系统架构](#-设计哲学与架构) •
[官方插件生态](#-官方插件生态) •
[特性对比](#-功能特性矩阵对比) •
[命令手册](#-常用命令速查手册) •
[English Documentation](README.md)

---

</div>

```text
╭─ kapsel [pwsh] ~/Projects/Kapsel 14:32:05
╰─ ❯ git checkout -b feature/dynamic-specs
✔ 0  git checkout -b feature/dynamic-specs  ⏱ 24ms
```

---

## 🌟 为什么选择 Kapsel？

开发者每天在不同操作系统与终端之间来回切换，常面临以下痛点：
- **肌肉记忆碰撞**：Linux 与 Windows 命令不一致（`rm -rf` 对比 `Remove-Item`，`cat` 对比 `type`，`ls -la` 对比 `dir /a`）；
- **环境污染严重**：各种工具将配置强行注入全局 `.bashrc`、`config.fish` 或 `$PROFILE`，卸载困难且相互干扰；
- **补全碎片化**：不同 Shell 的自动补全体验割裂，复杂子命令参数缺少提示。

**Kapsel** 通过引入**非侵入式沙盒终端胶囊**彻底化解这些问题：它作为透明增强层拦截并提速命令行交互，**对宿主系统全局配置零污染**——提供亚毫秒级异步自动补全、Linux-First 跨平台映射以及全自动环境隔离。

---

## 🚀 核心亮点

### 1. 双态执行多路复用器 (Dual-State Execution)
- **原生透传模式 (默认)**：
  对所有系统可执行程序（`git`、`docker`、`npm`、`cargo`、`python`、`vim` 等）零开销直通，保留 100% 完整 TTY 交互、实时信号响应与标准流管道。
- **统一胶囊管道 (`kps <cmd>` / `kapsel <cmd>`)**：
  跨平台通用命令与插件工具的统一入口，在后台自动完成多端命令翻译与宿主参数优化。
- **异步历史预测 (Deep Autosuggestions)**：
  静默式行内历史灰色预测，由独立的 SQLite 统计引擎（`~/.kapsel/history.db`）强力驱动。按下 `→`（右箭头）或 `Tab` 键即可瞬间采纳补全。

### 2. 多 Shell 动态智能自动补全 (基于 Carapace)
- **1,000+ 命令上下文覆盖**：
  深度集成 [Carapace](https://carapace.sh)，支持多层级参数与上下文实时联想（Git 分支与标签、Docker 容器与镜像、Kubectl Pod、NPM 脚本）。
- **零权限极速就位**：
  首次启动时静默引导平台预编译二进制到 `~/.kapsel/bin/`，**无需任何管理员/root 权限**。

### 3. 双根规约聚合与宿主防冲突哨兵 (Collision Sentinel)
- **双根规约隔离树 (`kps.yaml` 与 `kapsel.yaml`)**：
  将所有内建工具与插件规约编译收敛在 `kps` 和 `kapsel` 两个安全命名空间下。
- **宿主系统命令防劫持**：
  对于 `alias`、`help`、`install`、`history`、`profile`、`ps`、`kill` 等高危冲突词，严格限制在 `kps` 作用域内——**100% 保证宿主 Shell 原生命令（如 PowerShell 的 `Get-Alias`、Linux 的 `alias`）不被意外覆盖**。
- **深度参数补全**：
  输入 `kps alias add <Tab>` 即可享受 `--from`、`--to`、`--shell`、`--global` 等完整多级参数联想。

### 4. 模块化防崩溃插件子系统
- **解耦式架构**：各插件在独立内存边界运行，即使某个插件报错也绝不会导致 Kapsel 核心崩溃。
- **标准声明式规约**：每个插件遵循统一的 YAML 规约定义，支持通过 `kapsel enable` / `disable` 热插拔启用或停用。

### 5. 现代极简卡片式终端美学 (Boxed Aesthetics)
- **卡片式框线**：清晰区分每次命令的输入与输出上下文（`╭─ ❯` 与 `╰─`）。
- **实时遥测反馈**：毫秒级展示执行退出码（`✔ 0` 或 `✘ exit 1`）以及精准耗时（`⏱ 38ms`）。
- **原生多语言引擎 (i18n)**：全量内置 7 种语言（中文 `zh_CN`、英语 `en`、日语 `ja`、西班牙语 `es`、法语 `fr`、德语 `de`、俄语 `ru`）。

---

## ⚡ 快速安装

请根据您的网络环境与系统选择最便捷的安装途径：

- [🇨🇳 中国大陆极速通道 (镜像源加速 - 推荐)](#1-中国大陆极速通道-china-fast-track)
- [📦 主流包管理器安装 (PyPI / Scoop / Homebrew / APT)](#2-主流包管理器安装)
- [💾 预编译免环境单文件绿色版 (GitHub Releases)](#3-预编译免环境绿色版-独立运行)
- [🌐 国际版全套工具链自动脚本](#4-国际版全套工具链自动安装脚本)
- [🛠️ 源码构建与本地调试](#5-源码构建与开发者模式)

> 📖 **更多安装细节与常见问题诊断**：请参阅 [docs/INSTALLATION.md](docs/INSTALLATION.md)。

---

### 1. 🇨🇳 中国大陆极速通道 (China Fast-Track)

专为中国大陆网络环境深度定制，自动通过国内高速镜像代理（ghproxy / 清华大学 TUNA 镜像站）拉取资源，无需科学上网。

#### 方式一：下载本地脚本后执行安装（⭐ 强烈推荐，最稳健，规避网络波动与策略限制）

**Windows (PowerShell):**
```powershell
# 1. 使用国内镜像加速下载 CN 安装脚本
Invoke-WebRequest -Uri "https://ghproxy.net/https://raw.githubusercontent.com/MrEiu/Kapsel/master/scripts/install_cn.ps1" -OutFile "install_cn.ps1"

# 2. 授权当前会话执行脚本并运行安装
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned -Force
.\install_cn.ps1
```

**Linux & macOS (Bash):**
```bash
# 1. 使用国内镜像加速下载 CN 安装脚本
curl -fsSL "https://ghproxy.net/https://raw.githubusercontent.com/MrEiu/Kapsel/master/scripts/install_cn.sh" -o install_cn.sh

# 2. 运行脚本完成全自动部署
bash install_cn.sh
```

#### 方式二：国内镜像一行流快速执行 (管道执行)

```powershell
# Windows (PowerShell):
irm https://ghproxy.net/https://raw.githubusercontent.com/MrEiu/Kapsel/master/scripts/install_cn.ps1 | iex
```

```bash
# Linux / macOS (Bash):
curl -fsSL https://ghproxy.net/https://raw.githubusercontent.com/MrEiu/Kapsel/master/scripts/install_cn.sh | bash
```

#### 方式三：使用清华大学 PyPI 国内镜像在线安装

```bash
pip install --upgrade kapsel-cli -i https://pypi.tuna.tsinghua.edu.cn/simple
```

---

### 2. 📦 主流包管理器安装

#### PyPI (Python 3.9+)

```bash
# 推荐：使用 pipx 进行沙盒隔离安装（避免污染系统全局 Python）
pipx install kapsel-cli

# 或通过标准 pip 安装
pip install --upgrade kapsel-cli
```

#### Windows: Scoop

```powershell
# 添加官方 Bucket 并安装
scoop bucket add kapsel https://github.com/MrEiu/scoop-bucket
scoop install kapsel
```

#### macOS & Linux: Homebrew

```bash
# 添加官方 Tap 并安装
brew tap MrEiu/tap
brew install kapsel
```

#### Debian & Ubuntu: APT & DPKG (.deb)

```bash
# 官方 GitHub 下载安装:
curl -LO https://github.com/MrEiu/Kapsel/releases/latest/download/kapsel_amd64.deb
sudo dpkg -i kapsel_amd64.deb || sudo apt-get install -f -y

# 国内镜像加速下载安装:
curl -LO https://ghproxy.net/https://github.com/MrEiu/Kapsel/releases/latest/download/kapsel_amd64.deb
sudo dpkg -i kapsel_amd64.deb || sudo apt-get install -f -y
```

---

### 3. 💾 预编译免环境绿色版 (独立运行)

无需安装 Python、Node 或任何开发环境，下载解压即可运行：

| 平台 / 架构 | 发布文件名 | 官方 GitHub 直链 | 国内高速镜像直链 |
| :--- | :--- | :--- | :--- |
| **Windows x86_64** | `kapsel-windows-x86_64.zip` | [下载](https://github.com/MrEiu/Kapsel/releases/latest/download/kapsel-windows-x86_64.zip) | [国内镜像下载](https://ghproxy.net/https://github.com/MrEiu/Kapsel/releases/latest/download/kapsel-windows-x86_64.zip) |
| **Linux x86_64** | `kapsel-linux-x86_64.tar.gz` | [下载](https://github.com/MrEiu/Kapsel/releases/latest/download/kapsel-linux-x86_64.tar.gz) | [国内镜像下载](https://ghproxy.net/https://github.com/MrEiu/Kapsel/releases/latest/download/kapsel-linux-x86_64.tar.gz) |
| **macOS (Universal)** | `kapsel-macos-universal.tar.gz` | [下载](https://github.com/MrEiu/Kapsel/releases/latest/download/kapsel-macos-universal.tar.gz) | [国内镜像下载](https://ghproxy.net/https://github.com/MrEiu/Kapsel/releases/latest/download/kapsel-macos-universal.tar.gz) |
| **Debian / Ubuntu** | `kapsel_amd64.deb` | [下载](https://github.com/MrEiu/Kapsel/releases/latest/download/kapsel_amd64.deb) | [国内镜像下载](https://ghproxy.net/https://github.com/MrEiu/Kapsel/releases/latest/download/kapsel_amd64.deb) |

> 💡 **使用提示**：解压后将 `kapsel` 与 `kps`（Windows 为 `kapsel.exe` 与 `kps.exe`）复制到系统的 PATH 目录（例如 `~/.kapsel/bin` 或 `/usr/local/bin`）即可。

---

### 4. 🌐 国际版全套工具链自动安装脚本

全自动安装 Kapsel 并配置官方推荐的全部 CLI 工具套件（`carapace`、`zoxide`、`mise`、`chsrc`、`aichat`、`pueue`、`chezmoi`、`pet`、`tealdeer`、`fzf`）：

```powershell
# Windows (PowerShell):
irm https://raw.githubusercontent.com/MrEiu/Kapsel/master/scripts/install_tools_windows.ps1 | iex
```

```bash
# macOS:
curl -fsSL https://raw.githubusercontent.com/MrEiu/Kapsel/master/scripts/install_tools_macos.sh | bash

# Linux:
curl -fsSL https://raw.githubusercontent.com/MrEiu/Kapsel/master/scripts/install_tools_linux.sh | bash
```

---

### 5. 🛠️ 源码构建与开发者模式

```bash
git clone https://github.com/MrEiu/Kapsel.git
cd Kapsel
pip install -e .
kps completion sync
```

---

## 🧩 官方插件生态

Kapsel 官方维护了一套高性能、即装即用的工程化插件家族：

| 插件 | 命令前缀 | 核心依赖 | 功能介绍 |
| :--- | :--- | :--- | :--- |
| **`init`** | `kps init` | **`mise`** (Rust) | 项目级开发工具链与多语言运行时管理（统一替代 nvm、pyenv、rbenv 等）。 |
| **`portal`** | `kps portal` / `z` | **`zoxide`** (Rust) | 基于权重与频次的高性能目录瞬移导航，支持交互模糊搜索。 |
| **`shore`** | `kps shore` | **`chsrc`** (C) | 全平台换源神器，自动将 PyPI、Rust、Node、Go 及系统镜像切换至最快源。 |
| **`install`** | `kps install` | **`mpm`** (Python) | 统一包管理客户端，一站式纳管 Scoop、Winget、Brew、APT 等 20+ 包管理器。 |
| **`alias`** | `kps alias` | *原生引擎* | 跨终端通用的命令别名系统，提供跨 Shell 无缝翻译映射。 |
| **`ai`** | `kps ai` | **`aichat`** (Rust) | 终端原生 AI 智能助手，支持 OpenAI、Claude、Gemini、DeepSeek、Ollama 等模型。 |
| **`autopilot`**| `kps autopilot`| **`pueue`** (Rust) | 后台异步守护任务队列与耗时命令编排调度管理器。 |
| **`fuck`** | `kps fuck` | **`thefuck`** (Python) | 智能终端敲错自动纠正，快速修复上一条敲错的命令。 |
| **`help`** | `kps help <cmd>`| **`tealdeer`** (Rust) | 高性能终端实用示例速查表（替代臃肿的 man 手册）。 |
| **`profile`** | `kps profile` | **`chezmoi`** (Go) | 跨平台多设备 Dotfiles、Shell 配置文件及密钥环境同步工具。 |
| **`rec`** | `kps rec` | **`pet`** (Go) | 命令行代码片段管理器，支持参数化收藏与交互执行。 |

---

## 📊 功能特性矩阵对比

| 核心特性 | Kapsel | 传统原生 Shell (Bash/Zsh/Pwsh) | Starship | Oh-My-Zsh |
| :--- | :---: | :---: | :---: | :---: |
| **非侵入式沙盒 (零配置文件篡改)** | **原生具备** | 无 | 无 | 无 |
| **1,000+ 命令上下文深度补全 (Carapace)** | **开箱即用** | 需繁琐手动配插件 | 无 (仅提示符) | 部分 (易卡顿) |
| **Linux-First 跨平台命令平滑抹平 (`kps`)** | **原生具备** | 无 | 无 | 无 |
| **双根规约树 (绝对杜绝宿主命令冲突)** | **原生具备** | 无 | 无 | 无 |
| **卡片式终端输入/输出流框线美学** | **原生具备** | 无 | 仅提示符 | 无 |
| **用户独立沙盒数据状态 (`~/.kapsel/`)** | **统一隔离** | 分散杂乱 | 无 | 分散杂乱 |
| **亚毫秒级异步无感输入响应** | **原生具备** | 取决于配置 | 原生具备 | 经常卡顿 |

---

## 📖 常用命令速查手册

### 交互终端胶囊模式 (`kapsel` / `kps`)

在当前终端中启动 Kapsel 交互会话：
```bash
kapsel
```

会话中支持的系统管理指令：
```text
help                   展示 Kapsel 核心交互手册与命令快速导航
status                 查看当前系统运行环境、宿主 Shell、Git 分支与沙盒状态
upgrade [plugin]       两阶段升级检查：一键检查 Kapsel 内核与官方插件新版本并查看更新日志
search [-a]            发现与检索官方插件目录，查看版本与当前安装/启用状态
enable <plugin>        激活已停用的插件并自动重编译补全规约
disable <plugin>       软停用指定插件，保留物理文件且不加载其补全与命令
config                 查看或编辑全局配置 (~/.kapsel/config.yaml)
  config path          输出物理配置文件路径
  config edit          使用系统默认编辑器打开配置
  config get <key>     查询某项配置的值
  config set <k> <v>   在命令行修改配置值
  config reload        免重启热重载配置
completion             查看与管理 Carapace 声明式补全规约
  completion ls        列出当前活跃的所有命令补全规格与挂载状态
  completion sync      强制重新编译并同步双根规约 (kps.yaml 与 kapsel.yaml)
  completion new <cmd> 快速脚手架生成一份新的规约模板
  completion path      查看规格存放目录
datadir                查看或安全迁移 Kapsel 沙盒存储目录
language <lang>        切换界面语言 (zh_CN, en, ja, es, fr, de, ru)
toggle                 切换默认终端接入模式（首次开启，再次调用恢复原生）
clear                  清屏并重新打印头部卡片
exit                   干净退出胶囊模式，返回原生 Shell
```

### 单发调用模式 (无需常驻)

您也可以在普通终端中直接通过 `kps` 调用胶囊命令或插件：

```bash
# 查看运行状态与补全列表
kps status
kps completion ls

# 调用插件命令
kps portal ls
kps shore get
kps init use node@22

# 跨平台通用别名操作
kps rm -rf dist/
kps ls -la
```

---

## 🔒 沙盒隔离与数据存储模型

Kapsel 严格奉行**零污染安全守则**，所有数据、依赖、单二进制、规约和日志统一收敛在用户主目录下的 `.kapsel` 隐藏目录中：

```text
~/.kapsel/
├── config.yaml          # 全局用户配置（界面配色、卡片样式、默认语言）
├── history.db           # 独立的 SQLite 数据库，记录命令执行频次与历史
├── bin/                 # 用户空间独立二进制工具目录（carapace、zoxide、mise 等）
├── specs/               # 用户自定义的声明式自动补全规约目录
├── plugins/             # 本地安装的官方与社区插件库
└── logs/                # 会话运行日志与错误诊断文件
```

---

## 🧪 自动化测试与质量保障

Kapsel 采用工业级规范测试套件，全面覆盖补全规约编译器、冲突哨兵、插件生命周期与多语言机制：

```bash
# 克隆仓库
git clone https://github.com/MrEiu/Kapsel.git
cd Kapsel

# 安装测试套件
pip install -e ".[test]"

# 运行全量单元测试
pytest tests/ -v
```

所有 79 项自动化测试全部通过，保证各种平台上的健壮性与稳定性。

---

## 🤝 贡献与社区

欢迎参与 Kapsel 的开源共建！
- 如果发现 Bug 或有新功能想法，请前往 [GitHub Issues](https://github.com/MrEiu/Kapsel/issues) 提交反馈；
- 如果想开发或提交新插件，请参考 [插件开发规范](docs/PLUGIN_SPEC.md) 与 [插件仓库](https://github.com/MrEiu/plugins)。

---

## 📄 开源许可证

Kapsel 基于 **[MIT License](LICENSE)** 开源协议发布。

<div align="center">
  <sub>Designed with modern terminal ergonomics by MrEiu and the Kapsel Open-Source Team.</sub>
</div>
