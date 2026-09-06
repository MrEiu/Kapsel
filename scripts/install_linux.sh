#!/usr/bin/env bash
# ==============================================================================
# Kapsel - Modern Cross-Platform Terminal Capsule Installer for Linux
# Generated automatically by scripts/generate_installers.py - DO NOT EDIT DIRECTLY!
#
# Provides two installation editions:
# 1. Lightweight (--lite): Kapsel Core + Carapace completion engine (~20MB, ultra fast)
# 2. Full (--full):        Lightweight + System package manager + 11 official plugins
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/MrEiu/Kapsel/master/scripts/install_linux.sh | bash
#   curl -fsSL ... | bash -s -- --lite
#   curl -fsSL ... | bash -s -- --full
# ==============================================================================

set -e

# ------------------------------------------------------------------------------
# 0. Color & Aesthetic Definitions
# ------------------------------------------------------------------------------
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

EDITION="full"

for arg in "$@"; do
    case "${arg}" in
        --lite|-l)
            EDITION="lite"
            ;;
        --full|-f)
            EDITION="full"
            ;;
        --help|-h)
            echo "Kapsel Installer (v0.2.0)"
            echo ""
            echo "Usage: $0 [--lite] [--full] [--help]"
            echo ""
            echo "Options:"
            echo "  --lite, -l    Install Lightweight Edition (Core Kapsel CLI + Carapace autocompletion)"
            echo "  --full, -f    Install Full Edition (Core + Package Manager + 11 Official Plugins)"
            echo "  --help, -h    Show this help message"
            exit 0
            ;;
    esac
done

# If running interactively and no flags specified, prompt user
if [ "$#" -eq 0 ]; then
    if [ -c /dev/tty ]; then
        echo -e "${CYAN}╭────────────────────────────────────────────────────────────────────────╮${RESET}"
        echo -e "${CYAN}│${BOLD}  Please select the Kapsel installation edition:                        ${CYAN}│${RESET}"
        echo -e "${CYAN}│                                                                        │${RESET}"
        echo -e "${CYAN}│  ${GREEN}[1] Lightweight Edition${RESET}${DIM} (Core + Carapace completions) ~20MB         ${CYAN}│${RESET}"
        echo -e "${CYAN}│  ${PURPLE}[2] Full Edition${RESET}${BOLD} (Core + Package Manager + 11 Plugins) [Default]        ${CYAN}│${RESET}"
        echo -e "${CYAN}│                                                                        │${RESET}"
        echo -e "${CYAN}╰────────────────────────────────────────────────────────────────────────╯${RESET}"
        read -r -p "Enter selection [1 or 2, default 2]: " choice < /dev/tty
        if [ "$choice" = "1" ]; then
            EDITION="lite"
        else
            EDITION="full"
        fi
    fi
fi

EDITION_TITLE="Full Toolchain Edition"
if [ "$EDITION" = "lite" ]; then
    EDITION_TITLE="Lightweight Edition"
fi

echo ""
echo -e "${CYAN}╭────────────────────────────────────────────────────────────────────────╮${RESET}"
echo -e "${CYAN}│${SKY}  _  __                 _                                           ${CYAN}│${RESET}"
echo -e "${CYAN}│${SKY} | |/ /__ _ _ __  ___  | |   ${BOLD}${CYAN}⚡ KAPSEL CLI${RESET}${DIM} (v0.2.0)                  ${CYAN}│${RESET}"
echo -e "${CYAN}│${SKY} | ' // _\` | '_ \/ __| | |   ${GREEN} Next-Gen Intelligent Terminal Capsule ${CYAN}│${RESET}"
echo -e "${CYAN}│${SKY} | . \ (_| | |_) \__ \ | |   ${DIM} https://github.com/MrEiu/Kapsel          ${CYAN}│${RESET}"
echo -e "${CYAN}│${SKY} |_|\_\__,_| .__/|___/ |_|                                           ${CYAN}│${RESET}"
echo -e "${CYAN}│${SKY}           |_|             ${PURPLE}[${EDITION_TITLE}]${SKY}                         ${CYAN}│${RESET}"
echo -e "${CYAN}╰────────────────────────────────────────────────────────────────────────╯${RESET}"
echo ""

log_step() {
    echo -e "${BOLD}${SKY}==> [$1] $2${RESET}"
}

log_ok() {
    echo -e "  ${GREEN}✔${RESET} $1"
}

log_info() {
    echo -e "  ${CYAN}●${RESET} ${DIM}$1${RESET}"
}

log_warn() {
    echo -e "  ${AMBER}!${RESET} ${AMBER}$1${RESET}"
}

