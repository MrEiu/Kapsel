# Kapsel 安装与部署指南 (Installation & Deployment Guide)

本指南汇总了 **Kapsel** 在不同操作系统（Windows、macOS、Linux）及不同网络环境（国际通用、中国大陆加速）下的所有安装途径。

---

## 目录 (Table of Contents)

1. [🇨🇳 中国大陆极速通道 (China Fast-Track - 镜像源加速)](#1-中国大陆极速通道-china-fast-track)
   - [方式一：下载本地脚本后执行安装 (推荐)](#方式一使用镜像源下载脚本后执行安装-强烈推荐)
   - [方式二：国内镜像一行流快速执行](#方式二国内镜像一行流快速执行-管道执行)
   - [方式三：清华源 PyPI 在线安装](#方式三清华大学-pypi-国内镜像在线安装)
2. [📦 包管理器安装 (Package Managers)](#2-包管理器安装-package-managers)
   - [PyPI / pipx / pip](#pypi-python-39)
   - [Scoop (Windows)](#windows-scoop)
   - [Homebrew (macOS & Linux)](#macos--linux-homebrew)
   - [APT / dpkg (Debian & Ubuntu .deb)](#debian--ubuntu-apt--dpkg-deb)
3. [💾 预编译免环境单文件绿色版 (Standalone Binaries)](#3-预编译免环境单文件绿色版-standalone-binaries)
4. [🌐 国际版全套工具链自动部署脚本 (Global Toolchain Installers)](#4-国际版全套工具链自动部署脚本-global-toolchain-installers)
5. [🛠️ 源码构建与开发者调试 (Build from Source)](#5-源码构建与开发者调试-build-from-source)
6. [🔍 安装后验证与常见问题排查 (Verification & Troubleshooting)](#6-安装后验证与常见问题排查-verification--troubleshooting)

---

## 1. 🇨🇳 中国大陆极速通道 (China Fast-Track)

针对中国大陆网络环境深度定制，自动通过国内高速 CDN 代理和开源镜像站（清华大学 TUNA、阿里云、腾讯云、ghproxy 等）拉取资源，解决连接超时与中断问题。

### 方式一：使用镜像源下载脚本后执行安装 (⭐ 强烈推荐)

> **为什么推荐这种方式？**  
> 一行流管道（如 `irm ... | iex` 或 `curl ... | bash`）在网络波动时容易因数据包截断而抛出语法错误，或者受限于操作系统的脚本执行安全策略（Execution Policy）。  
> **先下载脚本文件到本地，再执行安装**，具有更高的稳定性和可靠性。

#### Windows (PowerShell):
```powershell
# 1. 使用国内镜像加速下载 CN 安装脚本
Invoke-WebRequest -Uri "https://ghproxy.net/https://raw.githubusercontent.com/MrEiu/Kapsel/master/scripts/install_cn.ps1" -OutFile "install_cn.ps1"

# 2. 授权当前进程运行脚本并执行
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned -Force
.\install_cn.ps1
```

#### Linux & macOS (Bash):
```bash
# 1. 使用国内镜像加速下载 CN 安装脚本
curl -fsSL "https://ghproxy.net/https://raw.githubusercontent.com/MrEiu/Kapsel/master/scripts/install_cn.sh" -o install_cn.sh

# 2. 运行脚本进行安装
bash install_cn.sh
```

---

### 方式二：国内镜像一行流快速执行 (管道执行)

适合网络状况良好、追求极速部署的用户：

#### Windows (PowerShell):
```powershell
irm https://ghproxy.net/https://raw.githubusercontent.com/MrEiu/Kapsel/master/scripts/install_cn.ps1 | iex
```

#### Linux & macOS (Bash):
```bash
curl -fsSL https://ghproxy.net/https://raw.githubusercontent.com/MrEiu/Kapsel/master/scripts/install_cn.sh | bash
```

---

### 方式三：清华大学 PyPI 国内镜像在线安装

如果您已经配置了 Python 3.9+ 环境，可以直接使用国内最稳定的清华大学 TUNA 镜像源安装：

```bash
# 标准 pip 安装
pip install --upgrade kapsel-cli -i https://pypi.tuna.tsinghua.edu.cn/simple

# 或通过 pipx 隔离安装
pipx install kapsel-cli --pip-args="-i https://pypi.tuna.tsinghua.edu.cn/simple"
```

---

## 2. 📦 包管理器安装 (Package Managers)

### PyPI (Python 3.9+)

适用于已具备 Python 开发环境的用户：

```bash
# 推荐：使用 pipx 进行沙盒隔离安装（避免包依赖冲突）
pipx install kapsel-cli

# 或直接通过 pip 安装
pip install --upgrade kapsel-cli
```

### Windows: Scoop

Scoop 是 Windows 开发者首选的命令行包管理器：

```powershell
# 1. 添加 Kapsel 官方 Bucket
scoop bucket add kapsel https://github.com/MrEiu/scoop-bucket

# 2. 一键安装
scoop install kapsel

# 更新至最新版
scoop update kapsel
```

### macOS & Linux: Homebrew

Homebrew 是 macOS 和 Linux 广泛使用的包管理器：

```bash
# 1. 添加 Kapsel 官方 Tap
brew tap MrEiu/tap

# 2. 一键安装
brew install kapsel

# 更新至最新版
brew upgrade kapsel
```

### Debian & Ubuntu: APT & DPKG (.deb)

Debian 及其衍生发行版（如 Ubuntu、Linux Mint、Deepin、UOS）可直接通过 `.deb` 包安装：

```bash
# 官方 GitHub 下载
curl -LO https://github.com/MrEiu/Kapsel/releases/latest/download/kapsel_amd64.deb

# 国内镜像加速下载:
curl -LO https://ghproxy.net/https://github.com/MrEiu/Kapsel/releases/latest/download/kapsel_amd64.deb

# 安装并自动补齐依赖
sudo dpkg -i kapsel_amd64.deb || sudo apt-get install -f -y
```

---

## 3. 💾 预编译免环境单文件绿色版 (Standalone Binaries)

如果您不想安装 Python、pip 或任何额外包管理器，可以直接从 [GitHub Releases](https://github.com/MrEiu/Kapsel/releases) 下载独立预编译包：

| 平台与架构 | 文件名 | GitHub 官方直链 | 国内极速加速镜像直链 |
| :--- | :--- | :--- | :--- |
| **Windows x86_64** | `kapsel-windows-x86_64.zip` | [下载](https://github.com/MrEiu/Kapsel/releases/latest/download/kapsel-windows-x86_64.zip) | [国内镜像下载](https://ghproxy.net/https://github.com/MrEiu/Kapsel/releases/latest/download/kapsel-windows-x86_64.zip) |
| **Linux x86_64** | `kapsel-linux-x86_64.tar.gz` | [下载](https://github.com/MrEiu/Kapsel/releases/latest/download/kapsel-linux-x86_64.tar.gz) | [国内镜像下载](https://ghproxy.net/https://github.com/MrEiu/Kapsel/releases/latest/download/kapsel-linux-x86_64.tar.gz) |
| **macOS (Universal)** | `kapsel-macos-universal.tar.gz` | [下载](https://github.com/MrEiu/Kapsel/releases/latest/download/kapsel-macos-universal.tar.gz) | [国内镜像下载](https://ghproxy.net/https://github.com/MrEiu/Kapsel/releases/latest/download/kapsel-macos-universal.tar.gz) |
| **Debian/Ubuntu** | `kapsel_amd64.deb` | [下载](https://github.com/MrEiu/Kapsel/releases/latest/download/kapsel_amd64.deb) | [国内镜像下载](https://ghproxy.net/https://github.com/MrEiu/Kapsel/releases/latest/download/kapsel_amd64.deb) |

### 放置与 PATH 配置方法：
1. 解压下载的压缩包，得到 `kapsel` 与 `kps`（Windows 为 `kapsel.exe` 与 `kps.exe`）；
2. 将它们移动至您系统的 PATH 目录：
   - **Windows**：建议放置在 `C:\Users\<你的用户名>\.kapsel\bin\`，并在“环境变量”中将该路径追加到用户 `Path`；
   - **Linux / macOS**：建议放置在 `~/.kapsel/bin/` 或 `/usr/local/bin/`，并执行 `chmod +x kapsel kps`。

---

## 4. 🌐 国际版全套工具链自动部署脚本 (Global Toolchain Installers)

国际通用极速单命令安装入口，全自动检测当前操作系统与已有环境状态：

```bash
# macOS & Linux (Bash / Zsh):
curl -fsSL https://raw.githubusercontent.com/MrEiu/Kapsel/master/scripts/install.sh | bash

# Windows (PowerShell):
irm https://raw.githubusercontent.com/MrEiu/Kapsel/master/scripts/install.ps1 | iex
```

### ✨ 特性亮点：
1. **智能环境预检与极速旁路 (Fast-Path)**：自动探测系统中已就绪的 Python 运行时、Kapsel CLI、Carapace 引擎、PATH 变量及插件，已满足条件的组件直接跳过，零重复耗时，秒级完成预检。
2. **多版本随心切换**：
   - **轻量版 (`--lite` / `-Lite`)**：Kapsel 核心 + Carapace 补全引擎（~20MB，极速初始化）。
   - **完全版 (`--full` / `-Full`，默认)**：轻量版 + 对应操作系统包管理器 + 逐一自动安装全部 11 个官方插件。
3. **跨 Shell 智能派发**：在 Windows Git Bash / MSYS 下运行 `install.sh` 亦会自动无缝唤起 PowerShell 引擎完成原生 Windows 安装。

---

## 5. 🛠️ 源码构建与开发者调试 (Build from Source)

如果您希望对 Kapsel 进行二次开发或编写自定义插件：

```bash
# 1. 克隆代码仓库
git clone https://github.com/MrEiu/Kapsel.git
cd Kapsel

# 2. 安装可编辑开发依赖
pip install -e .

# 3. 运行本地自动化测试验证
python -m pytest

# 4. 同步并生成双根补全规约树
kps completion sync
```

---

## 6. 🔍 安装后验证与常见问题排查 (Verification & Troubleshooting)

### 6.1 验证安装状态
在终端中依次运行以下指令验证部署成果：

```bash
# 查看版本信息
kapsel --version

# 查看核心与插件状态仪表盘
kapsel status

# 查看 Carapace 双根命令补全树
kps completion ls
```

### 6.2 常见问题与解决方案

#### Q1: 安装完成后提示 `kapsel: command not found` 或 `'kapsel' 不是内部或外部命令`？
- **原因**：安装目录未包含在系统的 `PATH` 环境变量中。
- **排查与解决**：
  - **Windows**：重新打开一个新的 PowerShell 窗口使全局 PATH 刷新。如果仍无效，检查 `~/.kapsel/bin` 或 Python Scripts 目录（如 `C:\Users\<用户名>\AppData\Local\Programs\Python\Python3xx\Scripts`）是否在用户 PATH 中。
  - **Linux / macOS**：在 `~/.bashrc` 或 `~/.zshrc` 末尾添加：
    ```bash
    export PATH="$HOME/.kapsel/bin:$PATH"
    ```
    然后执行 `source ~/.bashrc`（或 `source ~/.zshrc`）。

#### Q2: Windows PowerShell 提示脚本因为安全策略被阻止？
- **原因**：Windows 默认的 PowerShell 执行策略限制。
- **解决**：在当前终端会话执行以下指令临时放行，然后再运行安装脚本：
  ```powershell
  Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned -Force
  ```

#### Q3: Tab 键没有命令和参数补全？
- **原因**：Carapace 补全引擎二进制未就位或尚未同步规约。
- **解决**：在终端运行：
  ```bash
  kps completion sync
  ```
  Kapsel 会自动检查并引导下载 Carapace，重新生成毫秒级补全树。
