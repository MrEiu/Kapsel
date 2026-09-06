<div align="center">

# ⚡ Kapsel

**Un environnement de terminal multiplateforme qui enveloppe votre shell avec des commandes unifiées, une autocomplétion contextuelle et zéro pollution globale.**

[![PyPI Version](https://img.shields.io/pypi/v/kapsel-cli?color=3776AB&logo=pypi&logoColor=white&style=flat-square)](https://pypi.org/project/kapsel-cli/)
[![Python Version](https://img.shields.io/badge/Python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-3776AB.svg?style=flat-square&logo=python&logoColor=white)](https://pypi.org/project/kapsel-cli/)
[![Platform Support](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-4D4D4D.svg?style=flat-square&logo=linux&logoColor=white)](https://github.com/MrEiu/Kapsel)
[![License](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](LICENSE)

[Pourquoi Kapsel ?](#-pourquoi-kapsel-) •
[Fonctionnalités](#-fonctionnalités) •
[Démarrage rapide](#-démarrage-rapide) •
[Plugins intégrés](#-plugins-intégrés) •
[Installation](#-installation) •
[Architecture](#-architecture--sandboxing) •
[🇨🇳 简体中文](README_zh.md)

</div>

---

### 📺 Capsule interactive en action

```text
╭─ kapsel [pwsh] ~/Projects/Kapsel 14:32:05
╰─ ❯ git checkout -b feature/dynamic-specs
✔ 0  git checkout -b feature/dynamic-specs  ⏱ 24ms
```

> **Enveloppez la complexité, exposez la simplicité.**
> Exécutez vos exécutables shell natifs comme d'habitude, tout en profitant d'une traduction automatique des commandes, de suggestions en ligne, de spécifications de complétion riches et d'une chaîne d'outils modulaire—le tout isolé dans `~/.kapsel/`.

---

## 💡 Pourquoi Kapsel ?

Changer de système d'exploitation entraîne souvent une mémoire musculaire cassée, des fichiers de configuration en désordre et des configurations d'autocomplétion fragmentées. Kapsel comble cette lacune grâce à une couche capsule non invasive :

| Défi | Configuration Shell Traditionnelle | Avec Kapsel |
| :--- | :--- | :--- |
| **Friction Multi-Plateforme** | Commandes fragmentées selon l'OS (`dir` vs `ls`, `rmdir` vs `rm -rf`) | Couche de commandes unifiée, priorisant Linux, sur Windows, macOS et Linux |
| **Pollution du Profil Shell** | `.bashrc` ou `$PROFILE` surchargés avec des scripts globaux fragiles | Sandbox 100% autonome dans `~/.kapsel/` (aucune mutation globale) |
| **Configuration de l'Autocomplétion** | Configuration manuelle par shell, souvent incomplète ou lente | Complétions instantanées et contextuelles pour plus de 1 000 outils CLI via Carapace |
| **Chaîne d'Outils & Éparpillement de la Synchronisation** | Outils disparates nécessitant une installation manuelle répétitive | Plugins `kps` intégrés pour les environnements d'exécution, les miroirs, le saut de répertoires et la synchronisation |

---

## ✨ Fonctionnalités

- **🌐 Cohérence des commandes multiplateformes** : Saisissez des commandes standard (`ls -la`, `cat`, `rm -rf`, `grep`) naturellement dans n'importe quel terminal ; elles sont automatiquement traduites en primitives natives de l'hôte sans détourner les fonctions intégrées de celui-ci.
- **⚡ Autocomplétion contextuelle** : Intégrée à [Carapace](https://carapace.sh) pour fournir des complétions d'arguments et de contexte à plusieurs niveaux (branches Git, images Docker, scripts npm) dans PowerShell, Bash et Zsh.
- **🛡️ Environnement sandbox sans pollution** : Tout (binaires, historique SQLite, spécifications déclaratives, plugins et journaux) réside dans `~/.kapsel/`. Vos fichiers de configuration shell hôte restent totalement intacts.
- **🧩 Écosystème de plugins organisé** : Accédez à de puissants utilitaires de développement (`zoxide`, `mise`, `chsrc`, `pueue`, assistants IA) directement via la commande unifiée `kps`.
- **🎨 Esthétique moderne en cartes** : Présentation visuelle épurée des commandes en cartes avec badges de code de sortie (`✔ 0` / `✘ 1`), chronométrage d'exécution et prise en charge i18n native dans 7 langues.

---

## 🚀 Démarrage rapide

Lancez le shell interactif de la capsule :

```bash
kapsel
```

Dans Kapsel, les commandes s'exécutent nativement avec un retour d'information amélioré :

```bash
# 1. Exécution native avec chronométrage et carte de code de sortie
git status
docker ps

# 2. Traduction universelle des commandes sur n'importe quel système d'exploitation
rm -rf ./temp_dir
cat package.json

# 3. Utilisez les plugins intégrés à tout moment
kps portal work        # Accéder au répertoire (zoxide)
kps ai "expliquez git rebase"  # Interroger l'assistant IA du terminal
kps shore get          # Sélection automatique des miroirs de paquets les plus rapides

# 4. Inspecter l'état de la capsule
kps status
```

> **Exécution en une seule commande** : Vous pouvez également invoquer directement les outils Kapsel depuis votre shell habituel en utilisant `kps <commande>` (par exemple `kps portal`, `kps status`, `kps ai`).

---

## 🧩 Plugins Intégrés

Kapsel est préconfiguré avec 11 plugins officiels, découplés, sous l'espace de noms `kps` :

| Plugin | Commande | Ce qu'il fait | Propulsé par |
| :--- | :--- | :--- | :--- |
| **`portal`** | `kps portal` / `z` | Saut rapide entre répertoires avec pondération par fréquence | [zoxide](https://github.com/ajeetdsouza/zoxide) |
| **`ai`** | `kps ai` | Copilote IA pour terminal, générant et expliquant des commandes | OpenAI / Claude / Ollama |
| **`init`** | `kps init` | Gestionnaire d'exécution de chaînes d'outils multi-langages (Node, Python, Go, Rust) | [mise](https://github.com/jdx/mise) |
| **`shore`** | `kps shore` | Benchmark et bascule vers les miroirs de téléchargement de paquets et OS les plus rapides | [chsrc](https://github.com/AkihiroSuda/chsrc) |
| **`install`** | `kps install` | Installateur logiciel universel regroupant plus de 20 gestionnaires de paquets | [mpm](https://github.com/MrEiu/mpm) |
| **`alias`** | `kps alias` | Traduction d'alias multiplateforme sans collision d'espace de noms | Moteur natif |
| **`autopilot`**| `kps autopilot`| File d'attente en arrière-plan et exécuteur de tâches démon autonome | [pueue](https://github.com/Nukesor/pueue) |
| **`help`** | `kps help <cmd>`| Aide-mémoire instantané, communautaire et pratique pour les commandes | [tealdeer](https://github.com/dbrgn/tealdeer) |
| **`fuck`** | `kps fuck` | Correction automatique intelligente et réparation syntaxique des commandes erronées | [thefuck](https://github.com/nvbn/thefuck) |
| **`profile`** | `kps profile` | Synchronisation multiplateforme des fichiers de configuration et postes de travail | [chezmoi](https://github.com/twpayne/chezmoi) |
| **`rec`** | `kps rec` | Signet et exécuteur de snippets de commandes CLI interactifs | [pet](https://github.com/knqyf263/pet) |

---

## 📦 Installation

### Recommandé (pipx / pip)

```bash
# Installation isolée via pipx (recommandé)
pipx install kapsel-cli

# Ou pip standard
pip install --upgrade kapsel-cli
```

### Installateurs automatisés en une ligne

Scripts de démarrage rapide qui détectent automatiquement votre système d'exploitation et configurent les complétions :

```bash
# macOS et Linux :
curl -fsSL https://raw.githubusercontent.com/MrEiu/Kapsel/master/scripts/install.sh | bash

# Windows (PowerShell) :
irm https://raw.githubusercontent.com/MrEiu/Kapsel/master/scripts/install.ps1 | iex
```

### Autres options d'installation

- **Binaires précompilés autonomes** : Téléchargez les versions prêtes à l'emploi depuis [GitHub Releases](https://github.com/MrEiu/Kapsel/releases/latest).
- **Gestionnaires de paquets** : Disponible sur Scoop (`scoop install kapsel`), Homebrew, et Debian/Ubuntu `.deb`.
- **Compilation depuis les sources** : `git clone https://github.com/MrEiu/Kapsel.git && cd Kapsel && pip install -e .`

👉 *Pour l'accélération via le miroir chinois et les détails complets sur les gestionnaires de paquets de toutes les plateformes, consultez **[docs/INSTALLATION.md](docs/INSTALLATION.md)**.*

## ⚙️ Configuration

Kapsel stocke sa configuration dans `~/.kapsel/config.yaml`. Gérez les paramètres directement depuis votre terminal :

```bash
# Afficher le tableau de bord de configuration
kps config

# Ouvrir le fichier de configuration dans un éditeur externe
kps config edit

# Ajuster les paramètres à la volée
kps config set ui.enable_banner false
kps config set interaction.autosuggest_sensitivity 0.2
```

---

## 🏛️ Architecture et Sandboxing

Kapsel suit un **Principe de Zéro Pollution**. Tout l'état d'exécution est strictement contenu :

```text
~/.kapsel/
├── config.yaml          # Configuration UI à l'échelle du système, thèmes et paramètres d'interaction
├── history.db           # Base de données SQLite persistante stockant l'historique des commandes et les statistiques
├── bin/                 # Outils binaires autonomes dans l'espace utilisateur (carapace, zoxide, mise...)
├── specs/               # Spécifications YAML déclaratives d'autocomplétion
├── plugins/             # Extensions de plugins officiels et communautaires installés
└── logs/                # Journaux de diagnostic et métriques de session
```

- **Moteur à Double État** : Les exécutables natifs s'exécutent directement via le passage en sous-shell hôte ; les utilitaires de capsule s'exécutent via le registre unifié `kps`.
- **Sentinelle de Collision** : Garantit que les commandes internes natives du shell (par exemple `Get-Alias`, `Get-Help` de PowerShell) ne sont jamais interceptées ou détournées.
- **Plugins Isolés** : Les plugins s'exécutent indépendamment, garantissant que les extensions tierces ne peuvent pas faire planter le shell principal.

---

## 🧪 Développement et Tests

```bash
# Cloner le dépôt
git clone https://github.com/MrEiu/Kapsel.git
cd Kapsel

# Installer le package en mode éditable avec les dépendances de test
pip install -e ".[test]"

# Exécuter la suite de tests unitaires
pytest tests/ -v
```

---

## 📄 Licence

Distribué sous la **[licence MIT](LICENSE)**. Réalisé par MrEiu et les contributeurs open-source.
