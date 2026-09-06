<div align="center">

# ⚡ Kapsel

**Cápsula de terminal multiplataforma para una experiencia de línea de comandos más limpia y coherente.**

[![PyPI Version](https://img.shields.io/pypi/v/kapsel-cli?color=3776AB&logo=pypi&logoColor=white&style=flat-square)](https://pypi.org/project/kapsel-cli/)
[![Python Version](https://img.shields.io/badge/Python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-3776AB.svg?style=flat-square&logo=python&logoColor=white)](https://pypi.org/project/kapsel-cli/)
[![Platform Support](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-4D4D4D.svg?style=flat-square&logo=linux&logoColor=white)](https://github.com/MrEiu/Kapsel)
[![License](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](LICENSE)

[Inicio Rápido](#-inicio-rápido) ·
[Características](#-características) ·
[Plugins](#-ecosistema-de-plugins) ·
[Instalación](#-instalación) ·
[Arquitectura](#-arquitectura) ·
[Documentación](#-documentación)

[English](README.md) ·
[🇨🇳 简体中文](README_zh.md) ·
[🇯🇵 日本語](README_ja.md) ·
[🇷🇺 Русский](README_ru.md) ·
[🇩🇪 Deutsch](README_de.md) ·
[🇫🇷 Français](README_fr.md) ·
[🇵🇱 Polski](README_pl.md)

</div>

---

## 📺 Kapsel en Acción

```text
╭─ kapsel [pwsh] ~/Projects/Kapsel 14:32:05
╰─ ❯ git checkout -b feature/dynamic-specs
✔ 0  git checkout -b feature/dynamic-specs  ⏱ 24ms
```

> **Envuelve la complejidad, expone la simplicidad.**
>
> Siga usando su shell nativa y los comandos del sistema como de costumbre, mientras Kapsel agrega una capa unificada de comandos, autocompletado consciente del contexto, sugerencias de historial en línea y un ecosistema extensible de plugins — todo autocontenido dentro de `~/.kapsel/`.

---

## 💡 ¿Por qué Kapsel?

Los flujos de trabajo en el terminal aún están fuertemente condicionados por el sistema operativo y la shell en uso.

La misma tarea cotidiana a menudo requiere diferentes comandos en Windows, macOS y Linux. La configuración de la shell está dispersa en archivos como `.bashrc`, `.zshrc` y perfiles de PowerShell, mientras que los sistemas de autocompletado y herramientas auxiliares requieren instalación y configuración independientes.

Kapsel añade una capa de cápsula no invasiva alrededor de su terminal actual:

| Problema | Configuración Tradicional | Solución Kapsel |
| :--- | :--- | :--- |
| **Comandos multiplataforma** | Diferente sintaxis según el sistema operativo | Capa unificada de comandos Linux-First |
| **Configuración de shell** | Archivos de perfil globales y scripts dispersos | Estado totalmente aislado en `~/.kapsel/` |
| **Autocompletado** | Configuración manual y compleja por herramienta | Autocompletado contextual con Carapace |
| **Utilidades de desarrollo** | Múltiples herramientas independientes | Ecosistema unificado de plugins bajo `kps` |
| **Extensibilidad** | Dependencia de scripts propios de cada shell | Arquitectura modular de plugins aislada |

Kapsel no sustituye a su shell ni a los ejecutables del sistema. Funciona a su lado proporcionando un entorno de ejecución coherente.

---

## ✨ Características

### 🌐 Ejecución Nativa y Multiplataforma

Ejecute sus comandos del sistema directamente:

```bash
git
docker
python
npm
cargo
vim
```

Al mismo tiempo, Kapsel ofrece una capa de comandos Linux-First para operaciones comunes:

```bash
ls -la
cat package.json
rm -rf ./dist
grep -r "TODO" .
```

Los comandos internos de su shell host quedan protegidos contra intercepciones no deseadas.

---

### ⚡ Autocompletado Contextual Inteligente

Kapsel se integra con [Carapace](https://carapace.sh) para ofrecer un autocompletado multinivel enriquecido:

El motor comprende comandos, argumentos, opciones y contexto dinámico como:

- Ramas y etiquetas de Git
- Contenedores e imágenes de Docker
- Recursos de Kubernetes
- Scripts de npm
- Más de 1.000 especificaciones de herramientas CLI

Las especificaciones se gestionan de forma declarativa y se pueden ampliar fácilmente mediante plugins.

---

### 💡 Sugerencias de Historial en Línea

Kapsel mantiene un almacenamiento SQLite local y sugiere comandos anteriores relevantes a medida que escribe.

Pulse `→` para aceptar una sugerencia de inmediato.

Todo el historial y el estado de ejecución permanecen seguros dentro de la sandbox de Kapsel.

---

### 🛡️ Entorno Limpio sin Contaminación

Kapsel guarda todas sus configuraciones, binarios, historial, especificaciones, plugins y registros en:

```text
~/.kapsel/
```

Diseñado para no alterar los archivos de configuración de su sistema:

```text
.bashrc
.zshrc
config.fish
PowerShell profiles
```

Su shell anfitriona permanece intacta.

---

### 🧩 Arquitectura Modular de Plugins

Bajo el espacio de nombres `kps`, Kapsel ofrece un entorno de ejecución de plugins.

Los plugins permiten añadir comandos, integraciones, flujos de trabajo y herramientas externas sin modificar el núcleo de Kapsel.

---

### 🎨 Experiencia Interactiva Moderna

Presentación en tarjeta compacta de dos líneas:

```text
╭─ ...
╰─ ❯ ...
✔ 0  ...  ⏱ 24ms
```

El estado de salida y el tiempo de ejecución en milisegundos se muestran de inmediato. Interfaz totalmente localizada en múltiples idiomas.

---

# 🚀 Inicio Rápido

## 1. Instalación

Método recomendado (mediante `pipx`):

```bash
pipx install kapsel-cli
```

O con `pip`:

```bash
pip install --upgrade kapsel-cli
```

## 2. Iniciar Kapsel

```bash
kapsel
```

Use su terminal con normalidad:

```bash
git status
docker ps
python --version
```

Y use comandos universales cuando lo requiera:

```bash
ls -la
cat package.json
rm -rf ./temp
```

## 3. Comandos de Kapsel

Las herramientas de Kapsel están disponibles mediante `kps`:

```bash
kps status
kps config
kps portal
kps ai
```

Ejemplos:

```bash
kps portal work
kps ai "explica el comando git rebase"
kps shore get
```

## 4. Ejecución en Línea Única

No necesita entrar en la cápsula interactiva para usar las herramientas:

```bash
kps status
kps portal
kps ai "busca archivos grandes"
```

Ideal para scripts, alias y flujos automatizados.

---

# 🧩 Ecosistema de Plugins

Kapsel está concebido como un entorno orientado a plugins y no como un paquete monolítico cerrado.

## Plugins Oficiales

| Plugin | Comando | Descripción | Motor |
| :--- | :--- | :--- | :--- |
| **`portal`** | `kps portal` / `z` | Navegación ultrarrápida de directorios por frecuencia y recencia | [zoxide](https://github.com/ajeetdsouza/zoxide) |
| **`ai`** | `kps ai` | Asistente de IA en el terminal para generar, explicar y ejecutar comandos | OpenAI / Claude / Ollama |
| **`init`** | `kps init` | Gestor de runtimes para Node, Python, Go, Rust y más | [mise](https://github.com/jdx/mise) |
| **`shore`** | `kps shore` | Test de velocidad y cambio al espejo de paquetes más veloz | [chsrc](https://github.com/AkihiroSuda/chsrc) |
| **`install`** | `kps install` | Instalación unificada de software entre gestores de paquetes | [mpm](https://github.com/MrEiu/mpm) |
| **`alias`** | `kps alias` | Traducción y unificación multiplataforma de alias de comandos | Motor Nativo |
| **`autopilot`** | `kps autopilot` | Colas de tareas en segundo plano y monitor de procesos | [pueue](https://github.com/Nukesor/pueue) |
| **`help`** | `kps help <cmd>` | Guías rápidas y ejemplos prácticos de comandos | [tealdeer](https://github.com/dbrgn/tealdeer) |
| **`fuck`** | `kps fuck` | Corrección automática de errores tipográficos en comandos | [thefuck](https://github.com/nvbn/thefuck) |
| **`profile`** | `kps profile` | Control de versiones para dotfiles y configuraciones | [chezmoi](https://github.com/twpayne/chezmoi) |
| **`rec`** | `kps rec` | Marcadores y plantillas parametrizadas de fragmentos CLI | [pet](https://github.com/knqyf263/pet) |

---

## 🌍 Plugins de la Comunidad

Los desarrolladores pueden crear y compartir sus propios plugins:

- Nuevas herramientas e integraciones
- Flujos de automatización
- Especificaciones personalizadas de Carapace

Puede colaborar a través del **[Repositorio de Plugins de Kapsel](https://github.com/MrEiu/plugins)**.

---

# 📦 Instalación

## Métodos recomendados

### pipx

```bash
pipx install kapsel-cli
```

### pip

```bash
pip install --upgrade kapsel-cli
```

---

## Instalador automático en una línea

### macOS & Linux

```bash
curl -fsSL https://raw.githubusercontent.com/MrEiu/Kapsel/master/scripts/install.sh | bash
```

### Windows PowerShell

```powershell
irm https://raw.githubusercontent.com/MrEiu/Kapsel/master/scripts/install.ps1 | iex
```

---

## Binarios Independientes (Sin Python)

Disponibles para entornos de producción o contenedores sin Python:

| Plataforma / Arquitectura | Archivo |
| :--- | :--- |
| **Windows x86_64** | `kapsel-windows-x86_64.zip` |
| **Linux x86_64** | `kapsel-linux-x86_64.tar.gz` |
| **macOS Universal** | `kapsel-macos-universal.tar.gz` |
| **Debian / Ubuntu** | `kapsel_amd64.deb` |

Obtenga la última versión en **[GitHub Releases](https://github.com/MrEiu/Kapsel/releases/latest)**.

---

## Gestores de paquetes

- **Scoop**
- **Homebrew**
- **Debian / Ubuntu (.deb)**

Consulte la **[Guía de Instalación](docs/INSTALLATION.md)** para más detalles.

---

## Compilar desde el código fuente

```bash
git clone https://github.com/MrEiu/Kapsel.git
cd Kapsel
pip install -e .
kps completion sync
```

---

# ⚙️ Configuración

Archivo principal de configuración:

```text
~/.kapsel/config.yaml
```

Inspeccionar o cambiar valores directamente desde la consola:

```bash
kps config
```

Abrir en el editor predeterminado:

```bash
kps config edit
```

Modificar valores puntuales:

```bash
kps config set ui.enable_banner false
kps config set interaction.autosuggest_sensitivity 0.2
```

Los cambios se recargan automáticamente sin reiniciar la sesión. Más información en la **[Guía de Configuración](docs/configuration.md)**.

---

# 🏛️ Arquitectura

Kapsel opera como una capa no invasiva alrededor de su shell:

```text
                     Terminal Anfitrión
                            │
                            ▼
                 ┌─────────────────────┐
                 │       Kapsel        │
                 │                     │
                 │ Despachador de cmd  │
                 │ Motor de completado │
                 │ Registro de plugins │
                 │ Historial y estado  │
                 └──────────┬──────────┘
                            │
                  ┌─────────┴─────────┐
                  ▼                   ▼
           Comandos Nativos     Comandos Kapsel
          git / docker / ...     kps <comando>
```

## Ejecución de Doble Estado (Dual-State Execution)

- **Ejecución Nativa**: Los programas del sistema se pasan de forma transparente manteniendo TTY, señales y redirecciones.
- **Ejecución Kapsel**: Las utilidades de Kapsel se despachan mediante el espacio `kps` y el registro de plugins.

## Espacios de Nombres sin Conflictos

Comandos como `alias`, `help`, `install`, `history`, `profile`, `ps`, `kill` y `dir` residen bajo el prefijo `kps`, evitando reemplazar comandos propios de la shell anfitriona.

## Organización de la Sandbox

```text
~/.kapsel/
├── config.yaml          # Configuración
├── history.db           # Base de datos SQLite del historial
├── bin/                 # Binarios de herramientas
├── specs/               # Especificaciones de Carapace
├── plugins/             # Plugins instalados
└── logs/                # Registros de sesión y diagnóstico
```

---

# 📚 Documentación

| Documento | Descripción |
| :--- | :--- |
| [Guía de Instalación](docs/INSTALLATION.md) | Instrucciones completas para cada plataforma |
| [Configuración](docs/configuration.md) | Opciones de configuración detalladas |
| [Referencia de Comandos](docs/commands.md) | Manual completo de comandos |
| [Plugins](docs/plugins.md) | Uso e instalación de plugins |
| [Desarrollo de Plugins](https://github.com/MrEiu/plugins) | Guía para crear y publicar plugins |
| [Arquitectura](docs/architecture.md) | Diseño técnico y fundamentos internos |

---

# 🧪 Desarrollo y Pruebas

Clonar el repositorio:

```bash
git clone https://github.com/MrEiu/Kapsel.git
cd Kapsel
```

Instalar dependencias de desarrollo:

```bash
pip install -e ".[test]"
```

Ejecutar la suite de pruebas:

```bash
pytest tests/ -v
```

---

# 🤝 Colaboración

Toda contribución a Kapsel es bienvenida:

- **Núcleo**: Corrección de fallos, mejoras y nuevas capacidades
- **Plugins**: Publicar nuevas utilidades en el **[repositorio de plugins](https://github.com/MrEiu/plugins)**
- **Documentación**: Traducciones, guías y ejemplos de uso

---

# 📄 Licencia

Kapsel es software de código abierto publicado bajo la licencia **[MIT License](LICENSE)**.

---

<div align="center">

**Kapsel — Envuelve la complejidad, expone la simplicidad.**

Creado por [MrEiu](https://github.com/MrEiu) y colaboradores de la comunidad de código abierto.

</div>
