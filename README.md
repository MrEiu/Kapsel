# Kapsel: Cross-Platform Intelligent Capsule Shell

<p align="center">
  <b>Wrap complexity, expose simplicity.</b><br>
  A modern, dual-state terminal enhancement wrapper and cross-platform developer capsule with dynamic multi-shell autocompletion.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-3776AB?style=flat&logo=python&logoColor=white" alt="Python 3.9+">
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-4D4D4D?style=flat&logo=linux" alt="Cross-Platform">
  <img src="https://img.shields.io/badge/Completion-Carapace%20Powered-00F0FF?style=flat" alt="Carapace Powered">
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat" alt="MIT License">
</p>

---

## Overview

**Kapsel** (German for *Capsule*) is a modern, lightweight, non-invasive command-line interface (CLI) wrapper and interactive terminal environment.

Operating on the philosophy of **"Wrap complexity, expose simplicity"**, Kapsel intercepts the terminal input stream without altering your host operating system's native configuration (no intrusive modifications to `.bashrc`, `config.fish`, or PowerShell profiles). Powered by an intelligent **Dual-State Engine** and **Carapace-backed dynamic autocompletion**, Kapsel provides an exceptionally uniform, elegant, and productive command-line workflow across Windows, macOS, and Linux.

---

## Key Features

### 1. Dual-State Execution Engine

Seamlessly toggle between two execution paradigms within a single prompt:

- **Native Mode (Quiet Terminal Booster)**:
  - **Zero-Friction Passthrough**: Executes system commands (`git`, `docker`, `npm`, `cargo`, `python`, `vim`) natively with 100% fidelity. Full compatibility with interactive applications and standard I/O redirection.
  - **Asynchronous Autosuggestions**: Predicts historical commands in subtle muted text behind the cursor using an isolated SQLite database; press `→` (Right Arrow) to accept immediately.
  - **Filesystem Path Completion**: Intelligent context-aware path completions when navigating directories or specifying file arguments.

- **Capsule Mode (`kapsel <cmd>` / `kps <cmd>`)**:
  - **Unified Command Pipeline**: Prefix any command with `kps ` or `kapsel ` to invoke the unified command subsystem.
  - **Cross-Platform Translation**: Translate universal commands into their best native shell equivalents (e.g. mapping `ll`, `rm -rf`, `cat` into PowerShell or CMD cmdlets).
  - **Zero Namespace Collision**: Subcommands and plugins live strictly inside the `kps` namespace.

---

### 2. Carapace-Powered Dynamic Autocompletion (1,000+ Commands)

