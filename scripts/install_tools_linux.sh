#!/usr/bin/env bash
# ==============================================================================
# Kapsel - Complete Toolchain Installer for Linux
# Supports Debian/Ubuntu (apt), Arch Linux (pacman/yay), and Fedora/RHEL (dnf).
# Installs all required terminal utilities for Kapsel Core and official plugins:
# - Core: carapace (carapace-bin)
# - Plugins: zoxide, mise, chsrc, aichat, pueue, chezmoi, pet, tealdeer, fzf
# - Python CLI: meta-package-manager (mpm), thefuck
#
# Adheres to Kapsel Dependency Philosophy:
# Native Package Manager -> Standalone binaries into ~/.kapsel/bin/ -> Zero virtualenvs.
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
echo -e "${CYAN}${BOLD}   Kapsel All-in-One Toolchain Installer (Linux)            ${RESET}"
echo -e "${CYAN}${BOLD}============================================================${RESET}"

KAPSEL_BIN_DIR="${HOME}/.kapsel/bin"
mkdir -p "${KAPSEL_BIN_DIR}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

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
# 1. Detect Linux Distribution and Package Manager
# ------------------------------------------------------------------------------
log_step "Detecting Linux Distribution"

PKG_MGR=""
if command -v pacman >/dev/null 2>&1; then
    PKG_MGR="pacman"
    log_info "Detected Arch Linux ecosystem (pacman)."
elif command -v apt-get >/dev/null 2>&1; then
    PKG_MGR="apt"
    log_info "Detected Debian / Ubuntu ecosystem (apt)."
elif command -v dnf >/dev/null 2>&1; then
    PKG_MGR="dnf"
    log_info "Detected Fedora / RedHat ecosystem (dnf)."
else
    PKG_MGR="generic"
    log_info "Generic Linux environment. Will use direct standalone binary installs."
fi

# ------------------------------------------------------------------------------
# 2. Install System Prerequisites (curl, git, python3-pip, pipx)
# ------------------------------------------------------------------------------
log_step "Checking System Prerequisites"

case "${PKG_MGR}" in
    apt)
        sudo apt-get update -qq
        sudo apt-get install -y -qq curl git python3-pip pipx ca-certificates tar gzip >/dev/null 2>&1 || true
        ;;
    pacman)
        sudo pacman -Sy --noconfirm --needed curl git python-pip python-pipx base-devel >/dev/null 2>&1 || true
        ;;
    dnf)
        sudo dnf install -y -q curl git python3-pip pipx tar gzip >/dev/null 2>&1 || true
        ;;
esac
log_ok "System prerequisites satisfied."

# ------------------------------------------------------------------------------
# 3. Arch Linux Fast-Track (if AUR helper available)
# ------------------------------------------------------------------------------
if [ "${PKG_MGR}" = "pacman" ]; then
    AUR_HELPER=""
    if command -v yay >/dev/null 2>&1; then
        AUR_HELPER="yay"
    elif command -v paru >/dev/null 2>&1; then
        AUR_HELPER="paru"
    fi

    if [ -n "${AUR_HELPER}" ]; then
        log_step "Installing full toolchain via Arch AUR (${AUR_HELPER})"
        ${AUR_HELPER} -S --needed --noconfirm \
            carapace-bin zoxide mise-bin chsrc aichat pueue chezmoi pet-bin tealdeer fzf thefuck python-meta-package-manager || true
    fi
fi

# ------------------------------------------------------------------------------
# 4. Standard Direct & Package Installations (Non-Arch or Fallback)
# ------------------------------------------------------------------------------
log_step "Installing Core & Plugin Binary Tools"

# 4a. carapace (Core completion engine)
if command -v carapace >/dev/null 2>&1 || [ -f "${KAPSEL_BIN_DIR}/carapace" ]; then
    log_ok "carapace is already installed."
else
    log_info "Installing carapace into ~/.kapsel/bin..."
    if [ -f "${SCRIPT_DIR}/install_carapace.sh" ]; then
        bash "${SCRIPT_DIR}/install_carapace.sh"
    else
        curl -sSL https://raw.githubusercontent.com/carapace-sh/carapace-bin/master/install.sh | bash -s -- -b "${KAPSEL_BIN_DIR}"
    fi
    log_ok "carapace installed."
fi

# 4b. zoxide (portal)
if command -v zoxide >/dev/null 2>&1; then
    log_ok "zoxide is already installed."
else
    log_info "Installing zoxide via official installer..."
    curl -sS https://raw.githubusercontent.com/ajeetdsouza/zoxide/main/install.sh | bash
    log_ok "zoxide installed."
fi