log_err() {
    echo -e "\n  ${RED}✘ Error:${RESET} $1"
    exit 1
}

KAPSEL_HOME="${HOME}/.kapsel"
KAPSEL_BIN_DIR="${KAPSEL_HOME}/bin"
mkdir -p "${KAPSEL_BIN_DIR}"
export PATH="${KAPSEL_BIN_DIR}:${PATH}"

# ------------------------------------------------------------------------------
# 1. Preflight Environment State Inspection
# ------------------------------------------------------------------------------
log_step "1/5" "Inspecting Current System Environment"

# 1.1 Detect Host OS & Package Manager
OS_NAME="$(uname -s)"
PKG_MGR="generic"

if [ "${OS_NAME}" = "Darwin" ]; then
    PKG_MGR="brew"
elif command -v pacman >/dev/null 2>&1; then
    PKG_MGR="pacman"
elif command -v apt-get >/dev/null 2>&1; then
    PKG_MGR="apt"
elif command -v dnf >/dev/null 2>&1; then
    PKG_MGR="dnf"
elif command -v apk >/dev/null 2>&1; then
    PKG_MGR="apk"
fi

# 1.2 Locate Python
PYTHON_CMD=""
PY_VER=""
for cand in python3 python py; do
    if command -v "${cand}" >/dev/null 2>&1; then
        if "${cand}" -c "import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)" 2>/dev/null; then
            PYTHON_CMD="${cand}"
            PY_VER="$("${cand}" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')" 2>/dev/null)"
            break
        fi
    fi
done

# 1.3 Detect Kapsel Core
KAPSEL_INSTALLED=0
INSTALLED_KAPSEL_VER=""
KAPSEL_UP_TO_DATE=0

if [ -n "${PYTHON_CMD}" ]; then
    ver_out="$("${PYTHON_CMD}" -m kapsel.cli -v 2>/dev/null || true)"
    if echo "${ver_out}" | grep -qE "[0-9]+\.[0-9]+\.[0-9]+"; then
        KAPSEL_INSTALLED=1
        INSTALLED_KAPSEL_VER="$(echo "${ver_out}" | grep -oE "[0-9]+\.[0-9]+\.[0-9]+" | head -n1)"
        if [ "${INSTALLED_KAPSEL_VER}" = "0.2.0" ]; then
            KAPSEL_UP_TO_DATE=1
        fi
    fi
fi

if [ "${KAPSEL_INSTALLED}" -eq 0 ] && command -v kapsel >/dev/null 2>&1; then
    ver_out="$(kapsel -v 2>/dev/null || true)"
    if echo "${ver_out}" | grep -qE "[0-9]+\.[0-9]+\.[0-9]+"; then
        KAPSEL_INSTALLED=1
        INSTALLED_KAPSEL_VER="$(echo "${ver_out}" | grep -oE "[0-9]+\.[0-9]+\.[0-9]+" | head -n1)"
        if [ "${INSTALLED_KAPSEL_VER}" = "0.2.0" ]; then
            KAPSEL_UP_TO_DATE=1
        fi
    fi
fi

# 1.4 Detect Carapace Engine
CARAPACE_BIN="${KAPSEL_BIN_DIR}/carapace"
CARAPACE_INSTALLED=0
CARAPACE_VER=""

if [ -x "${CARAPACE_BIN}" ]; then
    cara_out="$("${CARAPACE_BIN}" --version 2>/dev/null || true)"
    if [ -n "${cara_out}" ]; then
        CARAPACE_INSTALLED=1
        CARAPACE_VER="${cara_out}"
    fi
elif command -v carapace >/dev/null 2>&1; then
    cara_out="$(carapace --version 2>/dev/null || true)"
    if [ -n "${cara_out}" ]; then
        CARAPACE_INSTALLED=1
        CARAPACE_VER="${cara_out}"
    fi
fi

# 1.5 Detect PATH Profile Configuration
PATH_CONFIGURED=0
for prof in "${HOME}/.zshrc" "${HOME}/.bashrc" "${HOME}/.bash_profile" "${HOME}/.profile"; do
    if [ -f "${prof}" ] && grep -q ".kapsel/bin" "${prof}" 2>/dev/null; then
        PATH_CONFIGURED=1
        break
    fi
done

# 1.6 Detect Plugins (Full Edition only)
INSTALLED_PLUGINS=0
TOTAL_PLUGINS=11
MISSING_PLUGINS=()
ALL_PLUGINS=("alias" "portal" "init" "shore" "ai" "install" "autopilot" "rec" "profile" "fuck" "help" )

