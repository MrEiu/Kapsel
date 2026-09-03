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

2. **单次快速命令转换 (`kps`)**：
   ```bash
   kps rm -rf dist/
   kps ls -la
   kps ps
   ```
   直接在您现有的任意 Shell（PowerShell、CMD、Bash）中调用 `kps`，即刻转换并执行。

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

## 📄 License

MIT License.
