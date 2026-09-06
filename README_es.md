<div align="center">

# ⚡ Kapsel

**Un entorno de terminal multiplataforma que envuelve tu shell con comandos unificados, autocompletado contextual y cero contaminación global.**

[![PyPI Version](https://img.shields.io/pypi/v/kapsel-cli?color=3776AB&logo=pypi&logoColor=white&style=flat-square)](https://pypi.org/project/kapsel-cli/)
[![Python Version](https://img.shields.io/badge/Python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-3776AB.svg?style=flat-square&logo=python&logoColor=white)](https://pypi.org/project/kapsel-cli/)
[![Platform Support](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-4D4D4D.svg?style=flat-square&logo=linux&logoColor=white)](https://github.com/MrEiu/Kapsel)
[![License](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](LICENSE)

[¿Por qué Kapsel?](#-por-qué-kapsel) •
[Características](#-características) •
[Inicio Rápido](#-inicio-rápido) •
[Plugins Integrados](#-plugins-integrados) •
[Instalación](#-instalación) •
[Arquitectura](#-arquitectura--aislamiento) •
[🇨🇳 简体中文](README_zh.md)

</div>

---

### 📺 Cápsula Interactiva en Acción

```text
╭─ kapsel [pwsh] ~/Projects/Kapsel 14:32:05
╰─ ❯ git checkout -b feature/dynamic-specs
✔ 0  git checkout -b feature/dynamic-specs  ⏱ 24ms
```

> **Envuelve la complejidad, expón la simplicidad.**
> Ejecuta tus ejecutables de shell nativos como siempre, mientras disfrutas de traducción automática de comandos, sugerencias en línea, especificaciones de completado enriquecidas y un conjunto de herramientas modular—todo aislado dentro de `~/.kapsel/`.

---

## 💡 ¿Por qué Kapsel?

Cambiar entre sistemas operativos a menudo conduce a memoria muscular rota, archivos de configuración desordenados y configuraciones de autocompletado fragmentadas. Kapsel cierra esta brecha con una capa de cápsula no invasiva:

| Desafío | Configuración de Shell Tradicional | Con Kapsel |
| :--- | :--- | :--- |
| **Fricción entre plataformas** | Comandos fragmentados entre sistemas operativos (`dir` vs `ls`, `rmdir` vs `rm -rf`) | Capa de comandos unificada basada en Linux para Windows, macOS y Linux |
| **Contaminación del perfil de shell** | `.bashrc` o `$PROFILE` inflados con scripts globales frágiles | Entorno aislado 100% autocontenido en `~/.kapsel/` (cero mutación global) |
| **Configuración de autocompletado** | Configuración manual por shell, a menudo incompleta o lenta | Autocompletados instantáneos conscientes del contexto para más de 1,000 herramientas CLI mediante Carapace |
| **Dispersión de herramientas y sincronización** | Herramientas inconexas que requieren instalación manual repetitiva | Complementos `kps` integrados para runtimes, espejos, salto de directorios y sincronización |

---

## ✨ Características

- **🌐 Consistencia de comandos multiplataforma**: Escriba comandos estándar (`ls -la`, `cat`, `rm -rf`, `grep`) de forma natural en cualquier terminal, traducidos automáticamente a primitivas nativas del sistema sin interferir con las funciones integradas del host.
- **⚡ Autocompletado consciente del contexto**: Integrado con [Carapace](https://carapace.sh) para ofrecer completados de argumentos y contexto de múltiples niveles (ramas de Git, imágenes de Docker, scripts de npm) en PowerShell, Bash y Zsh.
- **🛡️ Aislamiento sin contaminación**: Todo (binarios, historial SQLite, especificaciones declarativas, plugins y registros) reside dentro de `~/.kapsel/`. Los archivos de configuración de su shell host permanecen completamente intactos.
- **🧩 Ecosistema de plugins seleccionados**: Acceda a potentes utilidades de desarrollo (`zoxide`, `mise`, `chsrc`, `pueue`, asistentes de IA) directamente a través del comando unificado `kps`.
- **🎨 Estética moderna con tarjetas**: Presentación visual limpia de comandos en tarjetas con insignias de código de salida (`✔ 0` / `✘ 1`), cronómetro de ejecución y soporte nativo de i18n en 7 idiomas.

---

## 🚀 Inicio Rápido

Lanza la cápsula interactiva:

```bash
kapsel
```

Dentro de Kapsel, los comandos se ejecutan de forma nativa con retroalimentación mejorada:

```bash
# 1. Paso directo nativo con tarjeta de tiempo y código de salida
git status
docker ps

# 2. Traducción universal de comandos en cualquier sistema operativo
rm -rf ./temp_dir
cat package.json

# 3. Usa los complementos integrados en cualquier momento
kps portal work        # Saltar al directorio (zoxide)
kps ai "explain git rebase"  # Pregunta al asistente de IA del terminal
kps shore get          # Selecciona automáticamente los espejos de paquetes más rápidos

# 4. Inspecciona el estado de la cápsula
kps status
```

> **Ejecución de un solo uso**: También puedes invocar las herramientas de Kapsel directamente desde tu shell habitual usando `kps <comando>` (por ejemplo, `kps portal`, `kps status`, `kps ai`).

---

## 🧩 Plugins Integrados

Kapsel viene preconfigurado con 11 plugins oficiales desacoplados bajo el espacio de nombres `kps`:

| Plugin | Comando | Qué Hace | Impulsado por |
| :--- | :--- | :--- | :--- |
| **`portal`** | `kps portal` / `z` | Salto rápido entre directorios con ponderación por frecuencia | [zoxide](https://github.com/ajeetdsouza/zoxide) |
| **`ai`** | `kps ai` | Copiloto de IA para terminal que genera y explica comandos | OpenAI / Claude / Ollama |
| **`init`** | `kps init` | Gestor de entornos de ejecución para múltiples lenguajes (Node, Python, Go, Rust) | [mise](https://github.com/jdx/mise) |
| **`shore`** | `kps shore` | Evalúa y cambia a los espejos de descarga de paquetes y SO más rápidos | [chsrc](https://github.com/AkihiroSuda/chsrc) |
| **`install`** | `kps install` | Instalador de software universal que agrega más de 20 gestores de paquetes | [mpm](https://github.com/MrEiu/mpm) |
| **`alias`** | `kps alias` | Traducción de alias multiplataforma sin colisión de espacios de nombres | Motor Nativo |
| **`autopilot`**| `kps autopilot`| Cola en segundo plano y ejecutor autónomo de tareas daemon | [pueue](https://github.com/Nukesor/pueue) |
| **`help`** | `kps help <cmd>`| Hojas de referencia rápidas, prácticas e impulsadas por la comunidad | [tealdeer](https://github.com/dbrgn/tealdeer) |
| **`fuck`** | `kps fuck` | Corrección automática inteligente y arreglo de sintaxis para comandos mal escritos | [thefuck](https://github.com/nvbn/thefuck) |
| **`profile`** | `kps profile` | Sincronización de dotfiles y configuración de estaciones de trabajo multiplataforma | [chezmoi](https://github.com/twpayne/chezmoi) |
| **`rec`** | `kps rec` | Marcador y ejecutor interactivo de fragmentos de comandos CLI | [pet](https://github.com/knqyf263/pet) |

---

## 📦 Instalación

### Recomendado (pipx / pip)

```bash
# Instalación aislada mediante pipx (recomendado)
pipx install kapsel-cli

# O pip estándar
pip install --upgrade kapsel-cli
```

### Instaladores Automatizados de Una Línea

Scripts de arranque rápido que detectan automáticamente tu sistema operativo y configuran las finalizaciones:

```bash
# macOS y Linux:
curl -fsSL https://raw.githubusercontent.com/MrEiu/Kapsel/master/scripts/install.sh | bash

# Windows (PowerShell):
irm https://raw.githubusercontent.com/MrEiu/Kapsel/master/scripts/install.ps1 | iex
```

### Otras Opciones de Instalación

- **Binarios Precompilados Independientes**: Descarga versiones listas para ejecutar desde [GitHub Releases](https://github.com/MrEiu/Kapsel/releases/latest).
- **Gestores de Paquetes**: Disponible en Scoop (`scoop install kapsel`), Homebrew y `.deb` para Debian/Ubuntu.
- **Compilar desde el Código Fuente**: `git clone https://github.com/MrEiu/Kapsel.git && cd Kapsel && pip install -e .`

👉 *Para aceleración con espejos en China y detalles completos de gestores de paquetes por plataforma, consulta **[docs/INSTALLATION.md](docs/INSTALLATION.md)**.*

---

## ⚙️ Configuración

Kapsel almacena su configuración en `~/.kapsel/config.yaml`. Gestiona los ajustes directamente desde tu terminal:

```bash
# Ver el panel de configuración
kps config

# Abrir el archivo de configuración en un editor externo
kps config edit

# Ajustar configuraciones sobre la marcha
kps config set ui.enable_banner false
kps config set interaction.autosuggest_sensitivity 0.2
```

---

## 🏛️ Arquitectura y Aislamiento

Kapsel sigue un **Principio de Cero Contaminación**. Todo el estado en tiempo de ejecución está estrictamente contenido:

```text
~/.kapsel/
├── config.yaml          # Configuración de interfaz de usuario, temas y ajustes de interacción a nivel de sistema
├── history.db           # Base de datos SQLite persistente que almacena historial de comandos y estadísticas
├── bin/                 # Herramientas binarias independientes en espacio de usuario (carapace, zoxide, mise...)
├── specs/               # Especificaciones YAML declarativas de autocompletado
├── plugins/             # Extensiones de complementos oficiales y de la comunidad instaladas
└── logs/                # Registros de diagnóstico y métricas de sesión
```

- **Motor de Doble Estado**: Los ejecutables nativos se ejecutan directamente mediante paso directo de subcapa del host; las utilidades de cápsula se ejecutan mediante el registro unificado `kps`.
- **Centinela de Colisiones**: Garantiza que los comandos integrados nativos del shell (por ejemplo, `Get-Alias`, `Get-Help` de PowerShell) nunca sean interceptados o secuestrados.
- **Complementos Aislados**: Los complementos se ejecutan de forma independiente, asegurando que las extensiones de terceros no puedan bloquear el shell principal.

---

## 🧪 Desarrollo y Pruebas

```bash
# Clonar el repositorio
git clone https://github.com/MrEiu/Kapsel.git
cd Kapsel

# Instalar el paquete editable con dependencias de prueba
pip install -e ".[test]"

# Ejecutar la suite de pruebas unitarias
pytest tests/ -v
```

---

## 📄 Licencia

Distribuido bajo la **[Licencia MIT](LICENSE)**. Creado por MrEiu y colaboradores de código abierto.