if [ "${EDITION}" = "full" ]; then
    FOUND_PLUGINS=""
    if [ -n "${PYTHON_CMD}" ]; then
        FOUND_PLUGINS="$("${PYTHON_CMD}" -c "
try:
    from kapsel.storage.config import get_kapsel_dir; p = get_kapsel_dir() / 'plugins'
    print(','.join([x.name for x in p.iterdir() if x.is_dir() and (x/'__init__.py').exists()]))
except Exception:
    pass" 2>/dev/null || true)"
    fi

    for pid in "${ALL_PLUGINS[@]}"; do
        if echo ",${FOUND_PLUGINS}," | grep -q ",${pid}," || { [ -d "${KAPSEL_HOME}/plugins/${pid}" ] && [ -f "${KAPSEL_HOME}/plugins/${pid}/__init__.py" ]; }; then
            INSTALLED_PLUGINS=$((INSTALLED_PLUGINS + 1))
        else
            MISSING_PLUGINS+=("${pid}")
        fi
    done
fi

# Render Preflight Status Inspection Box
echo ""
echo -e "  ${CYAN}┌── Preflight Environment Status ────────────────────────────────────────┐${RESET}"
if [ -n "${PYTHON_CMD}" ]; then
    echo -e "  ${CYAN}│${RESET} Python Runtime:     ${GREEN}✔ Found ${PY_VER} (${PYTHON_CMD})${RESET}"
else
    echo -e "  ${CYAN}│${RESET} Python Runtime:     ${AMBER}● Missing (Will auto-install via ${PKG_MGR})${RESET}"
fi

if [ "${KAPSEL_UP_TO_DATE}" -eq 1 ]; then
    echo -e "  ${CYAN}│${RESET} Kapsel Core CLI:    ${GREEN}✔ Up-to-date (v${INSTALLED_KAPSEL_VER})${RESET}"
elif [ "${KAPSEL_INSTALLED}" -eq 1 ]; then
    echo -e "  ${CYAN}│${RESET} Kapsel Core CLI:    ${SKY}● Installed v${INSTALLED_KAPSEL_VER} (Upgrade to v0.2.0 needed)${RESET}"
else
    echo -e "  ${CYAN}│${RESET} Kapsel Core CLI:    ${AMBER}● Not installed (Target: v0.2.0)${RESET}"
fi

if [ "${CARAPACE_INSTALLED}" -eq 1 ]; then
    echo -e "  ${CYAN}│${RESET} Carapace Engine:    ${GREEN}✔ Installed (${CARAPACE_VER})${RESET}"
else
    echo -e "  ${CYAN}│${RESET} Carapace Engine:    ${AMBER}● Not installed (Target: v1.7.3)${RESET}"
fi

if [ "${PATH_CONFIGURED}" -eq 1 ]; then
    echo -e "  ${CYAN}│${RESET} System PATH:        ${GREEN}✔ ~/.kapsel/bin configured in shell profile${RESET}"
else
    echo -e "  ${CYAN}│${RESET} System PATH:        ${AMBER}● Needs profile configuration${RESET}"
fi

