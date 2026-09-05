#!/usr/bin/env bash
# ==============================================================================
# Kapsel - Complete Toolchain Installer for macOS
# Installs all required terminal utilities for Kapsel Core and official plugins:
# - Core: carapace (carapace-bin)
# - Plugins: zoxide, mise, chsrc, aichat, pueue, chezmoi, pet, tealdeer, fzf
# - Python CLI: meta-package-manager (mpm), thefuck
#
# Adheres to Kapsel Dependency Philosophy:
# Homebrew first -> Standard pipx for Python CLI tools -> Zero virtualenvs.
# ==============================================================================

set -e

INSTALL_ULTRA=false
for arg in "$@"; do
    case "${arg}" in
        --ultra|-u)
            INSTALL_ULTRA=true
            ;;
    esac
done

RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
DIM='\033[2m'
BOLD='\033[1m'
RESET='\033[0m'

echo -e "${CYAN}${BOLD}============================================================${RESET}"
echo -e "${CYAN}${BOLD}   Kapsel All-in-One Toolchain Installer (macOS)            ${RESET}"
echo -e "${CYAN}${BOLD}============================================================${RESET}"

KAPSEL_BIN_DIR="${HOME}/.kapsel/bin"
mkdir -p "${KAPSEL_BIN_DIR}"

log_step() {
    echo -e "\n${CYAN}====> $1${RESET}"
}

log_ok() {
    echo -e "  ${GREEN}[OK] $1${RESET}"
}

log_info() {
    echo -e "  ${YELLOW}[INFO] $1${RESET}"
}

log_warn() {
    echo -e "  ${RED}[WARN] $1${RESET}"
}

# ------------------------------------------------------------------------------
# 1. Check and Bootstrap Homebrew
# ------------------------------------------------------------------------------
log_step "Checking Package Manager: Homebrew"

if ! command -v brew >/dev/null 2>&1; then
    log_info "Homebrew is not installed. Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
    # Configure Homebrew in current session for Apple Silicon or Intel
    if [ -f "/opt/homebrew/bin/brew" ]; then
        eval "$(/opt/homebrew/bin/brew shellenv)"
    elif [ -f "/usr/local/bin/brew" ]; then
        eval "$(/usr/local/bin/brew shellenv)"
    fi
    log_ok "Homebrew installed successfully."
else
    log_ok "Homebrew is already installed."
fi

# ------------------------------------------------------------------------------
# 2. Install Core & Plugin Binary Tools via Homebrew
# ------------------------------------------------------------------------------
log_step "Installing Binary Tools via Homebrew"

BREW_TOOLS=(
    "carapace"
    "zoxide"
    "mise"
    "aichat"
    "pueue"
    "chezmoi"
    "pet"
    "tealdeer"
    "fzf"
    "thefuck"
    "pipx"
)

for tool in "${BREW_TOOLS[@]}"; do
    if command -v "${tool}" >/dev/null 2>&1; then
        log_ok "${tool} is already installed."
    else
        log_info "Installing ${tool} via Homebrew..."
        brew install "${tool}" || log_warn "Failed to install ${tool} via brew."
    fi
done

# ------------------------------------------------------------------------------
# 2b. Optional: Ultra Modern CLI Tools (if --ultra passed)
# ------------------------------------------------------------------------------
if [ "${INSTALL_ULTRA}" = true ]; then
    log_step "Installing Ultra Modern CLI Tools (--ultra via Homebrew)"
    ULTRA_TOOLS=(
        "eza"
        "bat"
        "ripgrep"
        "fd"
        "procs"
        "dust"
        "bottom"
        "gping"
        "jq"
        "sd"
        "lazygit"
        "hyperfine"
    )
    for tool in "${ULTRA_TOOLS[@]}"; do
        if command -v "${tool}" >/dev/null 2>&1; then
            log_ok "${tool} is already installed."
        else
            log_info "Installing ${tool} via Homebrew..."
            brew install "${tool}" || log_warn "Failed to install ${tool} via brew."
        fi
    done
