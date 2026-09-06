<div align="center">

# ⚡ Kapsel

**跨平台终端胶囊：打造更纯净、更统一的现代化命令行体验。**

[![PyPI Version](https://img.shields.io/pypi/v/kapsel-cli?color=3776AB&logo=pypi&logoColor=white&style=flat-square)](https://pypi.org/project/kapsel-cli/)
[![Python Version](https://img.shields.io/badge/Python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-3776AB.svg?style=flat-square&logo=python&logoColor=white)](https://pypi.org/project/kapsel-cli/)
[![Platform Support](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-4D4D4D.svg?style=flat-square&logo=linux&logoColor=white)](https://github.com/MrEiu/Kapsel)
[![License](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](LICENSE)

[快速开始](#-快速开始) ·
[特性亮点](#-特性亮点) ·
[插件生态](#-插件生态) ·
[安装指南](#-安装指南) ·
[系统架构](#-系统架构) ·
[参考文档](#-参考文档)

[English](README.md) ·
[🇯🇵 日本語](README_ja.md) ·
[🇷🇺 Русский](README_ru.md) ·
[🇩🇪 Deutsch](README_de.md) ·
[🇪🇸 Español](README_es.md) ·
[🇫🇷 Français](README_fr.md) ·
[🇵🇱 Polski](README_pl.md)

</div>

---

## 📺 交互预览

```text
╭─ kapsel [pwsh] ~/Projects/Kapsel 14:32:05
╰─ ❯ git checkout -b feature/dynamic-specs
✔ 0  git checkout -b feature/dynamic-specs  ⏱ 24ms
```

> **封装复杂，呈现纯粹。**
>
> 像往常一样继续使用宿主 Shell 与系统原生命令，Kapsel 为你注入统一命令转义层、上下文感知自动补全、行内实时建议与可扩展插件沙箱 —— 一切状态皆自包含于 `~/.kapsel/`。

---

## 💡 为什么选择 Kapsel？

现代开发者的命令行工作流仍被底层操作系统与不同的 Shell 严重割裂。

相同的日常任务在 Windows、macOS 和 Linux 上往往需要不同的命令与语法；Shell 配置分散在 `.bashrc`、`.zshrc`、PowerShell Profiles 等多种文件中；而补全系统和开发辅助工具通常需要分别独立安装与反复配置。

Kapsel 在你现有的终端外围构建了一层轻量无侵入的胶囊环境：

| 痛点场景 | 传统配置方案 | Kapsel 方案 |
| :--- | :--- | :--- |
| **跨平台命令语法** | 不同操作系统命令与参数差异显著 | Linux-First 统一跨平台命令层 |
| **Shell 环境配置** | 全局环境变量污染与脚本分散 | 严格隔离在 `~/.kapsel/` 自包含沙箱 |
| **自动补全体验** | 每个 Shell 与工具需单独配置复杂规则 | 基于 Carapace 引擎的上下文智能感知补全 |
| **开发效能工具** | 工具分散、配置不一、维护繁琐 | 统一收拢于 `kps` 命名空间插件生态 |
| **扩展灵活性** | 高度依赖特定 Shell 语法扩展 | 语言中立、进程独立的模块化插件架构 |

Kapsel 不会替换你的宿主 Shell 或系统原生可执行程序。它作为旁路辅助层，提供始终一致的现代化执行环境。

---

## ✨ 特性亮点

### 🌐 原生透传与跨平台执行

直接运行系统已安装的所有命令：

```bash
git
docker
python
npm
cargo
vim
```

同时，Kapsel 为高频操作提供开箱即用的 Linux-First 统一命令层：

```bash
ls -la
cat package.json
rm -rf ./dist
grep -r "TODO" .
```

宿主 Shell 内部保留命令与系统内建命令享有最高保护优先级，杜绝误拦截。

---

### ⚡ 上下文感知多级补全

Kapsel 深度集成 [Carapace](https://carapace.sh) 补全引擎，提供多层级语义补全：

补全引擎深入理解命令、参数、标志位以及动态上下文：

- Git 分支与标签
- Docker 容器名与镜像
- Kubernetes 资源与命名空间
- npm 脚本名称
- 1000+ 常用 CLI 规范支持

补全规范采用声明式管理，可通过插件或自定义 Spec 轻松扩展。

---

### 💡 行内智能历史建议

基于本地 SQLite 历史时序存储，在你键入时异步推断最近匹配的高频历史命令。

按下 `→` 键即可一键补全整行或按词采纳。

所有历史记录与运行时状态均安全保留在 Kapsel 沙箱内部。

---

### 🛡️ 零污染纯净沙箱

Kapsel 将自身的全部配置、工具二进制、执行历史、补全规范、插件及日志统一存储于：

```text
~/.kapsel/
```

绝不擅自修改任何宿主环境配置文件：

```text
.bashrc
.zshrc
config.fish
PowerShell profiles
```

让宿主系统与终端始终保持纯净可控。

---

### 🧩 模块化插件架构

在 `kps` 命名空间下提供专有插件运行时。

插件可以扩展命令、集成工作流、挂载补全规范及引入外部现代化 CLI 工具，无需侵入 Kapsel 核心。

官方插件与社区插件共享一致的开放扩展架构。

---

### 🎨 交互式现代终端体验

交互式胶囊呈现高雅紧凑的双行卡片布局：

```text
╭─ ...
╰─ ❯ ...
✔ 0  ...  ⏱ 24ms
```

命令执行完毕后即刻回显退出码与耗时统计（毫秒级），界面全面支持多语言本地化显示。

---

# 🚀 快速开始

## 1. 安装

推荐使用 `pipx` 进行隔离安装：

```bash
pipx install kapsel-cli
```

或使用标准 `pip`：

```bash
pip install --upgrade kapsel-cli
```

## 2. 启动 Kapsel

```bash
kapsel
```

启动后即可正常使用终端：

```bash
git status
docker ps
python --version
```

在需要时无缝使用跨平台通用命令：

```bash
ls -la
cat package.json
rm -rf ./temp
```

## 3. 调用 Kapsel 扩展工具

所有扩展功能与插件均可通过 `kps` 指令访问：

```bash
kps status
kps config
kps portal
kps ai
```

例如：

```bash
kps portal work
kps ai "解释 git rebase 的作用"
kps shore get
```

## 4. 单次命令直执

无需进入交互式胶囊，直接在宿主 Shell 中执行即可：

```bash
kps status
kps portal
kps ai "查找当前目录下大于 100M 的文件"
```

非常适合集成到脚本、Shell 别名、自动化工作流及单次任务中。

---

# 🧩 插件生态

Kapsel 采用高度面向插件的设计理念，而非臃肿膨胀的静态内建集合。

生态体系划分为 **官方核心插件** 与 **社区开放插件**。

## 官方插件

Kapsel 当前预置并维护以下官方核心插件：

| 插件 | 命令入口 | 功能描述 | 核心驱动 |
| :--- | :--- | :--- | :--- |
| **`portal`** | `kps portal` / `z` | 基于频次权重的超快速目录跳转 | [zoxide](https://github.com/ajeetdsouza/zoxide) |
| **`ai`** | `kps ai` | 终端智能伴侣，支持命令生成、解释与故障诊断 | OpenAI / Claude / Ollama |
| **`init`** | `kps init` | 多语言通用运行时与工具链管理器（Node、Python、Go、Rust 等） | [mise](https://github.com/jdx/mise) |
| **`shore`** | `kps shore` | 全球与国内开源镜像源测速与一键智能切换 | [chsrc](https://github.com/AkihiroSuda/chsrc) |
| **`install`** | `kps install` | 跨系统跨包管理器统一软件安装工具 | [mpm](https://github.com/MrEiu/mpm) |
| **`alias`** | `kps alias` | 跨平台命令别名转义与平台抹平引擎 | 原生引擎 |
| **`autopilot`** | `kps autopilot` | 异步后台任务队列管理与长周期作业守护 | [pueue](https://github.com/Nukesor/pueue) |
| **`help`** | `kps help <cmd>` | 实用命令精简速查与示例 Cheatsheet | [tealdeer](https://github.com/dbrgn/tealdeer) |
| **`fuck`** | `kps fuck` | 敲错命令一键语法纠错并重新执行 | [thefuck](https://github.com/nvbn/thefuck) |
| **`profile`** | `kps profile` | 点文件与工作站配置跨平台版本化管理 | [chezmoi](https://github.com/twpayne/chezmoi) |
| **`rec`** | `kps rec` | CLI 常用代码片段收藏、参数化模板与运行 | [pet](https://github.com/knqyf263/pet) |

官方插件作为解耦组件独立发布与维护，确保 Kapsel 核心轻量高速。

---

## 🌍 社区插件

Kapsel 鼓励全球开发者共建开放生态。

你可以自由开发扩展插件：

- 自定义业务指令
- 研发流程集成
- 第三方云服务接入
- 定制 Carapace 补全规范
- 团队自动化脚本打包

欢迎通过 **[Kapsel 官方插件中心](https://github.com/MrEiu/plugins)** 提交你的开源插件。

---

# 📦 安装指南

## 推荐安装方式

### pipx

```bash
pipx install kapsel-cli
```

### pip

```bash
pip install --upgrade kapsel-cli
```

---

## 一键自动化安装脚本

### macOS & Linux

```bash
curl -fsSL https://raw.githubusercontent.com/MrEiu/Kapsel/master/scripts/install.sh | bash
```

中国大陆加速源：

```bash
curl -fsSL https://raw.githubusercontent.com/MrEiu/Kapsel/master/scripts/install_cn.sh | bash
```

### Windows PowerShell

```powershell
irm https://raw.githubusercontent.com/MrEiu/Kapsel/master/scripts/install.ps1 | iex
```

中国大陆加速源：

```powershell
irm https://raw.githubusercontent.com/MrEiu/Kapsel/master/scripts/install_cn.ps1 | iex
```

安装脚本会自动检测操作系统与架构，配置 Kapsel 及其 Carapace 自动补全环境。

---

## 免 Python 独立单二进制包

针对无 Python 环境的生产机器与容器环境，提供预编译单二进制发布包：

| 平台 / 架构 | 发布产物 |
| :--- | :--- |
| **Windows x86_64** | `kapsel-windows-x86_64.zip` |
| **Linux x86_64** | `kapsel-linux-x86_64.tar.gz` |
| **macOS Universal** | `kapsel-macos-universal.tar.gz` |
| **Debian / Ubuntu** | `kapsel_amd64.deb` |

前往 **[GitHub Releases](https://github.com/MrEiu/Kapsel/releases/latest)** 获取最新版本。

---

## 系统包管理器

- **Scoop (Windows)**：`scoop install kapsel`
- **Homebrew (macOS/Linux)**：`brew install kapsel`
- **Debian / Ubuntu (.deb)**：`sudo dpkg -i kapsel_amd64.deb`

详见 **[完整安装指南](docs/INSTALLATION.md)**。

---

## 源码安装与编译

```bash
git clone https://github.com/MrEiu/Kapsel.git
cd Kapsel
pip install -e .
kps completion sync
```

---

# ⚙️ 配置系统

Kapsel 主配置文件位于：

```text
~/.kapsel/config.yaml
```

可在终端中直接查看与修改配置：

```bash
kps config
```

使用默认编辑器快速打开：

```bash
kps config edit
```

命令行直接读写键值：

```bash
kps config set ui.enable_banner false
kps config set interaction.autosuggest_sensitivity 0.2
```

修改后无需重启会话即可自动热重载生效。详见 **[配置指南](docs/configuration.md)**。

---

# 🏛️ 系统架构

Kapsel 遵循“物理独立、逻辑统一”的设计原则，构建于宿主 Shell 外围：

```text
                     宿主终端
                        │
                        ▼
             ┌─────────────────────┐
             │       Kapsel        │
             │                     │
             │   命令分发调度器     │
             │   补全推理引擎       │
             │   插件注册中心       │
             │   历史时序 / 状态    │
             └──────────┬──────────┘
                        │
              ┌─────────┴─────────┐
              ▼                   ▼
       系统原生可执行程序    Kapsel 扩展指令
       git / docker / ...    kps <command>
```

## 双态执行管道 (Dual-State Execution)

- **原生管道 (Native Execution)**：系统原生命令直接透明穿透至宿主环境执行，完整保留 TTY 交互、信号捕捉（Ctrl+C/Ctrl+Z）、管道重定向及子进程表现。
- **胶囊管道 (Kapsel Execution)**：通过 `kps` 命名空间及插件系统调度分发，统一处理别名转义与跨平台抹平。

## 零冲突命名空间 (Collision-Safe Namespaces)

严格隔离易冲突指令（如 `alias`、`help`、`install`、`history`、`profile`、`ps`、`kill`、`dir` 等），收拢于 `kps` 命令空间内，确保宿主 Shell 自带的同名内建命令不受劫持。

## 零污染沙箱组织 (Zero-Pollution State)

```text
~/.kapsel/
├── config.yaml          # 全局配置
├── history.db           # SQLite 历史持久化存储
├── bin/                 # 用户空间独立依赖二进制
├── specs/               # Carapace 声明式补全定义
├── plugins/             # 本地安装的扩展插件
└── logs/                # 运行日志与诊断信息
```

---

# 📚 参考文档

| 文档名称 | 内容概述 |
| :--- | :--- |
| [安装指南](docs/INSTALLATION.md) | 全平台详细安装步骤、镜像源配置与故障排查 |
| [配置参考](docs/configuration.md) | 完整配置项说明与运行时参数调优 |
| [命令手册](docs/commands.md) | 核心管理指令与 `kps` 插件指令全览 |
| [插件使用](docs/plugins.md) | 官方插件详解与使用技巧 |
| [插件开发](https://github.com/MrEiu/plugins) | 编写自定义插件、发布与规范说明 |
| [架构设计](docs/architecture.md) | 核心引擎底层设计与实现细节 |

---

# 🧪 开发与测试

克隆代码仓库：

```bash
git clone https://github.com/MrEiu/Kapsel.git
cd Kapsel
```

安装开发与测试依赖：

```bash
pip install -e ".[test]"
```

运行完整自动化测试套件：

```bash
pytest tests/ -v
```

---

# 🤝 参与贡献

欢迎任何形式的贡献！

- **核心改进**：提交核心引擎 Bug 修复、补全优化或架构建议。
- **插件生态**：在 **[Kapsel 官方插件仓库](https://github.com/MrEiu/plugins)** 提交新插件。
- **文档完善**：翻译文档、修正错误或补充实战使用案例。

---

# 📄 开源许可

本项目遵循 **[MIT License](LICENSE)** 开源协议。

---

<div align="center">

**Kapsel — 封装复杂，呈现纯粹。**

由 [MrEiu](https://github.com/MrEiu) 及开源社区贡献者共同打造。

</div>
