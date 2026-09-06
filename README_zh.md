<div align="center">

# ⚡ Kapsel

**一个跨平台的终端环境，为您的 Shell 提供统一命令、上下文感知自动补全，并且零全局污染。**

[![PyPI Version](https://img.shields.io/pypi/v/kapsel-cli?color=3776AB&logo=pypi&logoColor=white&style=flat-square)](https://pypi.org/project/kapsel-cli/)
[![Python Version](https://img.shields.io/badge/Python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-3776AB.svg?style=flat-square&logo=python&logoColor=white)](https://pypi.org/project/kapsel-cli/)
[![Platform Support](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-4D4D4D.svg?style=flat-square&logo=linux&logoColor=white)](https://github.com/MrEiu/Kapsel)
[![License](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](LICENSE)

[为什么选择 Kapsel？](#-为什么选择-kapsel) •
[功能特性](#-功能特性) •
[快速开始](#-快速开始) •
[内置插件](#-内置插件) •
[安装指南](#-安装指南) •
[架构设计](#-架构设计--沙箱机制) •
[🇨🇳 简体中文](README_zh.md)

</div>

---

### 📺 交互式胶囊演示

```text
╭─ kapsel [pwsh] ~/Projects/Kapsel 14:32:05
╰─ ❯ git checkout -b feature/dynamic-specs
✔ 0  git checkout -b feature/dynamic-specs  ⏱ 24ms
```

> **封装复杂性，展现简洁性。**
> 像往常一样运行您的原生 Shell 可执行文件，同时享受自动命令翻译、内联建议、丰富的补全规范以及模块化工具链——所有这些都安全地隔离在 `~/.kapsel/` 目录中。

---

## 💡 为什么选择 Kapsel？

在操作系统之间切换往往会导致肌肉记忆失效、点文件杂乱无章，以及自动补全配置支离破碎。Kapsel 通过一种非侵入式的胶囊层弥合了这一差距：

| 挑战 | 传统 Shell 配置 | 使用 Kapsel |
| :--- | :--- | :--- |
| **跨平台摩擦** | 不同操作系统间命令割裂（`dir` 与 `ls`、`rmdir` 与 `rm -rf`） | 在 Windows、macOS 和 Linux 上统一以 Linux 优先的命令层 |
| **Shell 配置文件污染** | `.bashrc` 或 `$PROFILE` 臃肿，充斥着脆弱的全局脚本 | 完全自包含的沙盒环境，位于 `~/.kapsel/`（零全局修改） |
| **自动补全配置** | 每个 Shell 需手动配置，往往不完整或响应缓慢 | 通过 Carapace 为 1,000+ CLI 工具提供即时、上下文感知的补全 |
| **工具链与同步碎片化** | 工具彼此割裂，需重复手动安装 | 集成 `kps` 插件，涵盖运行时、镜像源、目录跳转与同步 |

---

## ✨ 功能特性

- **🌐 跨平台命令一致性**：在任何终端中自然输入标准命令（`ls -la`、`cat`、`rm -rf`、`grep`），系统会自动将其转换为主机原生操作，且不会劫持主机内置命令。
- **⚡ 上下文感知自动补全**：与 [Carapace](https://carapace.sh) 集成，在 PowerShell、Bash 和 Zsh 中提供多级参数与上下文补全（Git 分支、Docker 镜像、npm 脚本）。
- **🛡️ 零污染沙盒机制**：所有内容（二进制文件、SQLite 历史记录、声明式规范、插件及日志）均存放于 `~/.kapsel/` 目录内。您的主机 Shell 配置文件完全不受影响。
- **🧩 精选插件生态系统**：通过统一的 `kps` 命令直接访问强大的开发者工具（`zoxide`、`mise`、`chsrc`、`pueue`、AI 助手）。
- **🎨 现代卡片式美学设计**：清晰的视觉命令卡片框架，配备退出码徽章（`✔ 0` / `✘ 1`）、执行计时器，并原生支持 7 种语言的国际化（i18n）。

---

## 🚀 快速开始

启动交互式胶囊外壳：

```bash
kapsel
```

在 Kapsel 内部，命令以原生方式运行，并带有增强反馈：

```bash
# 1. 原生直通，附带计时与退出码卡片
git status
docker ps

# 2. 在任何操作系统上实现通用命令翻译
rm -rf ./temp_dir
cat package.json

# 3. 随时使用内置插件
kps portal work        # 跳转到目录（zoxide）
kps ai "解释 git rebase"  # 询问终端 AI 助手
kps shore get          # 自动选择最快的软件包镜像

# 4. 检查胶囊状态
kps status
```

> **一次性执行**：您也可以直接在常规 shell 中使用 `kps <命令>` 调用 Kapsel 工具（例如 `kps portal`、`kps status`、`kps ai`）。

---

## 🧩 内置插件

Kapsel 预配置了 11 个解耦的官方插件，均位于 `kps` 命名空间下：

| 插件 | 命令 | 功能说明 | 底层驱动 |
| :--- | :--- | :--- | :--- |
| **`portal`** | `kps portal` / `z` | 基于 frecency 加权算法的快速目录跳转 | [zoxide](https://github.com/ajeetdsouza/zoxide) |
| **`ai`** | `kps ai` | 终端 AI 助手，用于生成和解释命令 | OpenAI / Claude / Ollama |
| **`init`** | `kps init` | 多语言工具链运行时管理器（Node、Python、Go、Rust） | [mise](https://github.com/jdx/mise) |
| **`shore`** | `kps shore` | 基准测试并切换最快的软件包与操作系统下载镜像 | [chsrc](https://github.com/AkihiroSuda/chsrc) |
| **`install`** | `kps install` | 聚合 20+ 包管理器的通用软件安装器 | [mpm](https://github.com/MrEiu/mpm) |
| **`alias`** | `kps alias` | 跨平台别名翻译，零命名空间冲突 | 原生引擎 |
| **`autopilot`**| `kps autopilot`| 后台队列与自主守护任务运行器 | [pueue](https://github.com/Nukesor/pueue) |
| **`help`** | `kps help <cmd>`| 即时、社区驱动的实用命令速查表 | [tealdeer](https://github.com/dbrgn/tealdeer) |
| **`fuck`** | `kps fuck` | 智能自动纠错与语法修复，针对输入错误的命令 | [thefuck](https://github.com/nvbn/thefuck) |
| **`profile`** | `kps profile` | 跨平台点文件与工作站配置同步 | [chezmoi](https://github.com/twpayne/chezmoi) |
| **`rec`** | `kps rec` | 交互式 CLI 命令片段书签与运行器 | [pet](https://github.com/knqyf263/pet) |

---

## 📦 安装指南

### 推荐方式（pipx / pip）

```bash
# 通过 pipx 进行隔离安装（推荐）
pipx install kapsel-cli

# 或使用标准 pip 安装
pip install --upgrade kapsel-cli
```

### 一键自动化安装脚本

快速引导脚本，可自动检测您的操作系统并配置命令补全：

```bash
# macOS 和 Linux：
curl -fsSL https://raw.githubusercontent.com/MrEiu/Kapsel/master/scripts/install.sh | bash

# Windows（PowerShell）：
irm https://raw.githubusercontent.com/MrEiu/Kapsel/master/scripts/install.ps1 | iex
```

### 其他安装选项

- **独立预编译二进制文件**：从 [GitHub Releases](https://github.com/MrEiu/Kapsel/releases/latest) 下载即开即用的发布版本。
- **包管理器**：可通过 Scoop（`scoop install kapsel`）、Homebrew 以及 Debian/Ubuntu 的 `.deb` 包进行安装。
- **从源码构建**：`git clone https://github.com/MrEiu/Kapsel.git && cd Kapsel && pip install -e .`

👉 *有关中国镜像加速及完整平台包管理器详情，请参阅 **[docs/INSTALLATION.md](docs/INSTALLATION.md)**。*

---

## ⚙️ 配置

Kapsel 将其配置存储在 `~/.kapsel/config.yaml` 中。您可以直接在终端中管理设置：

```bash
# 查看配置仪表板
kps config

# 在外部编辑器中打开配置文件
kps config edit

# 即时调整设置
kps config set ui.enable_banner false
kps config set interaction.autosuggest_sensitivity 0.2
```

---

## 🏛️ 架构与沙箱隔离

Kapsel 遵循**零污染原则**。所有运行时状态均被严格隔离：

```text
~/.kapsel/
├── config.yaml          # 全局 UI 配置、主题及交互设置
├── history.db           # 持久化 SQLite 数据库，存储命令历史与统计信息
├── bin/                 # 用户空间独立二进制工具（carapace、zoxide、mise 等）
├── specs/               # 声明式自动补全 YAML 规范
├── plugins/             # 已安装的官方及社区插件扩展
└── logs/                # 诊断日志与会话指标
```

- **双状态引擎**：原生可执行文件通过宿主子外壳直通方式直接运行；胶囊工具则通过统一的 `kps` 注册表执行。
- **冲突哨兵**：确保原生外壳内建命令（如 PowerShell 的 `Get-Alias`、`Get-Help`）永远不会被拦截或劫持。
- **插件隔离**：插件独立运行，确保第三方扩展不会导致核心外壳崩溃。

---

## 🧪 开发与测试

```bash
# 克隆仓库
git clone https://github.com/MrEiu/Kapsel.git
cd Kapsel

# 安装可编辑包及测试依赖
pip install -e ".[test]"

# 运行单元测试套件
pytest tests/ -v
```

---

## 📄 许可证

本项目基于 **[MIT 许可证](LICENSE)** 分发，由 MrEiu 及开源贡献者共同构建。
