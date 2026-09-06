<div align="center">

# ⚡ Kapsel

**Cápsula de Terminal Inteligente de Próxima Generación y Multiplexor de Shell Ergonómico Multiplataforma**

[![Versión de Python](https://img.shields.io/badge/Python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-3776AB.svg?style=flat-square&logo=python&logoColor=white)](https://pypi.org/project/kapsel-cli/)
[![Soporte de Plataformas](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-4D4D4D.svg?style=flat-square&logo=linux&logoColor=white)](https://github.com/MrEiu/Kapsel)
[![Licencia](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](LICENSE)

<p align="center">
  <i>"Envuelve la complejidad, expón la simplicidad."</i><br>
  Una capa de abstracción de comandos consciente del contexto, sin contaminación, y un entorno de cápsula interactivo de alto rendimiento.<br>
  Potenciando flujos de trabajo de desarrolladores consistentes en Windows PowerShell, macOS Zsh y Linux Bash.
</p>

---

[Características Clave](#-características-clave) •
[Instalación Rápida](#-instalación-rápida) •
[Arquitectura](#-arquitectura--filosofía) •
[Ecosistema de Plugins](#-ecosistema-de-plugins-oficiales) •
[Comparación](#-matriz-de-características--comparación) •
[Referencia de Comandos](#-referencia-de-comandos) •
[🇨🇳 简体中文](README_zh.md)

---

</div>

```text
╭─ kapsel [pwsh] ~/Projects/Kapsel 14:32:05
╰─ ❯ git checkout -b feature/dynamic-specs
✔ 0  git checkout -b feature/dynamic-specs  ⏱ 24ms
```

---

## 🌟 Resumen

Los desarrolladores oscilan a diario entre sistemas operativos dispares, sufriendo una ergonomía de terminal fragmentada:
- Colisiones de memoria muscular (`rm -rf` vs `Remove-Item`, `cat` vs `type`, `ls -la` vs `dir /a`);
- Dotfiles globales frágiles que contaminan `.bashrc`, `config.fish` o `$PROFILE`;
- Motores de autocompletado inconsistentes entre shells.

**Kapsel** resuelve esto introduciendo una **cápsula de terminal aislada y no invasiva**. Opera como una capa de ejecución ergonómica que intercepta y mejora las interacciones de línea de comandos con **cero contaminación global del sistema**—ofreciendo autocompletado asíncrono de submilisegundos, mapeo universal priorizando Linux y aislamiento automatizado del entorno.

---

## 🚀 Características Clave

### 1. Multiplexor de Ejecución de Doble Estado
- **Capa de Ejecución Nativa (Modo Predeterminado)**:
  Paso directo sin sobrecarga para todos los ejecutables del sistema (`git`, `docker`, `npm`, `cargo`, `python`, `vim`). Conserva la interacción TTY completa, el manejo de señales en tiempo real y la canalización de flujos estándar.
- **Canalización Unificada de Cápsulas (`kps <cmd>` / `kapsel <cmd>`)**:
  Un único punto de entrada para comandos universales, utilidades de complementos y configuraciones del sistema. Elimina los prefijos de ejecución y traduce comandos multiplataforma a primitivas optimizadas para el host sobre la marcha.
- **Autosugerencias Profundas Asíncronas**:
  Predicción de historial en línea atenuada impulsada por un almacén estadístico SQLite persistente y aislado (`~/.kapsel/history.db`). Acepta sugerencias instantáneamente con `→` (Flecha Derecha).

### 2. Autocompletado Dinámico Multi-Shell (Impulsado por Carapace)
- **Cobertura de Más de 1,000 Comandos**:
  La integración directa con [Carapace](https://carapace.sh) permite la finalización de argumentos y contexto de múltiples niveles y múltiples shells (ramas/etiquetas de git, contenedores/imágenes de docker, pods de kubectl, scripts de npm).
- **Arranque Sin Configuración**:
  En el primer lanzamiento, Kapsel arranca silenciosamente el binario oficial de la plataforma en `~/.kapsel/bin/` con **cero permisos administrativos/de root**.

### 3. Especificación de Doble Raíz y Centinela de Colisiones
- **Árboles Raíz con Espacios de Nombres (`kps.yaml` y `kapsel.yaml`)**:
  Compila dinámicamente los componentes integrados principales y las especificaciones de complementos en árboles raíz aislados bajo `kps` y `kapsel`.
- **Centinela de Colisiones del Espacio de Nombres del Host**:
  Protege estrictamente los componentes integrados del shell del host (`alias`, `help`, `install`, `history`, `profile`, `ps`, `kill`, `dir`). Los comandos con posibles colisiones con el host se sellan dentro del espacio de nombres `kps`—**garantizando que los comandos nativos del shell (por ejemplo, `Get-Alias` de PowerShell) permanezcan 100% sin secuestrar**.
- **Finalizaciones de Parámetros Profundos**:
  Escribir `kps alias add <Tab>` ofrece una finalización rica de banderas de múltiples niveles (`--from`, `--to`, `--shell`, `--global`) en cualquier terminal.

### 4. Subsistema de Complementos Modular y a Prueba de Fallos
- **Arquitectura Desacoplada**: Los complementos operan en límites de memoria aislados. Un complemento que funcione mal nunca puede bloquear el Núcleo de Kapsel.
- **Estándar de Especificación Declarativa**: Cada complemento define especificaciones YAML declarativas independientes que cumplen con las especificaciones de Carapace.

### 5. Estética Minimalista de Terminal en Caja
- **Encuadre de Tarjetas**: Demarcación visual clara de entradas y salidas de comandos utilizando un encuadre moderno en caja (`╭─ ❯` y `╰─`).
- **Retroalimentación de Telemetría**: Visualización instantánea de los códigos de salida de ejecución (`✔ 0` o `✘ exit 1`) y tiempo transcurrido preciso de pared (`⏱ 38ms`).
- **Motor Multilingüe Nativo (i18n)**: Localización completa en 7 idiomas (`en`, `zh_CN`, `ja`, `es`, `fr`, `de`, `ru`).

---

## ⚡ Instalación Rápida

Elige el método de instalación que mejor se adapte a tu entorno:

- [📦 Gestores de Paquetes (PyPI / Scoop / Homebrew / APT)](#1-gestores-de-paquetes)
- [💾 Binarios Autónomos Precompilados](#2-binarios-autónomos-precompilados-cero-dependencias)
- [🌐 Instaladores Automatizados de Herramientas](#3-instaladores-automatizados-de-herramientas)
- [🛠️ Compilar desde el Código Fuente](#4-compilar-desde-el-código-fuente)

> 🇨🇳 **Usuarios en China Continental**: Si te encuentras en China y necesitas aceleración mediante espejos de alta velocidad (ghproxy, espejo PyPI de Tsinghua, scripts de descarga domésticos), consulta **[README_zh.md](README_zh.md)** o [docs/INSTALLATION.md](docs/INSTALLATION.md).

---

### 1. 📦 Gestores de Paquetes

#### PyPI (Python 3.9+)

```bash
# Recomendado: Entorno aislado mediante pipx (evita la contaminación global de Python)
pipx install kapsel-cli

# O instalación estándar con pip
pip install --upgrade kapsel-cli
```

#### Windows: Scoop

```powershell
# Añadir el bucket oficial de Kapsel e instalar
scoop bucket add kapsel https://github.com/MrEiu/scoop-bucket
scoop install kapsel
```

#### macOS y Linux: Homebrew

```bash
# Añadir el tap oficial de Kapsel e instalar
brew tap MrEiu/tap
brew install kapsel
```

#### Debian y Ubuntu: APT y DPKG (.deb)

```bash
curl -LO https://github.com/MrEiu/Kapsel/releases/latest/download/kapsel_amd64.deb
sudo dpkg -i kapsel_amd64.deb || sudo apt-get install -f -y
```

---

### 2. 💾 Binarios Autónomos Precompilados (Cero Dependencias)

No se requiere runtime de Python ni gestores de paquetes externos. Simplemente extrae y ejecuta:

| Plataforma / Arquitectura | Artefacto de la Versión | Descarga Oficial de GitHub |
| :--- | :--- | :--- |
| **Windows x86_64** | `kapsel-windows-x86_64.zip` | [Descargar](https://github.com/MrEiu/Kapsel/releases/latest/download/kapsel-windows-x86_64.zip) |
| **Linux x86_64** | `kapsel-linux-x86_64.tar.gz` | [Descargar](https://github.com/MrEiu/Kapsel/releases/latest/download/kapsel-linux-x86_64.tar.gz) |
| **macOS (Universal)** | `kapsel-macos-universal.tar.gz` | [Descargar](https://github.com/MrEiu/Kapsel/releases/latest/download/kapsel-macos-universal.tar.gz) |
| **Debian / Ubuntu** | `kapsel_amd64.deb` | [Descargar](https://github.com/MrEiu/Kapsel/releases/latest/download/kapsel_amd64.deb) |

> 💡 **Consejo de Uso**: Extrae el archivo y coloca `kapsel` (o `kapsel.exe`) y `kps` (o `kps.exe`) en cualquier directorio de tu `PATH` del sistema (como `~/.kapsel/bin` o `/usr/local/bin`).

---

### 3. 🌐 Instaladores Automatizados de Herramientas

Detecta automáticamente tu plataforma, configura Kapsel y ajusta utilidades modernas de línea de comandos (`carapace`, `zoxide`, `mise`, `chsrc`, `aichat`, `pueue`, `chezmoi`, `pet`, `tealdeer`, `fzf`):

```powershell
# Windows (PowerShell):
irm https://raw.githubusercontent.com/MrEiu/Kapsel/master/scripts/install_tools_windows.ps1 | iex
```

```bash
# macOS:
curl -fsSL https://raw.githubusercontent.com/MrEiu/Kapsel/master/scripts/install_tools_macos.sh | bash

# Linux (Debian / Ubuntu / Fedora / Arch):
curl -fsSL https://raw.githubusercontent.com/MrEiu/Kapsel/master/scripts/install_tools_linux.sh | bash
```

---

### 4. 🛠️ Compilar desde el Código Fuente

Ideal para desarrolladores que deseen contribuir al núcleo de Kapsel o desarrollar plugins personalizados:

```bash
git clone https://github.com/MrEiu/Kapsel.git
cd Kapsel
pip install -e .
kps completion sync
```

---

## 🧩 Ecosistema Oficial de Plugins

Kapsel mantiene un conjunto de plugins modular y desacoplado, diseñado para satisfacer flujos de trabajo de ingeniería modernos:

| Plugin | Comando | Tecnología Principal | Descripción |
| :--- | :--- | :--- | :--- |
| **`init`** | `kps init` | **`mise`** (Rust) | Gestor de cadenas de herramientas del proyecto y tiempos de ejecución políglota (reemplaza nvm, pyenv, rbenv). |
| **`portal`** | `kps portal` / `z` | **`zoxide`** (Rust) | Teletransporte de directorios ponderado por frecuencia con navegación difusa. |
| **`shore`** | `kps shore` | **`chsrc`** (C) | Cambiador de espejos automatizado y ultrarrápido (PyPI, Rust, Node, Go, espejos del sistema operativo). |
| **`install`** | `kps install` | **`mpm`** (Python) | Gestor de paquetes CLI unificado que agrega más de 20 gestores de paquetes. |
| **`alias`** | `kps alias` | *Motor Nativo* | Traducción universal de alias de comandos y mapeo cruzado entre múltiples terminales. |
| **`ai`** | `kps ai` | **`aichat`** (Rust) | Copiloto de IA para terminal que admite OpenAI, Claude, Gemini, DeepSeek y Ollama. |
| **`autopilot`**| `kps autopilot`| **`pueue`** (Rust) | Cola de tareas en segundo plano autónoma y gestor de ejecución de daemons de larga duración. |
| **`fuck`** | `kps fuck` | **`thefuck`** (Python) | Corrección inteligente de errores de entrada en terminal y arreglo automatizado de sintaxis. |
| **`help`** | `kps help <cmd>`| **`tealdeer`** (Rust) | Hojas de referencia prácticas de comandos instantáneas y consulta rápida (tldr). |
| **`profile`** | `kps profile` | **`chezmoi`** (Go) | Dotfiles multiplataforma, perfiles de shell y gestor de entorno con secretos cifrados. |
| **`rec`** | `kps rec` | **`pet`** (Go) | Grabador interactivo de fragmentos CLI, parametrizador de argumentos y ejecutor. |

---

## 📊 Matriz de Características y Comparación

| Capacidad de Característica | Kapsel | Shells Estándar (Bash/Zsh/Pwsh) | Starship | Oh-My-Zsh |
| :--- | :---: | :---: | :---: | :---: |
| **Runtime No Invasivo (Cero Mutación de Perfil)** | **Sí** | No | No | No |
| **Completado de Contexto de Comandos 1,000+ (Carapace)** | **Sí** | Plugins manuales | No (Solo prompt) | Parcial (Lento) |
| **Mapeo Multiplataforma Linux-Primero (`kps`)** | **Sí** | No | No | No |
| **Arquitectura de Doble Especificación Raíz (Anti-Colisión)** | **Sí** | No | No | No |
| **Marco de Ejecución de Terminal Encapsulado** | **Sí** | No | Solo prompt | No |
| **Estado de Sandbox Aislado (`~/.kapsel/`)** | **Sí** | Fragmentado | No | Fragmentado |
| **Respuesta de UI Asíncrona Sub-Milisegundo** | **Sí** | Depende | Sí | A menudo Lento |

---

## 📖 Referencia de Comandos

### Modo Shell Interactivo (`kapsel` / `kps`)

Inicie Kapsel como una sesión de shell interactiva:
```bash
kapsel
```

Dentro de la sesión de cápsula, están disponibles los siguientes comandos unificados:

```text
help                   Mostrar el manual de Kapsel, mecanismos de interacción y hoja de referencia de comandos
status                 Inspeccionar el entorno del SO, shell del host activo, rama de Git y estado del sandbox
upgrade [plugin]       Verificación de actualización en dos etapas para Kapsel Core y plugins oficiales con registros de cambios
search [-a]            Buscar y descubrir plugins oficiales con versiones y estados de instalación
enable <plugin>        Activar y habilitar un plugin instalado, sincronizando autocompletados
disable <plugin>       Deshabilitar un plugin activo sin eliminar archivos locales
config                 Inspeccionar o editar la configuración principal (~/.kapsel/config.yaml)
  config path          Imprimir la ruta física del archivo de configuración
  config edit          Abrir la configuración en el editor externo predeterminado
  config get <key>     Recuperar el valor de una clave de configuración
  config set <k> <v>   Actualizar el valor de configuración desde la terminal
  config reload        Recargar la configuración en caliente desde el disco sin reiniciar la sesión
completion             Gestionar, inspeccionar y sincronizar especificaciones declarativas de Carapace
  completion ls        Listar especificaciones de autocompletado activas, ámbitos y estados de montaje
  completion sync      Forzar la compilación y sincronización de especificaciones raíz duales (kps.yaml y kapsel.yaml)
  completion new <cmd> Crear una nueva plantilla de especificación declarativa
  completion path      Mostrar directorios de especificaciones activos
datadir                Inspeccionar o reubicar de forma segura el directorio sandbox de almacenamiento de datos
language <lang>        Cambiar el idioma de la interfaz activa (en, zh_CN, ja, es, fr, de, ru)
toggle                 Alternar el modo de terminal predeterminado de Kapsel (abrir en la primera llamada, cerrar en la segunda)
clear                  Limpiar la pantalla de la terminal y volver a renderizar el banner de encabezado
exit                   Salir limpiamente de Kapsel y volver al shell nativo del host
```

### Ejecución Externa de Una Sola Vez

Ejecute cualquier comando de cápsula o plugin directamente desde su shell estándar:

```bash
# Gestión y Diagnóstico
kps status
kps completion ls
kps config edit

# Comandos de plugins
kps portal ls
kps shore get
kps init use node@22

# Comandos mapeados multiplataforma
kps rm -rf dist/
kps ls -la
```

---

## 🔒 Aislamiento de Directorio y Modelo de Estado

Kapsel se adhiere estrictamente a la **Garantía de Cero Contaminación**. Todos los datos, binarios, cachés y registros residen exclusivamente dentro del directorio sandbox del usuario:

```text
~/.kapsel/
├── config.yaml          # Configuración de UI a nivel de sistema (colores, bordes de tarjetas, idioma)
├── history.db           # Base de datos SQLite persistente que almacena historial de comandos y estadísticas
├── bin/                 # Herramientas binarias independientes en espacio de usuario (carapace, zoxide, mise, chsrc...)
├── specs/               # Especificaciones declarativas de autocompletado personalizadas del usuario
├── plugins/             # Paquetes de plugins oficiales y de la comunidad instalados
└── logs/                # Registros de sesión y diagnósticos de fallos
```

---

## 🧪 Pruebas y Aseguramiento de Calidad

El código base de Kapsel garantiza una cobertura de pruebas exhaustiva con verificaciones estrictas de tipos y entornos aislados:

```bash
# Clonar el repositorio
git clone https://github.com/MrEiu/Kapsel.git
cd Kapsel

# Instalar dependencias de prueba
pip install -e ".[test]"

# Ejecutar la suite completa de pruebas
pytest tests/ -v
```

Las 79 pruebas unitarias automatizadas validan el descubrimiento del gestor de especificaciones, el bloqueo de centinelas de colisión, la integración de carapace, los ciclos de vida de los complementos y la resolución de i18n.

---

## 🤝 Contribuciones y Comunidad

¡Las contribuciones son bienvenidas!
- Revisa los [issues](https://github.com/MrEiu/Kapsel/issues) para encontrar tareas o reportar errores.
- Para desarrollar o enviar plugins, consulta la [Guía de Plugins](https://github.com/MrEiu/plugins).

---

## 📄 Licencia

Kapsel es un software de código abierto licenciado bajo la **[Licencia MIT](LICENSE)**.

<div align="center">
  <sub>Construido con ergonomía moderna de terminal por MrEiu y el Equipo de Código Abierto de Kapsel.</sub>
</div>
