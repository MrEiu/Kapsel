#!/usr/bin/env bash
# ==============================================================================
# Kapsel - Universal Cross-Platform Installer Dispatcher
# Generated automatically by scripts/generate_installers.py - DO NOT EDIT DIRECTLY!
#
# Single universal command for macOS, Linux, and Windows (Git Bash):
#   curl -fsSL https://raw.githubusercontent.com/MrEiu/Kapsel/master/scripts/install.sh | bash
#
# Options:
#   --lite, -l   Install Lightweight Edition (Core + Carapace autocompletion)
#   --full, -f   Install Full Edition (Core + Package Manager + 11 Plugins)
# ==============================================================================

set -e

# ANSI Colors
CYAN='\033[38;5;51m'
SKY='\033[38;5;39m'
BLUE='\033[38;5;33m'
GREEN='\033[38;5;48m'
PURPLE='\033[38;5;141m'
AMBER='\033[38;5;214m'
RED='\033[38;5;203m'
DIM='\033[38;5;244m'
BOLD='\033[1m'
RESET='\033[0m'

EDITION=""

for arg in "$@"; do
    case "${arg}" in
        --lite|-l)
            EDITION="lite"
            ;;
        --full|-f)
            EDITION="full"
            ;;
        --help|-h)
            echo "Kapsel Universal Installer (v0.2.0)"
            echo ""
            echo "Usage: curl -fsSL <url> | bash -s -- [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --lite, -l    Install Lightweight Edition (Core Kapsel CLI + Carapace autocompletion)"
            echo "  --full, -f    Install Full Edition (Core + Package Manager + 11 Official Plugins)"
            echo "  --help, -h    Show this help message"
            exit 0
            ;;
    esac
done

# Detect Operating System Platform
OS_RAW="$(uname -s)"
TARGET_OS=""

case "${OS_RAW}" in
    Darwin*)
        TARGET_OS="macos"
        ;;
    Linux*)
        TARGET_OS="linux"
        ;;
    MINGW*|MSYS*|CYGWIN*)
        TARGET_OS="windows"
        ;;
    *)
        echo -e "${RED}✘ Error:${RESET} Unsupported operating system: ${OS_RAW}"
        echo "Please visit https://github.com/MrEiu/Kapsel for manual installation instructions."
        exit 1
        ;;
esac

# If edition not specified via flags, check interactive terminal
if [ -z "${EDITION}" ]; then
    if [ -c /dev/tty ]; then
        echo ""
        echo -e "${CYAN}╭────────────────────────────────────────────────────────────────────────╮${RESET}"
        echo -e "${CYAN}│${SKY}  _  __                 _                                           ${CYAN}│${RESET}"
        echo -e "${CYAN}│${SKY} | |/ /__ _ _ __  ___  | |   ${BOLD}${CYAN}⚡ KAPSEL CLI${RESET}${DIM} (v0.2.0)                  ${CYAN}│${RESET}"
        echo -e "${CYAN}│${SKY} | ' // _\` | '_ \/ __| | |   ${GREEN} Next-Gen Intelligent Terminal Capsule ${CYAN}│${RESET}"
        echo -e "${CYAN}│${SKY} |_|\_\__,_| .__/|___/ |_|   ${DIM} https://github.com/MrEiu/Kapsel          ${CYAN}│${RESET}"
        echo -e "${CYAN}│${SKY}           |_|                                                         ${CYAN}│${RESET}"
        echo -e "${CYAN}├────────────────────────────────────────────────────────────────────────┤${RESET}"
        echo -e "${CYAN}│${BOLD}  Please select your installation edition:                               ${CYAN}│${RESET}"
        echo -e "${CYAN}│                                                                        │${RESET}"
        echo -e "${CYAN}│  ${GREEN}[1] Lightweight Edition${RESET}${DIM} (Core + Carapace completions) ~20MB         ${CYAN}│${RESET}"
        echo -e "${CYAN}│  ${PURPLE}[2] Full Toolchain Edition${RESET}${BOLD} (Core + Package Manager + 11 Plugins) [Default] ${CYAN}│${RESET}"
        echo -e "${CYAN}│                                                                        │${RESET}"
        echo -e "${CYAN}╰────────────────────────────────────────────────────────────────────────╯${RESET}"
        read -r -p "Enter selection [1 or 2, default 2]: " choice < /dev/tty
        if [ "${choice}" = "1" ]; then
            EDITION="lite"
        else
            EDITION="full"
        fi
    else
        EDITION="full"
    fi
fi

# Windows Delegation (when run from Git Bash / MSYS)
if [ "${TARGET_OS}" = "windows" ]; then
    echo -e "${SKY}● Detected Windows environment under ${OS_RAW}. Delegating to PowerShell installer...${RESET}"
    WIN_FLAG="-Full"
    if [ "${EDITION}" = "lite" ]; then
        WIN_FLAG="-Lite"
    fi

    powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "& { \$(Invoke-RestMethod -Uri 'https://raw.githubusercontent.com/MrEiu/Kapsel/master/scripts/install_windows.ps1') } ${WIN_FLAG}"
    exit $?
fi

# Local vs Remote Dispatch for POSIX (macOS & Linux)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd || echo "")"
LOCAL_SCRIPT=""

SPECIFIC_SCRIPT_NAME="install_${TARGET_OS}.sh"
REMOTE_URL="https://raw.githubusercontent.com/MrEiu/Kapsel/master/scripts/${SPECIFIC_SCRIPT_NAME}"

if [ -n "${SCRIPT_DIR}" ] && [ -f "${SCRIPT_DIR}/${SPECIFIC_SCRIPT_NAME}" ]; then
    LOCAL_SCRIPT="${SCRIPT_DIR}/${SPECIFIC_SCRIPT_NAME}"
fi

echo -e "${SKY}● Platform detected: ${BOLD}${TARGET_OS}${RESET}${SKY} | Edition: ${BOLD}${EDITION}${RESET}"
echo -e "${DIM}  Fetching ${SPECIFIC_SCRIPT_NAME}...${RESET}\n"

if [ -n "${LOCAL_SCRIPT}" ]; then
    bash "${LOCAL_SCRIPT}" "--${EDITION}"
else
    curl -fsSL "${REMOTE_URL}" | bash -s -- "--${EDITION}"
fi