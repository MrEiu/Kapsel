<div align="center">

# ⚡ Kapsel

**Eine plattformübergreifende Terminal-Kapsel für ein saubereres, konsistentes Befehlszeilenerlebnis.**

[![PyPI Version](https://img.shields.io/pypi/v/kapsel-cli?color=3776AB&logo=pypi&logoColor=white&style=flat-square)](https://pypi.org/project/kapsel-cli/)
[![Python Version](https://img.shields.io/badge/Python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-3776AB.svg?style=flat-square&logo=python&logoColor=white)](https://pypi.org/project/kapsel-cli/)
[![Platform Support](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-4D4D4D.svg?style=flat-square&logo=linux&logoColor=white)](https://github.com/MrEiu/Kapsel)
[![License](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](LICENSE)

[Schnellstart](#-schnellstart) ·
[Funktionen](#-funktionen) ·
[Plugins](#-plugin-ökosystem) ·
[Installation](#-installation) ·
[Architektur](#-architektur) ·
[Dokumentation](#-dokumentation)

[English](README.md) ·
[🇨🇳 简体中文](README_zh.md) ·
[🇯🇵 日本語](README_ja.md) ·
[🇷🇺 Русский](README_ru.md) ·
[🇪🇸 Español](README_es.md) ·
[🇫🇷 Français](README_fr.md) ·
[🇵🇱 Polski](README_pl.md)

</div>

---

## 📺 Kapsel in Aktion

```text
╭─ kapsel [pwsh] ~/Projects/Kapsel 14:32:05
╰─ ❯ git checkout -b feature/dynamic-specs
✔ 0  git checkout -b feature/dynamic-specs  ⏱ 24ms
```

> **Komplexität kapseln, Einfachheit freisetzen.**
>
> Nutzen Sie Ihre gewohnte Shell und Systemprogramme wie gewohnt weiter, während Kapsel eine einheitliche Befehlsebene, kontextbezogene Autovervollständigung, intelligente Verlaufsvorschläge und ein erweiterbares Plugin-Ökosystem hinzufügt — alles vollständig gekapselt in `~/.kapsel/`.

---

## 💡 Warum Kapsel?

Entwickler-Workflows im Terminal sind noch immer stark vom zugrundeliegenden Betriebssystem und der verwendeten Shell geprägt.

Dieselbe alltägliche Aufgabe erfordert oft unterschiedliche Befehle unter Windows, macOS und Linux. Shell-Konfigurationen sind über Dateien wie `.bashrc`, `.zshrc` und PowerShell-Profile verstreut, während Autovervollständigungen und Hilfswerkzeuge separat installiert werden müssen.

Kapsel legt eine nicht-invasive Kapsel-Schicht um Ihr bestehendes Terminal:

| Herausforderung | Traditioneller Ansatz | Kapsel-Ansatz |
| :--- | :--- | :--- |
| **Plattformübergreifende Befehle** | Unterschiedliche Befehle und Syntax pro OS | Einheitliche Linux-First Befehlsebene |
| **Shell-Konfiguration** | Globale Profildateien und fragmentierte Skripte | Vollständig isolierter Zustand unter `~/.kapsel/` |
| **Autovervollständigung** | Aufwendige Konfiguration pro Tool und Shell | Kontextbezogene Vervollständigung mit Carapace |
| **Entwickler-Tools** | Viele unverbundene Werkzeuge | Einheitliches Plugin-Ökosystem unter `kps` |
| **Erweiterbarkeit** | Shell-spezifische Skriptabhängigkeiten | Isolierte modulare Plugin-Architektur |

Kapsel ersetzt weder Ihre Shell noch Ihre Systembefehle. Es arbeitet Hand in Hand mit ihnen und bietet eine konsistente Arbeitsumgebung.

---

## ✨ Funktionen

### 🌐 Native & plattformübergreifende Ausführung

Verwenden Sie Ihre normalen Systembefehle direkt:

```bash
git
docker
python
npm
cargo
vim
```

Gleichzeitig bietet Kapsel eine Linux-First-Befehlsebene für gängige plattformübergreifende Operationen:

```bash
ls -la
cat package.json
rm -rf ./dist
grep -r "TODO" .
```

Eingebaute Befehle der Host-Shell sind zuverlässig vor versehentlichem Abfangen geschützt.

---

### ⚡ Kontextbezogene Autovervollständigung

Kapsel integriert [Carapace](https://carapace.sh) für eine tiefe, mehrstufige Befehlsvervollständigung:

Die Engine versteht Befehle, Argumente, Optionen und dynamischen Kontext:

- Git-Branches und Tags
- Docker-Container und Images
- Kubernetes-Ressourcen
- npm-Skripte
- Über 1.000 weitere CLI-Spezifikationen

Vervollständigungsspezifikationen werden deklarativ verwaltet und können leicht durch Plugins erweitert werden.

---

### 💡 Intelligente Inline-Vorschläge

Kapsel verwaltet einen lokalen SQLite-Verlaufsspeicher und schlägt während der Eingabe passende frühere Befehle vor.

Drücken Sie `→`, um einen Vorschlag direkt zu übernehmen.

Der Verlauf und der Laufzeitzustand verbleiben sicher in der Kapsel-Sandbox.

---

### 🛡️ Saubere Null-Verschmutzungs-Sandbox

Kapsel speichert Konfigurationen, Binärdateien, Verlauf, Spezifikationen, Plugins und Protokolle unter:

```text
~/.kapsel/
```

Bestehende Shell-Konfigurationsdateien werden nicht verändert:

```text
.bashrc
.zshrc
config.fish
PowerShell-Profile
```

Ihre Host-Shell bleibt unangetastet.

---

### 🧩 Modulare Plugin-Architektur

Kapsel bietet eine Plugin-Laufzeitumgebung unter dem Namensraum `kps`.

Plugins können Befehle, Workflows, Vervollständigungsspezifikationen und externe CLI-Tools hinzufügen, ohne den Kern von Kapsel zu verändern.

---

### 🎨 Moderne interaktive Terminal-Erfahrung

Die interaktive Kapsel bietet ein kompaktes zweizeiliges Kartenlayout:

```text
╭─ ...
╰─ ❯ ...
✔ 0  ...  ⏱ 24ms
```

Beendigungsstatus und Ausführungszeit in Millisekunden werden unmittelbar angezeigt. Die Benutzeroberfläche ist mehrsprachig lokalisiert.

---

# 🚀 Schnellstart

## 1. Installation

Empfohlene Installationsmethode (über `pipx`):

```bash
pipx install kapsel-cli
```

Oder über `pip`:

```bash
pip install --upgrade kapsel-cli
```

## 2. Kapsel starten

```bash
kapsel
```

Nutzen Sie Ihr Terminal wie gewohnt:

```bash
git status
docker ps
python --version
```

Verwenden Sie bei Bedarf universelle Befehle:

```bash
ls -la
cat package.json
rm -rf ./temp
```

## 3. Kapsel-Werkzeuge nutzen

Kapsel-Befehle sind über `kps` verfügbar:

```bash
kps status
kps config
kps portal
kps ai
```

Beispiele:

```bash
kps portal work
kps ai "Erkläre git rebase"
kps shore get
```

## 4. Einmalige Befehlsausführung

Sie müssen die interaktive Kapsel nicht betreten, um Kapsel-Tools zu nutzen:

```bash
kps status
kps portal
kps ai "Finde große Dateien"
```

Ideal für Skripte, Aliase und automatisierte Workflows.

---

# 🧩 Plugin-Ökosystem

Kapsel ist als Plugin-orientierte Umgebung konzipiert und nicht als starrer monolithischer Funktionsblock.

## Offizielle Plugins

| Plugin | Befehl | Beschreibung | Angetrieben durch |
| :--- | :--- | :--- | :--- |
| **`portal`** | `kps portal` / `z` | Blitzschnelle Verzeichnisnavigation basierend auf Nutzungshäufigkeit | [zoxide](https://github.com/ajeetdsouza/zoxide) |
| **`ai`** | `kps ai` | KI-Terminalassistent zum Erzeugen, Erklären und Ausführen von Befehlen | OpenAI / Claude / Ollama |
| **`init`** | `kps init` | Laufzeit- und Toolchain-Manager für Node, Python, Go, Rust u.v.m. | [mise](https://github.com/jdx/mise) |
| **`shore`** | `kps shore` | Geschwindigkeitsmessung und Wechsel zu den schnellsten Paket-Spiegeln | [chsrc](https://github.com/AkihiroSuda/chsrc) |
| **`install`** | `kps install` | Paketmanager-übergreifende Softwareinstallation | [mpm](https://github.com/MrEiu/mpm) |
| **`alias`** | `kps alias` | Plattformübergreifende Befehlsübersetzung und Aliase | Native Engine |
| **`autopilot`** | `kps autopilot` | Hintergrund-Aufgabenwarteschlangen und Prozessverwaltung | [pueue](https://github.com/Nukesor/pueue) |
| **`help`** | `kps help <cmd>` | Praxisnahe Spickzettel und Befehlsbeispiele | [tealdeer](https://github.com/dbrgn/tealdeer) |
| **`fuck`** | `kps fuck` | Automatische Syntaxkorrektur von fehlerhaften Befehlen | [thefuck](https://github.com/nvbn/thefuck) |
| **`profile`** | `kps profile` | Versionsverwaltung von Dotfiles und Konfigurationen | [chezmoi](https://github.com/twpayne/chezmoi) |
| **`rec`** | `kps rec` | Lesezeichen für Befehlsschnipsel mit Parametern | [pet](https://github.com/knqyf263/pet) |

---

## 🌍 Community-Plugins

Entwickler können Kapsel durch eigene Plugins erweitern:

- Neue CLI-Befehle und Integrationen
- Cloud- und Deployment-Workflows
- Benutzerdefinierte Carapace-Spezifikationen

Beiträge können über das **[Kapsel Plugin Repository](https://github.com/MrEiu/plugins)** eingereicht werden.

---

# 📦 Installation

## Empfohlene Methoden

### pipx

```bash
pipx install kapsel-cli
```

### pip

```bash
pip install --upgrade kapsel-cli
```

---

## Automatisierte Ein-Zeilen-Installation

### macOS & Linux

```bash
curl -fsSL https://raw.githubusercontent.com/MrEiu/Kapsel/master/scripts/install.sh | bash
```

### Windows PowerShell

```powershell
irm https://raw.githubusercontent.com/MrEiu/Kapsel/master/scripts/install.ps1 | iex
```

---

## Eigenständige Binärdateien (Ohne Python)

Vorkompilierte Releases stehen für Systeme ohne Python zur Verfügung:

| Plattform / Architektur | Datei |
| :--- | :--- |
| **Windows x86_64** | `kapsel-windows-x86_64.zip` |
| **Linux x86_64** | `kapsel-linux-x86_64.tar.gz` |
| **macOS Universal** | `kapsel-macos-universal.tar.gz` |
| **Debian / Ubuntu** | `kapsel_amd64.deb` |

Aktuelle Downloads finden Sie unter **[GitHub Releases](https://github.com/MrEiu/Kapsel/releases/latest)**.

---

## Paketmanager

- **Scoop**
- **Homebrew**
- **Debian / Ubuntu (.deb)**

Ausführliche Anleitungen finden Sie im **[Installationshandbuch](docs/INSTALLATION.md)**.

---

## Aus Quellcode bauen

```bash
git clone https://github.com/MrEiu/Kapsel.git
cd Kapsel
pip install -e .
kps completion sync
```

---

# ⚙️ Konfiguration

Hauptkonfigurationsdatei:

```text
~/.kapsel/config.yaml
```

Konfiguration direkt über das Terminal einsehen und bearbeiten:

```bash
kps config
```

Im Standardeditor öffnen:

```bash
kps config edit
```

Einzelne Einstellungen anpassen:

```bash
kps config set ui.enable_banner false
kps config set interaction.autosuggest_sensitivity 0.2
```

Änderungen werden sofort im laufenden Betrieb wirksam. Details im **[Konfigurationsleitfaden](docs/configuration.md)**.

---

# 🏛️ Architektur

Kapsel arbeitet als nicht-invasive Ebene um die Host-Shell herum:

```text
                     Host-Terminal
                           │
                           ▼
                ┌─────────────────────┐
                │       Kapsel        │
                │                     │
                │  Befehls-Dispatcher │
                │  Completion Engine  │
                │  Plugin-Registry    │
                │  Verlauf & Zustand  │
                └──────────┬──────────┘
                           │
                 ┌─────────┴─────────┐
                 ▼                   ▼
           Systembefehle       Kapsel-Befehle
         git / docker / ...     kps <befehl>
```

## Dual-State-Ausführung

- **Native Ausführung**: Systemprogramme werden unverändert transparent an die Host-Umgebung durchgereicht. TTY, Signale und Pipes bleiben vollständig erhalten.
- **Kapsel-Ausführung**: Über den Namensraum `kps` werden Kapsel-eigene Werkzeuge und Plugins ausgeführt.

## Kollisionssichere Namensräume

Befehle wie `alias`, `help`, `install`, `history`, `profile`, `ps`, `kill` und `dir` verbleiben im `kps`-Namensraum, um Systembefehle nicht zu überschreiben.

## Null-Verschmutzungs-Struktur

```text
~/.kapsel/
├── config.yaml          # Konfiguration
├── history.db           # SQLite-Befehlsverlauf
├── bin/                 # Benutzerdefinierte Binärdateien
├── specs/               # Carapace-Spezifikationen
├── plugins/             # Installierte Plugins
└── logs/                # Diagnose- und Sitzungsprotokolle
```

---

# 📚 Dokumentation

| Dokument | Beschreibung |
| :--- | :--- |
| [Installationshandbuch](docs/INSTALLATION.md) | Detaillierte Plattform-Installationsanleitungen |
| [Konfiguration](docs/configuration.md) | Alle Konfigurationsparameter im Überblick |
| [Befehlsreferenz](docs/commands.md) | Vollständige Befehlsübersicht |
| [Plugins](docs/plugins.md) | Plugin-Nutzung und Einrichtung |
| [Plugin-Entwicklung](https://github.com/MrEiu/plugins) | Eigene Plugins erstellen und veröffentlichen |
| [Architektur](docs/architecture.md) | Systemdesign und technische Details |

---

# 🧪 Entwicklung & Tests

Repository klonen:

```bash
git clone https://github.com/MrEiu/Kapsel.git
cd Kapsel
```

Abhängigkeiten installieren:

```bash
pip install -e ".[test]"
```

Tests ausführen:

```bash
pytest tests/ -v
```

---

# 🤝 Mitwirken

Wir freuen uns über jede Unterstützung für Kapsel:

- **Kern**: Fehlerbehebungen, Verbesserungen und neue Funktionen
- **Plugins**: Eigene Werkzeuge im **[Plugin-Repository](https://github.com/MrEiu/plugins)** veröffentlichen
- **Dokumentation**: Übersetzungen und Anwendungsbeispiele erweitern

---

# 📄 Lizenz

Kapsel ist Open-Source-Software unter der **[MIT-Lizenz](LICENSE)**.

---

<div align="center">

**Kapsel — Komplexität kapseln, Einfachheit freisetzen.**

Entwickelt von [MrEiu](https://github.com/MrEiu) und Open-Source-Mitwirkenden.

</div>
