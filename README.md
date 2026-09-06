<div align="center">

# ⚡ Kapsel

**A cross-platform terminal environment that wraps your shell with unified commands, context-aware autocompletion, and zero global pollution.**

[![PyPI Version](https://img.shields.io/pypi/v/kapsel-cli?color=3776AB&logo=pypi&logoColor=white&style=flat-square)](https://pypi.org/project/kapsel-cli/)
[![Python Version](https://img.shields.io/badge/Python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-3776AB.svg?style=flat-square&logo=python&logoColor=white)](https://pypi.org/project/kapsel-cli/)
[![Platform Support](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-4D4D4D.svg?style=flat-square&logo=linux&logoColor=white)](https://github.com/MrEiu/Kapsel)
[![License](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](LICENSE)

[Why Kapsel?](#-why-kapsel) •
[Features](#-features) •
[Quick Start](#-quick-start) •
[Built-in Plugins](#-built-in-plugins) •
[Installation](#-installation) •
[Architecture](#-architecture--sandboxing) •
[简体中文](README_zh.md)
[日本語](README_ja.md)
[Русский](README_ru.md)
[Polski](README_pl.md)
[Español](README_es.md)
[Français](README_fr.md)

</div>

---

### 📺 Interactive Capsule in Action

```text
╭─ kapsel [pwsh] ~/Projects/Kapsel 14:32:05
╰─ ❯ git checkout -b feature/dynamic-specs
✔ 0  git checkout -b feature/dynamic-specs  ⏱ 24ms
```

> **Wrap complexity, expose simplicity.**
> Run your native shell executables as usual, while enjoying automatic command translation, inline suggestions, rich completion specs, and a modular toolchain—all sandboxed within `~/.kapsel/`.

---

## 💡 Why Kapsel?

Switching between operating systems often leads to broken muscle memory, cluttered dotfiles, and fractured autocompletion setups. Kapsel bridges this gap with a non-invasive capsule layer:

| Challenge | Traditional Shell Setup | With Kapsel |
| :--- | :--- | :--- |
| **Cross-Platform Friction** | Fractured commands across OS (`dir` vs `ls`, `rmdir` vs `rm -rf`) | Unified Linux-first command layer across Windows, macOS, and Linux |
| **Shell Profile Pollution** | Bloated `.bashrc` or `$PROFILE` with fragile global scripts | 100% self-contained sandbox in `~/.kapsel/` (zero global mutation) |
| **Autocompletion Setup** | Manual setup per shell, often incomplete or slow | Instant context-aware completions for 1,000+ CLI tools via Carapace |
| **Toolchain & Sync Sprawl** | Disjointed tools requiring repetitive manual installation | Integrated `kps` plugins for runtimes, mirrors, directory jumping, and sync |

---

## ✨ Features

- **🌐 Cross-Platform Command Consistency**: Type standard commands (`ls -la`, `cat`, `rm -rf`, `grep`) naturally in any terminal, automatically translated to host-native primitives without hijacking host built-ins.
- **⚡ Context-Aware Autocompletion**: Integrated with [Carapace](https://carapace.sh) to deliver multi-level argument and context completions (Git branches, Docker images, npm scripts) across PowerShell, Bash, and Zsh.
- **🛡️ Zero-Pollution Sandboxing**: Everything (binaries, SQLite history, declarative specs, plugins, and logs) resides inside `~/.kapsel/`. Your host shell configuration files remain completely untouched.
- **🧩 Curated Plugin Ecosystem**: Access powerful developer utilities (`zoxide`, `mise`, `chsrc`, `pueue`, AI assistants) directly through the unified `kps` command.
- **🎨 Modern Card-Framed Aesthetics**: Clean visual command card framing with exit code badges (`✔ 0` / `✘ 1`), execution stopwatch timing, and native i18n support across 7 languages.

---

## 🚀 Quick Start

Launch the interactive capsule shell:

```bash
kapsel
```

Inside Kapsel, commands run natively with enhanced feedback:

```bash
# 1. Native pass-through with timing & exit code card
git status
docker ps

# 2. Universal command translation on any OS
rm -rf ./temp_dir
cat package.json

# 3. Use built-in plugins anytime
kps portal work        # Jump to directory (zoxide)
kps ai "explain git rebase"  # Ask terminal AI assistant
kps shore get          # Auto-select fastest package mirrors

# 4. Inspect capsule state
kps status
```

> **One-Shot Execution**: You can also invoke Kapsel tools directly from your regular shell using `kps <command>` (e.g. `kps portal`, `kps status`, `kps ai`).

---

## 🧩 Built-in Plugins

Kapsel comes pre-configured with 11 decoupled, official plugins under the `kps` namespace:

| Plugin | Command | What It Does | Powered by |
| :--- | :--- | :--- | :--- |
| **`portal`** | `kps portal` / `z` | Fast directory jumping with frecency weighting | [zoxide](https://github.com/ajeetdsouza/zoxide) |
| **`ai`** | `kps ai` | Terminal AI copilot for generating and explaining commands | OpenAI / Claude / Ollama |
| **`init`** | `kps init` | Multi-language toolchain runtime manager (Node, Python, Go, Rust) | [mise](https://github.com/jdx/mise) |
| **`shore`** | `kps shore` | Benchmark and switch fastest package & OS download mirrors | [chsrc](https://github.com/AkihiroSuda/chsrc) |
| **`install`** | `kps install` | Universal software installer aggregating 20+ package managers | [mpm](https://github.com/MrEiu/mpm) |
| **`alias`** | `kps alias` | Cross-platform alias translation with zero namespace collision | Native Engine |
| **`autopilot`**| `kps autopilot`| Background queue & autonomous daemon task runner | [pueue](https://github.com/Nukesor/pueue) |
| **`help`** | `kps help <cmd>`| Instant, community-driven practical command cheat sheets | [tealdeer](https://github.com/dbrgn/tealdeer) |
| **`fuck`** | `kps fuck` | Intelligent autocorrect and syntax fix for mistyped commands | [thefuck](https://github.com/nvbn/thefuck) |
| **`profile`** | `kps profile` | Cross-platform dotfile and workstation configuration sync | [chezmoi](https://github.com/twpayne/chezmoi) |
| **`rec`** | `kps rec` | Interactive CLI command snippet bookmarking & runner | [pet](https://github.com/knqyf263/pet) |

---

## 📦 Installation

### Recommended (pipx / pip)

```bash
# Isolated installation via pipx (recommended)
pipx install kapsel-cli

# Or standard pip
pip install --upgrade kapsel-cli
```

### One-Line Automated Installers

Quick bootstrap scripts that auto-detect your OS and configure completions:

```bash
# macOS & Linux:
curl -fsSL https://raw.githubusercontent.com/MrEiu/Kapsel/master/scripts/install.sh | bash

# Windows (PowerShell):
irm https://raw.githubusercontent.com/MrEiu/Kapsel/master/scripts/install.ps1 | iex
```

### Other Installation Options

- **Standalone Precompiled Binaries**: Download ready-to-run releases from [GitHub Releases](https://github.com/MrEiu/Kapsel/releases/latest).
- **Package Managers**: Available on Scoop (`scoop install kapsel`), Homebrew, and Debian/Ubuntu `.deb`.
- **Build from Source**: `git clone https://github.com/MrEiu/Kapsel.git && cd Kapsel && pip install -e .`

👉 *For China mirror acceleration and full platform package manager details, see **[docs/INSTALLATION.md](docs/INSTALLATION.md)**.*

---

## ⚙️ Configuration

Kapsel stores its configuration in `~/.kapsel/config.yaml`. Manage settings directly from your terminal:

```bash
# View configuration dashboard
kps config

# Open configuration file in external editor
kps config edit

# Adjust settings on the fly
kps config set ui.enable_banner false
kps config set interaction.autosuggest_sensitivity 0.2
```

---

## 🏛️ Architecture & Sandboxing

Kapsel follows a **Zero-Pollution Principle**. All runtime state is strictly contained:

```text
~/.kapsel/
├── config.yaml          # System-wide UI configuration, themes, and interaction settings
├── history.db           # Persistent SQLite database storing command history and stats
├── bin/                 # User-space standalone binary tools (carapace, zoxide, mise...)
├── specs/               # Declarative autocompletion YAML specifications
├── plugins/             # Installed official and community plugin extensions
└── logs/                # Diagnostic logs and session metrics
```

- **Dual-State Engine**: Native executables run directly via host subshell passthrough; capsule utilities run via the unified `kps` registry.
- **Collision Sentinel**: Ensures native shell built-ins (e.g. PowerShell's `Get-Alias`, `Get-Help`) are never intercepted or hijacked.
- **Isolated Plugins**: Plugins run independently, ensuring third-party extensions cannot crash the core shell.

---

## 🧪 Development & Testing

```bash
# Clone the repository
git clone https://github.com/MrEiu/Kapsel.git
cd Kapsel

# Install editable package with test dependencies
pip install -e ".[test]"

# Run unit test suite
pytest tests/ -v
```

---

## 📄 License

Distributed under the **[MIT License](LICENSE)**. Built by MrEiu and open-source contributors.
