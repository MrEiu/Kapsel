<div align="center">

# ⚡ Kapsel

**Next-Generation Intelligent Terminal Capsule & Cross-Platform Ergonomic Shell Multiplexer**

[![Python Version](https://img.shields.io/badge/Python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-3776AB.svg?style=flat-square&logo=python&logoColor=white)](https://pypi.org/project/kapsel-cli/)
[![Platform Support](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-4D4D4D.svg?style=flat-square&logo=linux&logoColor=white)](https://github.com/MrEiu/Kapsel)
[![License](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](LICENSE)

<p align="center">
  <i>"Wrap complexity, expose simplicity."</i><br>
  A zero-pollution, context-aware command abstraction layer and high-performance interactive capsule environment.<br>
  Empowering consistent developer workflows across Windows PowerShell, macOS Zsh, and Linux Bash.
</p>

---

[Key Features](#-key-features) •
[Quick Installation](#-quick-installation) •
[Architecture](#-architecture--philosophy) •
[Plugin Ecosystem](#-official-plugin-ecosystem) •
[Comparison](#-feature-matrix--comparison) •
[Cheatsheet](#-commands-reference)

---

</div>

```text
╭─ kapsel [pwsh] ~/Projects/Kapsel 14:32:05
╰─ ❯ git checkout -b feature/dynamic-specs
✔ 0  git checkout -b feature/dynamic-specs  ⏱ 24ms
```

---

## 🌟 Overview

Developers daily oscillate between disparate operating systems, suffering from fragmented terminal ergonomics:
- Muscle memory collisions (`rm -rf` vs `Remove-Item`, `cat` vs `type`, `ls -la` vs `dir /a`);
- Fragile global dotfiles polluting `.bashrc`, `config.fish`, or `$PROFILE`;
- Inconsistent autocompletion engines across shells.

**Kapsel** solves this by introducing a **non-invasive, sandboxed terminal capsule**. It operates as an ergonomic execution layer that intercepts and enhances command-line interactions with **zero global system pollution**—delivering sub-millisecond asynchronous autocompletion, Linux-first universal mapping, and automated environment isolation.

---

## 🚀 Key Features

### 1. Dual-State Execution Multiplexer
- **Native Execution Layer (Default Mode)**:
  Direct, zero-overhead passthrough for all system executables (`git`, `docker`, `npm`, `cargo`, `python`, `vim`). Retains full TTY interaction, real-time signal handling, and standard stream piping.
- **Unified Capsule Pipeline (`kps <cmd>` / `kapsel <cmd>`)**:
  A single entry point for universal commands, plugin utilities, and system configurations. Strips execution prefixes and translates cross-platform commands into host-optimized primitives on the fly.
- **Asynchronous Deep Autosuggestions**:
  Muted inline history prediction powered by a persistent, isolated SQLite statistical store (`~/.kapsel/history.db`). Accept suggestions instantaneously with `→` (Right Arrow).

### 2. Multi-Shell Dynamic Autocompletion (Carapace Powered)
- **1,000+ Command Coverage**:
  Direct integration with [Carapace](https://carapace.sh) enables multi-shell, multi-level argument and context completion (git branches/tags, docker containers/images, kubectl pods, npm scripts).
- **Zero-Setup Bootstrapping**:
  On first launch, Kapsel silently bootstraps the official platform binary into `~/.kapsel/bin/` with **zero administrative/root permissions**.

### 3. Dual Root Specification & Collision Sentinel
- **Namespaced Root Trees (`kps.yaml` & `kapsel.yaml`)**:
  Dynamically compiles core built-ins and plugin specifications into isolated root trees under `kps` and `kapsel`. 
- **Host Namespace Collision Sentinel**:
  Strictly guards host shell built-ins (`alias`, `help`, `install`, `history`, `profile`, `ps`, `kill`, `dir`). Commands with potential host collisions are sealed within the `kps` namespace—**guaranteeing native shell commands (e.g. PowerShell's `Get-Alias`) remain 100% unhijacked**.
- **Deep Parameter Completions**:
  Typing `kps alias add <Tab>` delivers rich multi-level flag completion (`--from`, `--to`, `--shell`, `--global`) in any terminal.

### 4. Modular, Crash-Proof Plugin Subsystem
- **Decoupled Architecture**: Plugins operate in isolated memory boundaries. A malfunctioning plugin can never crash Kapsel Core.
- **Declarative Spec Standard**: Every plugin defines independent declarative YAML specifications adhering to Carapace specifications.

### 5. Minimalist Boxed Terminal Aesthetics
- **Card Framing**: Clear visual demarcation of command inputs and outputs using modern boxed framing (`╭─ ❯` and `╰─`).
- **Telemetry Feedback**: Instantaneous display of execution exit codes (`✔ 0` or `✘ exit 1`) and precise wall-clock elapsed time (`⏱ 38ms`).
- **Native Multilingual Engine (i18n)**: Full localization across 7 languages (`en`, `zh_CN`, `ja`, `es`, `fr`, `de`, `ru`).

---

## ⚡ Quick Installation

### Option A: Universal Python Package (Global / Isolated)

```bash
# Recommended: Isolated installation via pipx
pipx install kapsel-cli

# Or standard pip installation
pip install --upgrade kapsel-cli
```

### Option B: One-Liner Toolchain Installers

Automatically downloads, verifies, and installs all required binary tools (`carapace`, `zoxide`, `mise`, `chsrc`, `aichat`, `pueue`, `chezmoi`, `pet`, `tealdeer`, `fzf`) into user space:

<table>
<tr>
<th>Platform</th>
<th>One-Line Installation Command</th>
</tr>
<tr>
<td><b>Windows (PowerShell)</b></td>
<td>

```powershell
irm https://raw.githubusercontent.com/MrEiu/Kapsel/master/scripts/install_tools_windows.ps1 | iex
```

</td>
</tr>
<tr>
<td><b>macOS (Homebrew)</b></td>
<td>

```bash
curl -fsSL https://raw.githubusercontent.com/MrEiu/Kapsel/master/scripts/install_tools_macos.sh | bash
```

</td>
</tr>
<tr>
<td><b>Linux (All Distros)</b></td>
<td>

```bash
curl -fsSL https://raw.githubusercontent.com/MrEiu/Kapsel/master/scripts/install_tools_linux.sh | bash
```

</td>
</tr>
<tr>
<td><b>China Fast-Track (国内极速镜像)</b></td>
<td>

```powershell
# Windows:
irm https://ghproxy.net/https://raw.githubusercontent.com/MrEiu/Kapsel/master/scripts/install_cn.ps1 | iex

# Linux / macOS:
curl -fsSL https://ghproxy.net/https://raw.githubusercontent.com/MrEiu/Kapsel/master/scripts/install_cn.sh | bash
```

</td>
</tr>
</table>

---

## 🧩 Official Plugin Ecosystem

Kapsel maintains a modular, decoupled plugin suite designed to satisfy modern engineering workflows:

| Plugin | Command | Core Technology | Description |
| :--- | :--- | :--- | :--- |
| **`init`** | `kps init` | **`mise`** (Rust) | Project toolchains & polyglot runtime manager (replaces nvm, pyenv, rbenv). |
| **`portal`** | `kps portal` / `z` | **`zoxide`** (Rust) | Frecency-weighted directory teleportation with fuzzy navigation. |
| **`shore`** | `kps shore` | **`chsrc`** (C) | Automated ultra-fast mirror switcher (PyPI, Rust, Node, Go, OS mirrors). |
| **`install`** | `kps install` | **`mpm`** (Python) | Unified CLI package manager aggregating 20+ package managers. |
| **`alias`** | `kps alias` | *Native Engine* | Universal command alias translation and multi-terminal cross-mapping. |
| **`ai`** | `kps ai` | **`aichat`** (Rust) | Terminal AI copilot supporting OpenAI, Claude, Gemini, DeepSeek, and Ollama. |
| **`autopilot`**| `kps autopilot`| **`pueue`** (Rust) | Autonomous background task queue and long-running daemon execution manager. |
| **`fuck`** | `kps fuck` | **`thefuck`** (Python) | Intelligent terminal input error correction and automated syntax fixing. |
| **`help`** | `kps help <cmd>`| **`tealdeer`** (Rust) | Instantaneous practical command cheat sheets and quick lookup (tldr). |
| **`profile`** | `kps profile` | **`chezmoi`** (Go) | Cross-platform dotfiles, shell profiles, and secret-encrypted environment manager. |
| **`rec`** | `kps rec` | **`pet`** (Go) | Interactive CLI snippet recorder, argument parameterizer, and runner. |

---

## 📊 Feature Matrix & Comparison

| Feature Capability | Kapsel | Standard Shells (Bash/Zsh/Pwsh) | Starship | Oh-My-Zsh |
| :--- | :---: | :---: | :---: | :---: |
| **Non-invasive Runtime (Zero Profile Mutation)** | **Yes** | No | No | No |
| **1,000+ Command Context Completion (Carapace)** | **Yes** | Manual plugins | No (Prompt only) | Partial (Slow) |
| **Cross-Platform Linux-First Mapping (`kps`)** | **Yes** | No | No | No |
| **Dual Root Spec Architecture (Anti-Collision)** | **Yes** | No | No | No |
| **Boxed Terminal Execution Framing** | **Yes** | No | Prompt only | No |
| **Isolated Sandbox State (`~/.kapsel/`)** | **Yes** | Fragmented | No | Fragmented |
| **Sub-Millisecond Async UI Response** | **Yes** | Depends | Yes | Often Slow |

---

## 📖 Commands Reference

### Interactive Shell Mode (`kapsel` / `kps`)

Launch Kapsel as an interactive shell session:
```bash
kapsel
```

Within the capsule session, the following unified commands are available:

```text
help                   Display Kapsel manual, interaction mechanisms, and command cheat sheet
status                 Inspect OS environment, active host shell, Git branch, and sandbox status
upgrade [plugin]       Two-stage upgrade check for Kapsel Core and official plugins with changelogs
search [-a]            Search and discover official plugins with versions and install states
enable <plugin>        Activate and enable an installed plugin, syncing autocompletions
disable <plugin>       Disable an active plugin without deleting local files
config                 Inspect or edit core configuration (~/.kapsel/config.yaml)
  config path          Print physical configuration file path
  config edit          Open configuration in default external editor
  config get <key>     Retrieve value for a configuration key
  config set <k> <v>   Update configuration value from terminal
  config reload        Hot-reload configuration from disk without session restart
completion             Manage, inspect, and synchronize declarative Carapace specifications
  completion ls        List active completion specifications, scopes, and mount states
  completion sync      Force compile and synchronize dual root specs (kps.yaml and kapsel.yaml)
  completion new <cmd> Scaffold a new declarative specification template
  completion path      Display active spec directories
datadir                Inspect or safely relocate data storage sandbox directory
language <lang>        Switch active UI language (en, zh_CN, ja, es, fr, de, ru)
toggle                 Toggle Kapsel default terminal mode (open on first call, close on second)
clear                  Clear terminal screen and re-render header banner
exit                   Cleanly exit Kapsel and return to native host shell
```

### One-Shot External Execution

Execute any capsule or plugin command directly from your standard shell:

```bash
# Management & Diagnostics
kps status
kps completion ls
kps config edit

# Plugin commands
kps portal ls
kps shore get
kps init use node@22

# Cross-platform mapped commands
kps rm -rf dist/
kps ls -la
```

---

## 🔒 Directory Sandboxing & State Model

Kapsel adheres strictly to the **Zero-Pollution Guarantee**. All data, binaries, caches, and logs reside exclusively within the user sandbox directory:

```text
~/.kapsel/
├── config.yaml          # System-wide UI configuration (colors, card borders, language)
├── history.db           # Persistent SQLite database storing command history and stats
├── bin/                 # User-space standalone binary tools (carapace, zoxide, mise, chsrc...)
├── specs/               # User custom declarative autocompletion specifications
├── plugins/             # Installed official and community plugin packages
└── logs/                # Session logs and crash diagnostics
```

---

## 🧪 Testing & Quality Assurance

The Kapsel codebase enforces thorough test coverage with strict type checks and isolated fixtures:

```bash
# Clone the repository
git clone https://github.com/MrEiu/Kapsel.git
cd Kapsel

# Install test dependencies
pip install -e ".[test]"

# Run full test suite
pytest tests/ -v
```

All 79 automated unit tests validate spec manager discovery, collision sentinel blocking, carapace integration, plugin lifecycles, and i18n resolution.

---

## 🤝 Contributing & Community

Contributions are welcome!
- Check out [issues](https://github.com/MrEiu/Kapsel/issues) to find tasks or report bugs.
- For developing or submitting plugins, refer to the [Plugins Guide](https://github.com/MrEiu/plugins).

---

## 📄 License

Kapsel is open-source software licensed under the **[MIT License](LICENSE)**.

<div align="center">
  <sub>Built with modern terminal ergonomics by MrEiu and the Kapsel Open-Source Team.</sub>
</div>