Kapsel deeply integrates [Carapace](https://carapace.sh) as its primary multi-shell autocompletion engine:
- **Rich Context-Aware Completions**: Provides real-time completions for branches, tags, container names, images, volumes, packages, and CLI flags across 1,000+ CLI tools (`git`, `docker`, `kubectl`, `cargo`, `npm`, `pnpm`, `python`, etc.).
- **Automatic First-Run Bootstrapping**: Automatically detects and downloads the matching standalone official binary into `~/.kapsel/bin/` with zero administrative permissions required.

---

### 3. Dual Root Specification Architecture (`kps.yaml` & `kapsel.yaml`)

To prevent hijacking native host shell commands (such as PowerShell's `Get-Alias`, `Get-Help`, or Linux's `/usr/bin/install`), Kapsel introduces the **Dual Root Specification and Collision Sentinel** architecture:
- **Root Tree Aggregator**: Compiles all core built-in commands (`help`, `status`, `config`, `datadir`, `add`, `completion`, `toggle`, `language`) and enabled plugins into unified root completion trees:
  - `%APPDATA%/carapace/specs/kps.yaml`
  - `%APPDATA%/carapace/specs/kapsel.yaml`
- **Collision Sentinel**: Automatically intercepts and blocks commands that conflict with host shell reserved words (`alias`, `help`, `history`, `kill`, `install`, `profile`, `dir`, `ps`, etc.) from being exposed as top-level standalone specs.
- **Deep Multi-Level Completion**: Typing `kps alias add <Tab>` in any shell autocompletes multi-level flags (`--from`, `--to`, `--shell`, `--global`) and subcommands with zero pollution to host shell commands!

---

### 4. Modular Plugin Ecosystem

Kapsel features an extensible, crash-proof plugin architecture with 11 official plugins:

| Plugin | Command | Backed Tool | Description |
| :--- | :--- | :--- | :--- |
| **`init`** | `kps init` | **`mise`** | Multi-language project development environment & runtime version manager. |
| **`portal`** | `kps portal` / `z <query>` | **`zoxide`** | Frecency-based intelligent directory teleportation and workspace navigation. |
| **`shore`** | `kps shore` | **`chsrc`** | Fast intelligent mirror source switcher (PyPI, Rust, Node, Go, OS mirrors). |
| **`install`** | `kps install` | **`mpm`** | Universal cross-platform package installer unifying 20+ package managers. |
| **`alias`** | `kps alias` | *Pure Python* | Cross-platform command alias translation and shell mapping engine. |
| **`ai`** | `kps ai` | **`aichat`** | Terminal AI assistant with multi-model dialogue and code generation. |
| **`autopilot`** | `kps autopilot` | **`pueue`** | Autonomous background task queue and daemon execution manager. |
| **`fuck`** | `kps fuck` | **`thefuck`** | Intelligent terminal error correction and command auto-fixing. |
| **`help`** | `kps help <cmd>` | **`tealdeer`** | Fast practical command cheat sheets and quick lookup (tldr). |
| **`profile`** | `kps profile` | **`chezmoi`** | Cross-platform dotfile and terminal configuration manager. |
| **`rec`** | `kps rec` | **`pet`** | Interactive command snippet recorder, manager, and runner. |

---

### 5. Minimalist Boxed Terminal Aesthetics

- **Boxed Card Framing**: Encapsulates command input, duration, and output inside a visually distinct card (`╭─ ❯` and `╰─`).
- **Execution Feedback**: Displays exit status (`✔ 0` or `✘ exit 1`) and precise elapsed execution time (`⏱ 42ms`).
- **Internationalization (i18n)**: Out-of-the-box multilingual support across 7 languages (`en`, `zh_CN`, `ja`, `es`, `fr`, `de`, `ru`).

---

## Installation

### Method 1: Standard Python Package (Recommended)

```bash
# Isolated installation via pipx (recommended)
pipx install kapsel-cli

# Or install via standard pip
pip install --upgrade kapsel-cli
```

### Method 2: All-in-One Toolchain Installers

Kapsel provides official automated scripts that install all required binary tools (`carapace`, `zoxide`, `mise`, `chsrc`, `aichat`, `pueue`, `chezmoi`, `pet`, `tealdeer`, `fzf`) and configure your environment:

- **Windows (PowerShell)**:
  ```powershell
  pwsh -ExecutionPolicy Bypass -File scripts/install_tools_windows.ps1
  ```

- **macOS**:
  ```bash
  bash scripts/install_tools_macos.sh
  ```

- **Linux (Ubuntu / Debian / Arch / Fedora)**:
  ```bash
  bash scripts/install_tools_linux.sh
  ```

- **Cross-Platform Dispatcher**:
  ```bash
  python scripts/install_all.py
  ```

### Method 3: Fast-Track for Users in China (国内一键高速激活)

Pre-configured with high-speed domestic mirror proxies (Tsinghua PyPI, Gitee Scoop, npmmirror, GitHub Releases accelerator):

- **Windows**:
  ```powershell
  irm https://ghproxy.net/https://raw.githubusercontent.com/MrEiu/Kapsel/master/scripts/install_cn.ps1 | iex
  ```

- **Linux / macOS**:
  ```bash
  curl -fsSL https://ghproxy.net/https://raw.githubusercontent.com/MrEiu/Kapsel/master/scripts/install_cn.sh | bash
  ```

---

## Quick Start

### 1. Launch Interactive Capsule Shell

```bash
kapsel
# Or use the quick alias
kps
```

### 2. Run Single Command Translation

You can also use `kps` directly from your standard shell without entering interactive mode:

```bash
# Execute plugin commands
kps status
kps portal ls
kps shore get
kps completion ls

# One-shot command mapping
kps rm -rf dist/
kps ls -la
```

---

## Built-in Commands Reference

| Command | Aliases | Description |
| :--- | :--- | :--- |
| `help` | `?`, `kps help` | Display Kapsel manual, interaction mechanisms, and command cheatsheet |
| `status` | `info`, `kps status` | Inspect OS environment, active host shell, Git branch, and sandbox status |
| `config` | `kps config` | View or modify core configuration (`~/.kapsel/config.yaml`) |
| `config path` | - | Print absolute physical path of `config.yaml` |
| `config edit` | - | Open `config.yaml` in the system default text editor |
| `config set <k> <v>` | - | Update a configuration key-value pair from command line |
| `config reload` | - | Hot-reload configuration without restarting the session |
| `completion` | `kps completion` | Inspect and synchronize declarative Carapace completion specifications |
| `completion ls` | - | Display active completion specs table (Scope, Source, Status) |
| `completion sync` | - | Force compile and sync dual root specs (`kps.yaml` and `kapsel.yaml`) |
| `completion new <name>`| - | Scaffold a new user declarative specification template |
| `datadir` | `kps datadir` | Inspect or safely relocate data storage sandbox directory |
| `language` | `kps language` | Switch active UI language (`en`, `zh_CN`, `ja`, `es`, `fr`, `de`, `ru`) |
| `toggle` | `kps toggle` | Toggle Kapsel default shell mode (open on first call, exit on second) |
| `clear` | `cls` | Clear terminal screen and re-render header banner |
| `exit` | `quit` | Cleanly exit Kapsel and return to native host shell |

---

## Directory Structure & Sandboxing

Kapsel stores all user data in a dedicated sandbox directory (`~/.kapsel/`):

```text
~/.kapsel/
├── config.yaml          # Core configuration (UI themes, card styles, language)
├── history.db           # Persistent SQLite database storing command history and stats
├── bin/                 # Standalone binary tools (carapace, zoxide, mise, chsrc...)
├── specs/               # User custom declarative autocompletion specifications
├── plugins/             # Installed official and third-party plugin packages
└── logs/                # Session logs and crash diagnostics
```

---

## License

This project is open-source software licensed under the [MIT License](LICENSE).