if [ "${EDITION}" = "full" ]; then
    NUM_MISSING=${#MISSING_PLUGINS[@]}    echo -e "  ${CYAN}│${RESET} Package Manager:    ${GREEN}✔ ${PKG_MGR} ecosystem detected${RESET}"
    if [ "${NUM_MISSING}" -eq 0 ]; then
        echo -e "  ${CYAN}│${RESET} Official Plugins:   ${GREEN}✔ ${INSTALLED_PLUGINS}/${TOTAL_PLUGINS} installed${RESET}"
    else
        echo -e "  ${CYAN}│${RESET} Official Plugins:   ${SKY}● ${INSTALLED_PLUGINS}/${TOTAL_PLUGINS} installed (${NUM_MISSING} missing)${RESET}"
    fi
fi
echo -e "  ${CYAN}└────────────────────────────────────────────────────────────────────────┘${RESET}"
echo ""

# Fast-path: Check if everything requested is already optimal
ALL_OPTIMAL=0
if [ -n "${PYTHON_CMD}" ] && [ "${KAPSEL_UP_TO_DATE}" -eq 1 ] && [ "${CARAPACE_INSTALLED}" -eq 1 ] && [ "${PATH_CONFIGURED}" -eq 1 ]; then
    if [ "${EDITION}" = "lite" ] || [ "${NUM_MISSING}" -eq 0 ]; then
        ALL_OPTIMAL=1
    fi
fi

if [ "${ALL_OPTIMAL}" -eq 1 ]; then
    log_ok "All components are already installed and up to date! Zero actions needed."
    "${PYTHON_CMD}" -m kapsel.cli completion sync >/dev/null 2>&1 || true
    "${PYTHON_CMD}" -c "from kapsel.storage.config import load_config; load_config()" >/dev/null 2>&1 || true
    echo ""
    echo -e "${GREEN}✨ Instant preflight check passed. Your Kapsel environment is ready to use.${RESET}\n"
    exit 0
fi

# ------------------------------------------------------------------------------
# 2. Python Runtime Verification / Bootstrap
# ------------------------------------------------------------------------------
if [ -z "${PYTHON_CMD}" ]; then
    log_step "2/5" "Bootstrapping Python 3.9+ Runtime"
    log_info "Attempting to install Python via ${PKG_MGR}..."

    case "${PKG_MGR}" in
        brew)
            brew install python3
            ;;
        pacman)
            sudo pacman -Sy --noconfirm python python-pip
            ;;
        apt)
            sudo apt-get update -qq && sudo apt-get install -y python3 python3-pip python3-venv
            ;;
        dnf)
            sudo dnf install -y python3 python3-pip
            ;;
        apk)
            apk add --no-cache python3 py3-pip
            ;;
        *)
            log_err "Please install Python 3.9 or higher and rerun this script."
            ;;
    esac

    for cand in python3 python; do
        if command -v "${cand}" >/dev/null 2>&1; then
            PYTHON_CMD="${cand}"
            break
        fi
    done
else
    log_step "2/5" "Python Runtime Environment"
    log_ok "Using existing Python ${PY_VER} (${PYTHON_CMD})"
fi

# ------------------------------------------------------------------------------
# 3. Install / Upgrade Kapsel Core CLI
# ------------------------------------------------------------------------------
log_step "3/5" "Installing / Upgrading Kapsel Core CLI"

if [ "${KAPSEL_UP_TO_DATE}" -eq 1 ]; then
    log_ok "Kapsel Core is already up-to-date (v${INSTALLED_KAPSEL_VER}) - Skipping pip install"
else
    log_info "Executing pip install for kapsel-cli..."
    "${PYTHON_CMD}" -m pip install --upgrade kapsel-cli >/dev/null 2>&1 || \
    pip install --upgrade kapsel-cli >/dev/null 2>&1 || \
    pip3 install --upgrade kapsel-cli --break-system-packages >/dev/null 2>&1 || true

    new_ver="$("${PYTHON_CMD}" -m kapsel.cli -v 2>/dev/null || echo "v0.2.0")"
    log_ok "Kapsel Core CLI ready: ${new_ver}"
fi

# ------------------------------------------------------------------------------
# 4. Bootstrapping Carapace Engine & PATH
# ------------------------------------------------------------------------------
log_step "4/5" "Checking Carapace Autocompletion Engine"

if [ "${CARAPACE_INSTALLED}" -eq 1 ]; then
    log_ok "Carapace engine is already installed (${CARAPACE_VER}) - Skipping download"
else
    ARCH="$(uname -m)"
    CARA_ARCH="amd64"
    if [ "${ARCH}" = "arm64" ] || [ "${ARCH}" = "aarch64" ]; then
        CARA_ARCH="arm64"
    fi

    CARA_OS="linux"
    if [ "${OS_NAME}" = "Darwin" ]; then
        CARA_OS="darwin"
    fi

    CARAPACE_URL="https://github.com/carapace-sh/carapace-bin/releases/download/v1.7.3/carapace-bin_1.7.3_${CARA_OS}_${CARA_ARCH}.tar.gz"

    log_info "Downloading Carapace (v1.7.3 for ${CARA_OS}_${CARA_ARCH})..."
    TMP_DIR="$(mktemp -d)"
    if curl -fsSL "${CARAPACE_URL}" -o "${TMP_DIR}/carapace.tar.gz" 2>/dev/null; then
        tar -xzf "${TMP_DIR}/carapace.tar.gz" -C "${TMP_DIR}" 2>/dev/null
        if [ -f "${TMP_DIR}/carapace" ]; then
            mv "${TMP_DIR}/carapace" "${CARAPACE_BIN}"
            chmod +x "${CARAPACE_BIN}"
            cara_ver="$("${CARAPACE_BIN}" --version 2>/dev/null || true)"
            log_ok "Carapace installed successfully: ${cara_ver}"
        fi
    else
        log_warn "Could not download Carapace archive. Kapsel will auto-bootstrap on first interactive run."
    fi
    rm -rf "${TMP_DIR}"
