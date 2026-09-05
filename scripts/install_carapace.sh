#!/usr/bin/env bash
# ==============================================================================
# Kapsel - Carapace Completion Engine Installer for Linux and macOS
# Automatically downloads and installs the official 'carapace-bin' standalone binary
# into ~/.kapsel/bin/carapace (No root or sudo permissions required).
# ==============================================================================

set -e

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
DIM='\033[2m'
BOLD='\033[1m'
RESET='\033[0m'

VERSION="1.7.3"
INSTALL_DIR="${HOME}/.kapsel/bin"
TARGET_BIN="${INSTALL_DIR}/carapace"

echo -e "${CYAN}${BOLD}=== Kapsel Carapace Completion Engine Installer ===${RESET}"

# 1. Detect Operating System
OS="$(uname -s)"
case "${OS}" in
    Linux*)     OS_TYPE="linux";;
    Darwin*)    OS_TYPE="darwin";;
    *)
        echo -e "${RED}Error: Unsupported operating system: ${OS}${RESET}"
        echo "For Windows, please use 'kps add carapace' or scripts/install_carapace.ps1"
        exit 1
        ;;
esac

# 2. Detect CPU Architecture
ARCH="$(uname -m)"
case "${ARCH}" in
    x86_64|amd64)   ARCH_TYPE="amd64";;
    aarch64|arm64)  ARCH_TYPE="arm64";;
    armv7l|armv6l)  ARCH_TYPE="armv6";;
    i386|i686)      ARCH_TYPE="386";;
    *)
        echo -e "${RED}Error: Unsupported CPU architecture: ${ARCH}${RESET}"
        exit 1
        ;;
esac

TAR_NAME="carapace-bin_${VERSION}_${OS_TYPE}_${ARCH_TYPE}.tar.gz"
DOWNLOAD_URL="https://github.com/carapace-sh/carapace-bin/releases/download/v${VERSION}/${TAR_NAME}"
MIRROR_URL="https://ghproxy.net/${DOWNLOAD_URL}"

echo -e "Platform detected: ${BOLD}${OS_TYPE} (${ARCH_TYPE})${RESET}"
echo -e "Target version:    ${BOLD}v${VERSION}${RESET}"
echo -e "Install location:  ${DIM}${TARGET_BIN}${RESET}"
echo ""

# 3. Create destination directory
mkdir -p "${INSTALL_DIR}"

TMP_DIR="$(mktemp -d 2>/dev/null || mktemp -d -t 'kapsel_carapace')"
ARCHIVE_PATH="${TMP_DIR}/${TAR_NAME}"

cleanup() {
    rm -rf "${TMP_DIR}"
}
trap cleanup EXIT

# 4. Download archive
echo -e "${CYAN}==> Downloading carapace-bin v${VERSION}...${RESET}"

download_file() {
    local url="$1"
    local dest="$2"
    if command -v curl >/dev/null 2>&1; then
        curl -fsSL --connect-timeout 10 --retry 2 "$url" -o "$dest"
    elif command -v wget >/dev/null 2>&1; then
        wget -q --timeout=10 --tries=2 "$url" -O "$dest"
    else
        echo -e "${RED}Error: Neither curl nor wget was found on this system.${RESET}"
        exit 1
    fi
}

if ! download_file "${DOWNLOAD_URL}" "${ARCHIVE_PATH}"; then
    echo -e "${YELLOW}Notice: Direct GitHub download failed or timed out. Trying mirror fallback...${RESET}"
    if ! download_file "${MIRROR_URL}" "${ARCHIVE_PATH}"; then
        echo -e "${RED}Error: Failed to download ${TAR_NAME} from GitHub and mirror.${RESET}"
        echo "Please check your network connectivity or download manually from:"
        echo "  https://github.com/carapace-sh/carapace-bin/releases/tag/v${VERSION}"
        exit 1
    fi
fi

# 5. Extract binary
echo -e "${CYAN}==> Extracting carapace binary...${RESET}"
tar -xzf "${ARCHIVE_PATH}" -C "${TMP_DIR}" carapace

if [ ! -f "${TMP_DIR}/carapace" ]; then
    echo -e "${RED}Error: Archive did not contain 'carapace' binary.${RESET}"
    exit 1
fi

mv -f "${TMP_DIR}/carapace" "${TARGET_BIN}"
chmod +x "${TARGET_BIN}"

# 6. Verify installation
echo -e "${CYAN}==> Verifying installation...${RESET}"
if "${TARGET_BIN}" --version >/dev/null 2>&1; then
    VER_OUTPUT="$("${TARGET_BIN}" --version 2>&1 | head -n 1)"
    echo -e "${GREEN}${BOLD}✔ Successfully installed Carapace (${VER_OUTPUT})!${RESET}"
    echo -e "${GREEN}Location: ${TARGET_BIN}${RESET}"
    echo ""
    echo -e "Kapsel will automatically detect Carapace in ${DIM}~/.kapsel/bin${RESET}."
    echo -e "Start Kapsel with ${BOLD}kapsel${RESET} to enjoy 1,000+ command completions (git, docker, kubectl, etc.)!"
else
    echo -e "${YELLOW}Warning: Carapace binary installed at ${TARGET_BIN}, but failed verification.${RESET}"
    exit 1
fi
