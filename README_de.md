<div align="center">

# ⚡ Kapsel

**Eine plattformübergreifende Terminal-Umgebung, die Ihre Shell mit einheitlichen Befehlen, kontextbezogener Autovervollständigung und null globaler Verschmutzung umhüllt.**

[![PyPI Version](https://img.shields.io/pypi/v/kapsel-cli?color=3776AB&logo=pypi&logoColor=white&style=flat-square)](https://pypi.org/project/kapsel-cli/)
[![Python Version](https://img.shields.io/badge/Python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-3776AB.svg?style=flat-square&logo=python&logoColor=white)](https://pypi.org/project/kapsel-cli/)
[![Platform Support](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-4D4D4D.svg?style=flat-square&logo=linux&logoColor=white)](https://github.com/MrEiu/Kapsel)
[![License](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](LICENSE)

[Warum Kapsel?](#-warum-kapsel) •
[Funktionen](#-funktionen) •
[Schnellstart](#-schnellstart) •
[Integrierte Plugins](#-integrierte-plugins) •
[Installation](#-installation) •
[Architektur](#-architektur--sandboxing) •
[🇨🇳 简体中文](README_zh.md)

</div>

---

### 📺 Interaktive Kapsel in Aktion

```text
╭─ kapsel [pwsh] ~/Projects/Kapsel 14:32:05
╰─ ❯ git checkout -b feature/dynamic-specs
✔ 0  git checkout -b feature/dynamic-specs  ⏱ 24ms
```

> **Komplexität umhüllen, Einfachheit offenlegen.**
> Führen Sie Ihre nativen Shell-Executables wie gewohnt aus und genießen Sie gleichzeitig automatische Befehlsübersetzung, Inline-Vorschläge, umfangreiche Vervollständigungsspezifikationen und eine modulare Toolchain – alles in `~/.kapsel/` sandboxed.

---

## 💡 Warum Kapsel?

Der Wechsel zwischen Betriebssystemen führt oft zu gebrochenem Muskelgedächtnis, unübersichtlichen Dotfiles und fragmentierten Autovervollständigungs-Setups. Kapsel überbrückt diese Lücke mit einer nicht-invasiven Kapsel-Schicht:

| Herausforderung | Traditionelles Shell-Setup | Mit Kapsel |
| :--- | :--- | :--- |
| **Plattformübergreifende Reibung** | Fragmentierte Befehle über Betriebssysteme hinweg (`dir` vs. `ls`, `rmdir` vs. `rm -rf`) | Einheitliche Linux-first-Befehlsebene für Windows, macOS und Linux |
| **Shell-Profil-Verschmutzung** | Aufgeblähte `.bashrc` oder `$PROFILE` mit fragilen globalen Skripten | 100% eigenständige Sandbox in `~/.kapsel/` (null globale Mutation) |
| **Autovervollständigungs-Setup** | Manuelles Setup pro Shell, oft unvollständig oder langsam | Sofortige kontextbezogene Vervollständigungen für über 1.000 CLI-Tools über Carapace |
| **Toolchain- & Sync-Ausbreitung** | Zusammenhanglose Tools, die wiederholte manuelle Installation erfordern | Integrierte `kps`-Plugins für Laufzeiten, Spiegel, Verzeichnissprünge und Synchronisierung |

---

## ✨ Funktionen

- **🌐 Plattformübergreifende Befehls-Konsistenz**: Geben Sie Standardbefehle (`ls -la`, `cat`, `rm -rf`, `grep`) natürlich in jedem Terminal ein – sie werden automatisch in native Host-Primitive übersetzt, ohne die integrierten Host-Befehle zu übernehmen.
- **⚡ Kontextbezogene Autovervollständigung**: Integriert mit [Carapace](https://carapace.sh), um mehrstufige Argument- und Kontextvervollständigungen (Git-Branches, Docker-Images, npm-Skripte) in PowerShell, Bash und Zsh bereitzustellen.
- **🛡️ Null-Verschmutzungs-Sandboxing**: Alles (Binärdateien, SQLite-Verlauf, deklarative Spezifikationen, Plugins und Protokolle) befindet sich in `~/.kapsel/`. Ihre Host-Shell-Konfigurationsdateien bleiben vollständig unberührt.
- **🧩 Kuratierte Plugin-Ökologie**: Greifen Sie direkt über den einheitlichen `kps`-Befehl auf leistungsstarke Entwicklerwerkzeuge (`zoxide`, `mise`, `chsrc`, `pueue`, KI-Assistenten) zu.
- **🎨 Moderne Kartenrahmen-Ästhetik**: Saubere visuelle Befehls-Kartenrahmen mit Exit-Code-Abzeichen (`✔ 0` / `✘ 1`), Stoppuhr-Zeitmessung der Ausführung und nativer i18n-Unterstützung in 7 Sprachen.

---

## 🚀 Schnellstart

Starten Sie die interaktive Kapsel-Shell:

```bash
kapsel
```

Innerhalb von Kapsel laufen Befehle nativ mit erweitertem Feedback:

```bash
# 1. Nativer Durchgriff mit Zeitmessung & Exit-Code-Karte
git status
docker ps

# 2. Universelle Befehlsübersetzung auf jedem Betriebssystem
rm -rf ./temp_dir
cat package.json

# 3. Integrierte Plugins jederzeit nutzen
kps portal work        # Zum Verzeichnis springen (zoxide)
kps ai "explain git rebase"  # Terminal-KI-Assistenten fragen
kps shore get          # Schnellste Paket-Mirrors automatisch auswählen

# 4. Kapsel-Zustand prüfen
kps status
```

> **Einmalige Ausführung**: Sie können Kapsel-Werkzeuge auch direkt aus Ihrer regulären Shell mit `kps <Befehl>` aufrufen (z. B. `kps portal`, `kps status`, `kps ai`).

---

## 🧩 Integrierte Plugins

Kapsel wird mit 11 entkoppelten, offiziellen Plugins unter dem Namespace `kps` vorkonfiguriert geliefert:

| Plugin | Befehl | Funktion | Unterstützt durch |
| :--- | :--- | :--- | :--- |
| **`portal`** | `kps portal` / `z` | Schnelles Verzeichniswechseln mit Frecency-Gewichtung | [zoxide](https://github.com/ajeetdsouza/zoxide) |
| **`ai`** | `kps ai` | Terminal-KI-Copilot zum Generieren und Erklären von Befehlen | OpenAI / Claude / Ollama |
| **`init`** | `kps init` | Multi-Sprachen-Toolchain-Laufzeitmanager (Node, Python, Go, Rust) | [mise](https://github.com/jdx/mise) |
| **`shore`** | `kps shore` | Benchmark und Wechsel zu schnellsten Paket- & OS-Download-Mirrors | [chsrc](https://github.com/AkihiroSuda/chsrc) |
| **`install`** | `kps install` | Universeller Software-Installer, der 20+ Paketmanager aggregiert | [mpm](https://github.com/MrEiu/mpm) |
| **`alias`** | `kps alias` | Plattformübergreifende Alias-Übersetzung ohne Namespace-Kollisionen | Native Engine |
| **`autopilot`**| `kps autopilot`| Hintergrund-Warteschlange & autonomer Daemon-Aufgabenausführer | [pueue](https://github.com/Nukesor/pueue) |
| **`help`** | `kps help <cmd>`| Sofortige, community-getriebene praktische Befehls-Spickzettel | [tealdeer](https://github.com/dbrgn/tealdeer) |
| **`fuck`** | `kps fuck` | Intelligente Autokorrektur und Syntax-Fix für falsch getippte Befehle | [thefuck](https://github.com/nvbn/thefuck) |
| **`profile`** | `kps profile` | Plattformübergreifende Dotfile- und Workstation-Konfigurationssynchronisierung | [chezmoi](https://github.com/twpayne/chezmoi) |
| **`rec`** | `kps rec` | Interaktives CLI-Befehls-Snippet-Lesezeichen & Ausführer | [pet](https://github.com/knqyf263/pet) |

---

## 📦 Installation

### Empfohlen (pipx / pip)

```bash
# Isolierte Installation über pipx (empfohlen)
pipx install kapsel-cli

# Oder Standard-pip
pip install --upgrade kapsel-cli
```

### Automatisierte Ein-Zeilen-Installationsprogramme

Schnelle Bootstrap-Skripte, die Ihr Betriebssystem automatisch erkennen und Vervollständigungen konfigurieren:

```bash
# macOS & Linux:
curl -fsSL https://raw.githubusercontent.com/MrEiu/Kapsel/master/scripts/install.sh | bash

# Windows (PowerShell):
irm https://raw.githubusercontent.com/MrEiu/Kapsel/master/scripts/install.ps1 | iex
```

### Weitere Installationsoptionen

- **Eigenständige vorkompilierte Binärdateien**: Laden Sie sofort ausführbare Releases von [GitHub Releases](https://github.com/MrEiu/Kapsel/releases/latest) herunter.
- **Paketmanager**: Verfügbar über Scoop (`scoop install kapsel`), Homebrew und Debian/Ubuntu `.deb`.
- **Aus dem Quellcode erstellen**: `git clone https://github.com/MrEiu/Kapsel.git && cd Kapsel && pip install -e .`

👉 *Für China-Mirror-Beschleunigung und Details zu Paketmanagern auf allen Plattformen, siehe **[docs/INSTALLATION.md](docs/INSTALLATION.md)**.*

## ⚙️ Konfiguration

Kapsel speichert seine Konfiguration in `~/.kapsel/config.yaml`. Verwalten Sie Einstellungen direkt über Ihr Terminal:

```bash
# Konfigurations-Dashboard anzeigen
kps config

# Konfigurationsdatei im externen Editor öffnen
kps config edit

# Einstellungen spontan anpassen
kps config set ui.enable_banner false
kps config set interaction.autosuggest_sensitivity 0.2
```

---

## 🏛️ Architektur & Sandboxing

Kapsel folgt einem **Zero-Pollution-Prinzip**. Der gesamte Laufzeitzustand ist strikt gekapselt:

```text
~/.kapsel/
├── config.yaml          # Systemweite UI-Konfiguration, Themes und Interaktionseinstellungen
├── history.db           # Persistente SQLite-Datenbank zur Speicherung von Befehlsverlauf und Statistiken
├── bin/                 # Eigenständige Binärwerkzeuge im Benutzerbereich (carapace, zoxide, mise...)
├── specs/               # Deklarative YAML-Spezifikationen für die automatische Vervollständigung
├── plugins/             # Installierte offizielle und Community-Plugin-Erweiterungen
└── logs/                # Diagnoseprotokolle und Sitzungsmetriken
```

- **Dual-State-Engine**: Native ausführbare Dateien laufen direkt über die Host-Subshell-Durchreichung; Kapsel-Dienstprogramme laufen über die einheitliche `kps`-Registry.
- **Kollisions-Sentinel**: Stellt sicher, dass native Shell-Built-ins (z. B. PowerShells `Get-Alias`, `Get-Help`) niemals abgefangen oder gekapert werden.
- **Isolierte Plugins**: Plugins laufen unabhängig und stellen sicher, dass Erweiterungen von Drittanbietern die Kern-Shell nicht zum Absturz bringen können.

---

## 🧪 Entwicklung & Testen

```bash
# Repository klonen
git clone https://github.com/MrEiu/Kapsel.git
cd Kapsel

# Editierbares Paket mit Testabhängigkeiten installieren
pip install -e ".[test]"

# Unit-Test-Suite ausführen
pytest tests/ -v
```

---

## 📄 Lizenz

Verteilt unter der **[MIT-Lizenz](LICENSE)**. Entwickelt von MrEiu und Open-Source-Mitwirkenden.
