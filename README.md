<div align="center">

# ⚡ Kapsel

**A cross-platform terminal capsule for a cleaner, more consistent command-line experience.**

[![PyPI Version](https://img.shields.io/pypi/v/kapsel-cli?color=3776AB&logo=pypi&logoColor=white&style=flat-square)](https://pypi.org/project/kapsel-cli/)
[![Python Version](https://img.shields.io/badge/Python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-3776AB.svg?style=flat-square&logo=python&logoColor=white)](https://pypi.org/project/kapsel-cli/)
[![Platform Support](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-4D4D4D.svg?style=flat-square&logo=linux&logoColor=white)](https://github.com/MrEiu/Kapsel)
[![License](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](LICENSE)

[Quick Start](#-quick-start) ·
[Features](#-features) ·
[Plugins](#-plugin-ecosystem) ·
[Installation](#-installation) ·
[Architecture](#-architecture) ·
[Documentation](#-documentation)

[🇨🇳 简体中文](README_zh.md) ·
[🇯🇵 日本語](README_ja.md) ·
[🇷🇺 Русский](README_ru.md) ·
[🇩🇪 Deutsch](README_de.md) ·
[🇪🇸 Español](README_es.md) ·
[🇫🇷 Français](README_fr.md) ·
[🇵🇱 Polski](README_pl.md)

</div>

---

## 📺 Kapsel in Action

```text
╭─ kapsel [pwsh] ~/Projects/Kapsel 14:32:05
╰─ ❯ git checkout -b feature/dynamic-specs
✔ 0  git checkout -b feature/dynamic-specs  ⏱ 24ms
```

> **Wrap complexity, expose simplicity.**
>
> Keep using your native shell and system executables as usual, while Kapsel
> adds a unified command layer, context-aware completion, inline suggestions,
> and an extensible plugin environment — all contained inside `~/.kapsel/`.

---

## 💡 Why Kapsel?

Terminal workflows are still heavily shaped by the host operating system and
the shell being used.

The same everyday task may require different commands on Windows, macOS, and
Linux. Shell configuration is fragmented across files such as `.bashrc`,
`.zshrc`, and PowerShell profiles, while completion systems and developer
utilities often need to be installed and configured independently.

Kapsel adds a non-invasive capsule layer around your existing terminal:

| Problem | Traditional Setup | Kapsel |
| :--- | :--- | :--- |
| **Cross-platform commands** | Different commands and syntax across operating systems | Linux-first unified command layer |
| **Shell configuration** | Global profile files and shell-specific scripts | Self-contained state under `~/.kapsel/` |
| **Completion** | Separate setup for each shell and tool | Context-aware completion through Carapace |
| **Developer utilities** | Multiple unrelated tools with different configuration | Unified plugin environment under `kps` |
| **Extensibility** | Shell-specific integrations | Isolated plugin architecture |

Kapsel does not replace your shell or your system executables. It sits beside
them and provides an additional, consistent execution environment.

---

## ✨ Features

### 🌐 Native & Cross-Platform Execution

Use your normal system commands directly:

```bash
git
docker
python
npm
cargo
vim
```

At the same time, Kapsel provides a Linux-first command layer for common
cross-platform operations:

```bash
ls -la
cat package.json
rm -rf ./dist
grep -r "TODO" .
```

Native shell built-ins remain protected from accidental interception.

---

### ⚡ Context-Aware Autocompletion

Kapsel integrates with [Carapace](https://carapace.sh) for rich,
multi-level command completion.

Completion can understand commands, arguments, flags, and context such as:

- Git branches and tags
- Docker containers and images
- Kubernetes resources
- npm scripts
- Other supported CLI specifications

Completion specifications are managed declaratively and can be extended
through plugins or custom specifications.

---

### 💡 Inline Command Suggestions

Kapsel maintains a local SQLite history store and provides asynchronous
history-based suggestions while you type.

Press `→` to accept a suggestion.

History and related runtime state remain inside the Kapsel sandbox.

---

### 🛡️ Zero-Pollution Environment

Kapsel keeps its own configuration, binaries, history, completion
specifications, plugins, and logs under:

```text
~/.kapsel/
```

It is designed to avoid modifying your existing shell configuration files,
including:

```text
.bashrc
.zshrc
config.fish
PowerShell profiles
```

Your host shell remains yours.

---

### 🧩 Modular Plugin Architecture

Kapsel provides a plugin runtime under the `kps` namespace.

Plugins can add commands, integrations, workflows, completion specifications,
and external developer tools without becoming part of the Kapsel core.

Official plugins and community plugins share the same extensible architecture.

---

### 🎨 Interactive Terminal Experience

The interactive capsule provides a compact command presentation with:

```text
╭─ ...
╰─ ❯ ...
✔ 0  ...  ⏱ 24ms
```

Execution status and elapsed time are shown directly after commands, while
the interface can be localized across multiple languages.

---

# 🚀 Quick Start

## 1. Install

The recommended installation method is:

```bash
pipx install kapsel-cli
```

Or:

```bash
pip install --upgrade kapsel-cli
```

## 2. Start Kapsel

```bash
kapsel
```

You can now use your terminal normally:

```bash
git status
docker ps
python --version
```

And use Kapsel's cross-platform command layer when needed:

```bash
ls -la
cat package.json
rm -rf ./temp
```

## 3. Use Kapsel Commands

Kapsel utilities are available through `kps`:

```bash
kps status
kps config
kps portal
kps ai
```

For example:

```bash
kps portal work
kps ai "explain git rebase"
kps shore get
```

## 4. One-Shot Execution

You do not need to enter the interactive capsule to use Kapsel.

From your existing shell:

```bash
kps status
kps portal
kps ai "find large files"
```

This makes `kps` suitable for scripts, aliases, shell workflows, and
individual commands.

---

# 🧩 Plugin Ecosystem

Kapsel is designed as a plugin-oriented terminal environment rather than a
fixed collection of built-in commands.

The ecosystem is divided into **official plugins** and **community plugins**.

## Official Plugins

Kapsel currently provides the following official plugins:

| Plugin | Command | Description | Powered by |
| :--- | :--- | :--- | :--- |
| **`portal`** | `kps portal` / `z` | Fast directory navigation with frecency-based selection | [zoxide](https://github.com/ajeetdsouza/zoxide) |
| **`ai`** | `kps ai` | Terminal AI assistant for generating, explaining, and working with commands | OpenAI / Claude / Ollama |
| **`init`** | `kps init` | Runtime and toolchain management for Node, Python, Go, Rust, and more | [mise](https://github.com/jdx/mise) |
| **`shore`** | `kps shore` | Package and OS mirror detection and switching | [chsrc](https://github.com/AkihiroSuda/chsrc) |
| **`install`** | `kps install` | Unified software installation across multiple package managers | [mpm](https://github.com/MrEiu/mpm) |
| **`alias`** | `kps alias` | Cross-platform command alias translation | Native Engine |
| **`autopilot`** | `kps autopilot` | Background task queues and long-running jobs | [pueue](https://github.com/Nukesor/pueue) |
| **`help`** | `kps help <cmd>` | Practical command documentation and cheat sheets | [tealdeer](https://github.com/dbrgn/tealdeer) |
| **`fuck`** | `kps fuck` | Automatic command correction and syntax fixing | [thefuck](https://github.com/nvbn/thefuck) |
| **`profile`** | `kps profile` | Dotfile and workstation configuration management | [chezmoi](https://github.com/twpayne/chezmoi) |
| **`rec`** | `kps rec` | CLI snippet bookmarking, parameterization, and execution | [pet](https://github.com/knqyf263/pet) |

Official plugins are maintained as separate components so that the core
runtime can remain small and focused.

---

## 🌍 Community Plugins

Kapsel is intended to grow beyond the official plugin collection.

Community developers can create plugins that extend Kapsel with:

- New commands
- External tools
- Developer workflows
- Service integrations
- Custom completion specifications
- Automation utilities

Community submissions can be contributed through the
**[Kapsel Plugin Repository](https://github.com/MrEiu/plugins)**.

See the plugin documentation for development requirements, specifications,
and contribution guidelines.

> The official plugin collection is curated by the Kapsel maintainers.
> Community plugins are developed and maintained by their respective
> contributors.

---

# 📦 Installation

## Recommended

### pipx

```bash
pipx install kapsel-cli
```

### pip

```bash
pip install --upgrade kapsel-cli
```

---

## One-Line Automated Installers

### macOS & Linux

```bash
curl -fsSL https://raw.githubusercontent.com/MrEiu/Kapsel/master/scripts/install.sh | bash
```

### Windows PowerShell

```powershell
irm https://raw.githubusercontent.com/MrEiu/Kapsel/master/scripts/install.ps1 | iex
```

The installers detect the host platform and configure Kapsel and its
completion environment automatically.

---

## Standalone Binaries

Precompiled releases are available for platforms that do not use Python:

| Platform / Architecture | Release Artifact |
| :--- | :--- |
| **Windows x86_64** | `kapsel-windows-x86_64.zip` |
| **Linux x86_64** | `kapsel-linux-x86_64.tar.gz` |
| **macOS Universal** | `kapsel-macos-universal.tar.gz` |
| **Debian / Ubuntu** | `kapsel_amd64.deb` |

See **[GitHub Releases](https://github.com/MrEiu/Kapsel/releases/latest)** for
the latest artifacts.

---

## Package Managers

Kapsel is also available through:

- **Scoop**
- **Homebrew**
- **Debian / Ubuntu packages**

See **[Installation Guide](docs/INSTALLATION.md)** for platform-specific
instructions and mirrors.

---

## Build from Source

```bash
git clone https://github.com/MrEiu/Kapsel.git
cd Kapsel
pip install -e .
kps completion sync
```

---

# ⚙️ Configuration

Kapsel stores its main configuration at:

```text
~/.kapsel/config.yaml
```

Configuration can be inspected and changed directly from the terminal:

```bash
kps config
```

Open the configuration file:

```bash
kps config edit
```

Change individual values:

```bash
kps config set ui.enable_banner false
kps config set interaction.autosuggest_sensitivity 0.2
```

Configuration can be reloaded without restarting the interactive session.

See **[Configuration Guide](docs/configuration.md)** for the complete
configuration reference.

---

# 🏛️ Architecture

Kapsel is designed as a non-invasive execution layer around the host shell.

```text
                     Host Terminal
                           │
                           ▼
                ┌─────────────────────┐
                │       Kapsel        │
                │                     │
                │  Command Dispatcher │
                │  Completion Engine  │
                │  Plugin Registry    │
                │  History / State    │
                └──────────┬──────────┘
                           │
                 ┌─────────┴─────────┐
                 ▼                   ▼
          Native Executables     Kapsel Commands
          git / docker / ...      kps <command>
```

## Dual-State Execution

Kapsel separates two execution paths:

**Native execution**

System executables are passed through to the host environment with normal
TTY interaction, signals, streams, and process behavior.

**Kapsel execution**

Kapsel-managed commands are dispatched through the `kps` namespace and plugin
registry.

This separation allows Kapsel to enhance terminal workflows without replacing
the host shell itself.

---

## Collision-Safe Namespaces

Kapsel maintains explicit command namespaces so that utilities such as:

```text
alias
help
install
history
profile
ps
kill
dir
```

do not silently replace or hijack native shell built-ins.

For commands that may collide with the host environment, Kapsel keeps them
inside the `kps` namespace.

---

## Zero-Pollution State

All Kapsel-managed state is contained in:

```text
~/.kapsel/
├── config.yaml          # Configuration
├── history.db           # Persistent command history
├── bin/                 # User-space runtime binaries
├── specs/               # Completion specifications
├── plugins/             # Installed plugins
└── logs/                # Diagnostic and session logs
```

This keeps Kapsel's runtime state separate from your system and shell
configuration.

---

# 📚 Documentation

Detailed documentation is maintained separately from the project overview.

| Document | Description |
| :--- | :--- |
| [Installation Guide](docs/INSTALLATION.md) | Platform-specific installation and setup |
| [Configuration](docs/configuration.md) | Configuration options and runtime settings |
| [Commands](docs/commands.md) | Complete command and option reference |
| [Plugins](docs/plugins.md) | Plugin architecture and usage |
| [Plugin Development](https://github.com/MrEiu/plugins) | Creating and submitting plugins |
| [Architecture](docs/architecture.md) | Internal architecture and design |

---

# 🧪 Development & Testing

Clone the repository:

```bash
git clone https://github.com/MrEiu/Kapsel.git
cd Kapsel
```

Install the development and test dependencies:

```bash
pip install -e ".[test]"
```

Run the test suite:

```bash
pytest tests/ -v
```

---

# 🤝 Contributing

Contributions to Kapsel are welcome.

There are several ways to contribute:

### Core

Bug fixes, improvements, documentation, tests, and new capabilities for the
Kapsel core.

### Plugins

Create new plugins or improve existing ones through the
**[Kapsel Plugin Repository](https://github.com/MrEiu/plugins)**.

### Documentation

Improve examples, guides, translations, and developer documentation.

Before making substantial changes, please open an issue to discuss the
proposed direction.

---

# 📄 License

Kapsel is open-source software licensed under the
**[MIT License](LICENSE)**.

---

<div align="center">

**Kapsel — Wrap complexity, expose simplicity.**

Built by [MrEiu](https://github.com/MrEiu) and open-source contributors.

</div>