fi

# ------------------------------------------------------------------------------
# 3. Install chsrc (Fast Mirror Switcher)
# ------------------------------------------------------------------------------
log_step "Installing chsrc (Fast Mirror Switcher)"

if command -v chsrc >/dev/null 2>&1 || [ -f "${KAPSEL_BIN_DIR}/chsrc" ]; then
    log_ok "chsrc is already installed."
else
    log_info "Installing chsrc via official installer..."
    curl -sSL https://chsrc.run/install | bash || {
        log_warn "curl installer failed. Downloading latest binary into ~/.kapsel/bin..."
        ARCH="$(uname -m)"
        CHSRC_URL="https://github.com/RubyMetric/chsrc/releases/latest/download/chsrc-x64-macos"
        if [ "${ARCH}" = "arm64" ] || [ "${ARCH}" = "aarch64" ]; then
            CHSRC_URL="https://github.com/RubyMetric/chsrc/releases/latest/download/chsrc-arm64-macos"
        fi
        curl -fsSL "${CHSRC_URL}" -o "${KAPSEL_BIN_DIR}/chsrc"
        chmod +x "${KAPSEL_BIN_DIR}/chsrc"
    }
    log_ok "chsrc installed."
fi

# ------------------------------------------------------------------------------
# 4. Install Python Tools (mpm)
# ------------------------------------------------------------------------------
log_step "Installing Python CLI Tools (mpm)"

if command -v mpm >/dev/null 2>&1; then
    log_ok "mpm (meta-package-manager) is already installed."
else
    log_info "Installing mpm via pipx..."
    if command -v pipx >/dev/null 2>&1; then
        pipx ensurepath --force >/dev/null 2>&1 || true
        pipx install meta-package-manager || pip3 install --user meta-package-manager
    else
        python3 -m pip install --user meta-package-manager
    fi
    log_ok "mpm installed."
fi

# ------------------------------------------------------------------------------
# 5. Configure Shell PATH
# ------------------------------------------------------------------------------
log_step "Configuring Shell Environment"

SHELL_RC=""
if [ -n "$ZSH_VERSION" ] || [ "$SHELL" = "/bin/zsh" ]; then
    SHELL_RC="${HOME}/.zshrc"
elif [ -n "$BASH_VERSION" ] || [ "$SHELL" = "/bin/bash" ]; then
    SHELL_RC="${HOME}/.bash_profile"
fi

if [ -n "${SHELL_RC}" ] && [ -f "${SHELL_RC}" ]; then
    if ! grep -q "\.kapsel/bin" "${SHELL_RC}"; then
        echo 'export PATH="${HOME}/.kapsel/bin:${PATH}"' >> "${SHELL_RC}"
        log_ok "Added ~/.kapsel/bin to ${SHELL_RC}."
    else
        log_ok "~/.kapsel/bin is already configured in ${SHELL_RC}."
    fi
fi

# ------------------------------------------------------------------------------
# 6. Trigger Spec Synchronization
# ------------------------------------------------------------------------------
log_step "Synchronizing Kapsel Completion Specifications"

if command -v kps >/dev/null 2>&1; then
    kps completion sync
else
    python3 -c "from kapsel.completion.spec_manager import CarapaceSpecManager; CarapaceSpecManager().sync_specs(force=True)" 2>/dev/null || true
fi

echo -e "\n${GREEN}${BOLD}============================================================${RESET}"
echo -e "${GREEN}${BOLD}   All Kapsel Tools Installation Complete!                  ${RESET}"
echo -e "${GREEN}${BOLD}============================================================${RESET}"
echo -e "You can now run 'kapsel' or 'kps status' to enjoy the full experience."
echo -e "Tip: Run 'kps alias ultra' or rerun with '--ultra' to install modern tools (eza, bat, rg, fd, etc.).\n"
