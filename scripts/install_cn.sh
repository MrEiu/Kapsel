#!/usr/bin/env bash
# ==============================================================================
# Kapsel - 中国大陆用户一键高速安装与激活脚本 (Linux & macOS)
# 自动通过国内镜像代理从 GitHub Release 极速拉取官方完整大包并一键归位激活。
# 用法:
#   curl -fsSL https://ghproxy.net/https://raw.githubusercontent.com/MrEiu/Kapsel/master/scripts/install_cn.sh | bash
# ==============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
BOLD='\033[1m'
RESET='\033[0m'

echo -e "${CYAN}${BOLD}============================================================${RESET}"
echo -e "${CYAN}${BOLD}   Kapsel 官方完整版国内一键极速激活脚本 (Linux / macOS)     ${RESET}"
echo -e "${CYAN}${BOLD}============================================================${RESET}"

VERSION="${1:-latest}"

# 1. 平台与架构识别
OS="$(uname -s)"
case "${OS}" in
    Linux*)  OS_TAG="linux";;
    Darwin*) OS_TAG="macos";;
    *)       echo -e "${RED}不支持的系统: ${OS}${RESET}"; exit 1;;
esac

ARCH="$(uname -m)"
case "${ARCH}" in
    x86_64|amd64)   ARCH_TAG="amd64";;
    aarch64|arm64)  ARCH_TAG="arm64";;
    *)              echo -e "${RED}不支持的架构: ${ARCH}${RESET}"; exit 1;;
esac

BUNDLE_NAME="kapsel-bundle-${OS_TAG}-${ARCH_TAG}.tar.gz"
REL_TAG="latest/download"
if [ "${VERSION}" != "latest" ]; then
    REL_TAG="download/v${VERSION}"
fi

GH_RELEASE_URL="https://github.com/MrEiu/Kapsel/releases/${REL_TAG}/${BUNDLE_NAME}"

ACCELERATOR_URLS=(
    "https://ghproxy.net/${GH_RELEASE_URL}"
    "https://mirror.ghproxy.com/${GH_RELEASE_URL}"
    "https://gh-proxy.com/${GH_RELEASE_URL}"
    "${GH_RELEASE_URL}"
)

TEMP_DIR="$(mktemp -d -t kapsel_install_XXXXXX)"
TAR_PATH="${TEMP_DIR}/${BUNDLE_NAME}"
DOWNLOAD_SUCCESS=false

echo -e "${CYAN}==> 正在连接高速镜像拉取完整一体包 (${BUNDLE_NAME})...${RESET}"

for url in "${ACCELERATOR_URLS[@]}"; do
    echo -e "  -> 尝试通道: ${url}"
    if curl -fsSL --connect-timeout 10 -o "${TAR_PATH}" "${url}" 2>/dev/null; then
        FILE_SIZE=$(wc -c < "${TAR_PATH}" | tr -d ' ')
        if [ "$FILE_SIZE" -gt 1048576 ]; then
            MB_SIZE=$(( FILE_SIZE / 1048576 ))
            echo -e "  ${GREEN}[✔] 极速下载完成！包体积: ~${MB_SIZE} MB${RESET}"
            DOWNLOAD_SUCCESS=true
            break
        fi
    fi
    echo -e "  ${YELLOW}[!] 通道超时或大包尚未发布，切换下一个通道...${RESET}"
done

UNPACK_DIR="${TEMP_DIR}/unpacked"
mkdir -p "${UNPACK_DIR}"

if [ "${DOWNLOAD_SUCCESS}" = true ]; then
    echo -e "${CYAN}==> 正在解压完整一体包并分发归位...${RESET}"
    tar -xzf "${TAR_PATH}" -C "${UNPACK_DIR}"
    
    SETUP_SCRIPT="$(find "${UNPACK_DIR}" -name "setup.sh" | head -n 1)"
    if [ -n "${SETUP_SCRIPT}" ] && [ -f "${SETUP_SCRIPT}" ]; then
        echo -e "${CYAN}==> 正在启动全自动归位激活程序...${RESET}"
        bash "${SETUP_SCRIPT}"
    else
        echo -e "${RED}解压后未找到 setup.sh 激活脚本。${RESET}"
        exit 1
    fi
else
    echo -e "\n${YELLOW}[提示] GitHub Release 大包尚未发布或网络阻断。${RESET}"
    echo -e "${CYAN}==> 自动启动智能在线降级安装器 (配置国内源与工具链)...${RESET}"
    
    SCRIPT_NAME="install_tools_linux.sh"
    if [ "${OS_TAG}" = "macos" ]; then
        SCRIPT_NAME="install_tools_macos.sh"
    fi
    
    FALLBACK_URL="https://ghproxy.net/https://raw.githubusercontent.com/MrEiu/Kapsel/master/scripts/${SCRIPT_NAME}"
    curl -fsSL "${FALLBACK_URL}" | bash
fi

rm -rf "${TEMP_DIR}"

echo -e "${GREEN}${BOLD}============================================================${RESET}"
echo -e "${GREEN}${BOLD}   部署全部就绪！打开新终端输入 kapsel 即可体验完整版 Kapsel。 ${RESET}"
echo -e "${GREEN}${BOLD}============================================================${RESET}\n"