# 4c. mise (init)
if command -v mise >/dev/null 2>&1; then
    log_ok "mise is already installed."
else
    log_info "Installing mise via official installer..."
    curl https://mise.run | sh
    log_ok "mise installed."
fi

# 4d. chsrc (shore)
if command -v chsrc >/dev/null 2>&1 || [ -f "${KAPSEL_BIN_DIR}/chsrc" ]; then
    log_ok "chsrc is already installed."
else
    log_info "Installing chsrc via official installer..."
    curl -sSL https://chsrc.run/install | bash || {
        ARCH="$(uname -m)"
        CHSRC_URL="https://github.com/RubyMetric/chsrc/releases/latest/download/chsrc-x64-linux"
        if [ "${ARCH}" = "aarch64" ]; then
            CHSRC_URL="https://github.com/RubyMetric/chsrc/releases/latest/download/chsrc-arm64-linux"
        fi
        curl -fsSL "${CHSRC_URL}" -o "${KAPSEL_BIN_DIR}/chsrc"
        chmod +x "${KAPSEL_BIN_DIR}/chsrc"
    }
    log_ok "chsrc installed."
fi

# 4e. chezmoi (profile)
if command -v chezmoi >/dev/null 2>&1; then
    log_ok "chezmoi is already installed."
else
    log_info "Installing chezmoi into ~/.kapsel/bin..."
    sh -c "$(curl -fsLS get.chezmoi.io)" -- -b "${KAPSEL_BIN_DIR}"
    log_ok "chezmoi installed."
fi

# 4f. fzf & tealdeer (tldr) via package manager if possible
for t in fzf tealdeer; do
    if command -v "${t}" >/dev/null 2>&1 || [ "${t}" = "tealdeer" -a -x "$(command -v tldr)" ]; then
        log_ok "${t} is already installed."
    else
        case "${PKG_MGR}" in
            apt) sudo apt-get install -y -qq "${t}" >/dev/null 2>&1 || true ;;
            dnf) sudo dnf install -y -q "${t}" >/dev/null 2>&1 || true ;;
        esac
    fi
done

# ------------------------------------------------------------------------------
# 4g. Optional: Ultra Modern CLI Tools (if --ultra passed)
# ------------------------------------------------------------------------------
if [ "${INSTALL_ULTRA}" = true ]; then
    log_step "Installing Ultra Modern CLI Tools (--ultra)"
    case "${PKG_MGR}" in
        apt)
            sudo apt-get install -y -qq ripgrep fd-find bat jq || true
            ;;
        pacman)
            if [ -n "${AUR_HELPER:-}" ]; then
                ${AUR_HELPER} -S --needed --noconfirm eza bat ripgrep fd procs dust bottom gping jq sd lazygit hyperfine kondo || true
            else
                sudo pacman -Sy --noconfirm --needed ripgrep fd bat eza procs dust bottom gping jq sd lazygit hyperfine || true
            fi
            ;;
        dnf)
            sudo dnf install -y -q ripgrep fd-find bat eza procs jq || true
            ;;
    esac
    log_ok "Ultra modern CLI tools processed."
fi

# ------------------------------------------------------------------------------
# 5. Install Python Tools (mpm, thefuck)
# ------------------------------------------------------------------------------
log_step "Installing Python CLI Tools (mpm, thefuck)"

if command -v pipx >/dev/null 2>&1; then
    pipx ensurepath --force >/dev/null 2>&1 || true

    if ! command -v mpm >/dev/null 2>&1; then
        log_info "Installing meta-package-manager (mpm) via pipx..."
        pipx install meta-package-manager || true
        log_ok "mpm installed."
    else
        log_ok "mpm is already installed."
    fi

    if ! command -v thefuck >/dev/null 2>&1; then
        log_info "Installing thefuck via pipx..."
        pipx install thefuck || true
        log_ok "thefuck installed."
    else
        log_ok "thefuck is already installed."
    fi
else
    log_info "Installing Python tools via pip --user..."
    python3 -m pip install --user meta-package-manager thefuck || true
fi

# ------------------------------------------------------------------------------
# 6. Configure Shell PATH
# ------------------------------------------------------------------------------
log_step "Configuring Shell Environment"

for rc in "${HOME}/.bashrc" "${HOME}/.zshrc"; do
    if [ -f "${rc}" ]; then
        if ! grep -q "\.kapsel/bin" "${rc}"; then
            echo 'export PATH="${HOME}/.kapsel/bin:${HOME}/.local/bin:${PATH}"' >> "${rc}"
            log_ok "Configured PATH in ${rc}."
        fi
    fi
done

# ------------------------------------------------------------------------------
# 7. Trigger Spec Synchronization
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