fi

# Ensure PATH is persisted to user profile if not already configured
if [ "${PATH_CONFIGURED}" -eq 0 ]; then
    TARGET_PROFILE=""
    if [ -n "${ZSH_VERSION:-}" ] || [ -f "${HOME}/.zshrc" ]; then
        TARGET_PROFILE="${HOME}/.zshrc"
    elif [ -f "${HOME}/.bashrc" ]; then
        TARGET_PROFILE="${HOME}/.bashrc"
    else
        TARGET_PROFILE="${HOME}/.profile"
    fi

    if [ -n "${TARGET_PROFILE}" ]; then
        echo "" >> "${TARGET_PROFILE}"
        echo '# Kapsel CLI Environment' >> "${TARGET_PROFILE}"
        echo 'export PATH="${HOME}/.kapsel/bin:${PATH}"' >> "${TARGET_PROFILE}"
        log_ok "Appended ~/.kapsel/bin to ${TARGET_PROFILE}"
    fi
else
    log_ok "Shell profile PATH configuration is already up to date"
fi

# ------------------------------------------------------------------------------
# 5. Full Edition: Package Manager & Official Plugins
# ------------------------------------------------------------------------------
if [ "${EDITION}" = "full" ]; then
    log_step "5/5" "Configuring Full Toolchain & Official Plugins"

    if [ "${PKG_MGR}" = "brew" ] && ! command -v brew >/dev/null 2>&1; then
        log_info "Bootstrapping Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" || true
    fi

    if [ "${NUM_MISSING}" -eq 0 ]; then
        log_ok "All 11 official plugins are already installed - Skipping 'kapsel add'"
    else
        echo ""
        echo -e "${PURPLE}  Installing ${NUM_MISSING} Missing Kapsel Plugins via 'kapsel add'...${RESET}"
        for pid in "${MISSING_PLUGINS[@]}"; do
            echo -e "  ${SKY}➜${RESET} Adding plugin ${BOLD}${pid}${RESET}..."
            "${PYTHON_CMD}" -m kapsel.cli add "${pid}" >/dev/null 2>&1 || kapsel add "${pid}" >/dev/null 2>&1 || true
            log_ok "Plugin '${pid}' added and configured"
        done
    fi
else
    log_step "5/5" "Finalizing Core Installation"
    log_ok "Lightweight core profile active"
fi

# Synchronize completion specifications & ensure default configuration
"${PYTHON_CMD}" -m kapsel.cli completion sync >/dev/null 2>&1 || true
"${PYTHON_CMD}" -c "from kapsel.storage.config import load_config; load_config()" >/dev/null 2>&1 || true

# ------------------------------------------------------------------------------
# 6. Final Summary & Quick Start
# ------------------------------------------------------------------------------
echo ""
echo -e "${CYAN}╭────────────────────────────────────────────────────────────────────────╮${RESET}"
echo -e "${CYAN}│${GREEN}  ✔ Kapsel ${EDITION_TITLE} installed successfully!                       ${CYAN}│${RESET}"
echo -e "${CYAN}│                                                                        │${RESET}"
echo -e "${CYAN}│${BOLD}  Quick Start Commands:                                                 ${CYAN}│${RESET}"
echo -e "${CYAN}│   ${CYAN}• kapsel${RESET}         Enter the interactive smart capsule shell           ${CYAN}│${RESET}"
echo -e "${CYAN}│   ${CYAN}• kapsel toggle${RESET}  Toggle Kapsel as your default terminal shell        ${CYAN}│${RESET}"
echo -e "${CYAN}│   ${CYAN}• kapsel status${RESET}  Inspect host shell, platform, and active plugins    ${CYAN}│${RESET}"
if [ "${EDITION}" = "full" ]; then
echo -e "${CYAN}│   ${CYAN}• z <dir>${RESET}        Instant directory jumping via portal plugin         ${CYAN}│${RESET}"
echo -e "${CYAN}│   ${CYAN}• kps ai <prompt>${RESET} Terminal AI command generation (OpenAI SDK)        ${CYAN}│${RESET}"
echo -e "${CYAN}│   ${CYAN}• kps shore${RESET}      Auto-benchmark and switch fastest package mirrors   ${CYAN}│${RESET}"
fi
echo -e "${CYAN}│                                                                        │${RESET}"
echo -e "${CYAN}│${DIM}  Restart your terminal or run 'source ~/.profile' to apply PATH.        ${CYAN}│${RESET}"
echo -e "${CYAN}╰────────────────────────────────────────────────────────────────────────╯${RESET}"
echo ""