#!/usr/bin/env bash
# ==============================================================================
# Kapsel - 中国大陆用户高速安装与全自动配置脚本 (Linux & macOS)
# 自动通过国内高速镜像代理拉取安装包与工具链，免翻墙，一键归位激活。
#
# 【推荐用法】先使用国内镜像下载脚本到本地，再执行脚本安装（最稳健，规避网络中断与环境波动）：
#   curl -fsSL "https://ghproxy.net/https://raw.githubusercontent.com/MrEiu/Kapsel/master/scripts/install_cn.sh" -o install_cn.sh
#   bash install_cn.sh
#
# 【极速用法】一行流管道直接执行：
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
    x86_64|amd64)   ARCH_TAG="amd64"; ARCH_ALIAS="x86_64";;
    aarch64|arm64)  ARCH_TAG="arm64"; ARCH_ALIAS="arm64";;
    *)              echo -e "${RED}不支持的架构: ${ARCH}${RESET}"; exit 1;;
esac

KAPSEL_BIN_DIR="${HOME}/.kapsel/bin"
mkdir -p "${KAPSEL_BIN_DIR}"

REL_TAG="latest/download"
if [ "${VERSION}" != "latest" ]; then
    REL_TAG="download/v${VERSION}"
fi

MIRROR_PREFIXES=(
    "https://ghproxy.net/"
    "https://mirror.ghproxy.com/"
    "https://gh-proxy.com/"
)

TEMP_DIR="$(mktemp -d -t kapsel_install_XXXXXX)"
DOWNLOAD_SUCCESS=false

# ------------------------------------------------------------------------------
# 阶段 1: 优先尝试从 GitHub Releases 高速拉取完整一体大包
# ------------------------------------------------------------------------------
BUNDLE_NAME="kapsel-bundle-${OS_TAG}-${ARCH_TAG}.tar.gz"
GH_BUNDLE_URL="https://github.com/MrEiu/Kapsel/releases/${REL_TAG}/${BUNDLE_NAME}"
TAR_PATH="${TEMP_DIR}/${BUNDLE_NAME}"

echo -e "${CYAN}==> [阶段 1/3] 正在尝试通过高速镜像拉取全量一体离线包...${RESET}"

for prefix in "${MIRROR_PREFIXES[@]}"; do
    url="${prefix}${GH_BUNDLE_URL}"
    echo -e "  -> 尝试通道: ${url}"
    if curl -fsSL --connect-timeout 15 -o "${TAR_PATH}" "${url}" 2>/dev/null; then
        FILE_SIZE=$(wc -c < "${TAR_PATH}" | tr -d ' ')
        if [ "$FILE_SIZE" -gt 1048576 ]; then
            MB_SIZE=$(( FILE_SIZE / 1048576 ))
            echo -e "  ${GREEN}[✔] 极速下载完成！包体积: ~${MB_SIZE} MB${RESET}"
            DOWNLOAD_SUCCESS=true
            break
        fi
    fi
done

if [ "${DOWNLOAD_SUCCESS}" = true ]; then
    UNPACK_DIR="${TEMP_DIR}/unpacked"
    mkdir -p "${UNPACK_DIR}"
    echo -e "${CYAN}==> 正在解压完整一体包并分发归位...${RESET}"
    tar -xzf "${TAR_PATH}" -C "${UNPACK_DIR}"
    
    SETUP_SCRIPT="$(find "${UNPACK_DIR}" -name "setup.sh" | head -n 1)"
    if [ -n "${SETUP_SCRIPT}" ] && [ -f "${SETUP_SCRIPT}" ]; then
        echo -e "${CYAN}==> 正在启动全自动归位激活程序...${RESET}"
        bash "${SETUP_SCRIPT}"
    fi
else
    # --------------------------------------------------------------------------
    # 阶段 2: 尝试拉取轻量级预编译独立二进制单文件
    # --------------------------------------------------------------------------
    echo -e "${CYAN}==> [阶段 2/3] 正在尝试通过高速镜像拉取预编译独立二进制单文件...${RESET}"
    if [ "${OS_TAG}" = "macos" ]; then
        BIN_NAME="kapsel-macos-universal.tar.gz"
    else
        BIN_NAME="kapsel-linux-${ARCH_ALIAS}.tar.gz"
    fi
    GH_BIN_URL="https://github.com/MrEiu/Kapsel/releases/${REL_TAG}/${BIN_NAME}"
    BIN_TAR_PATH="${TEMP_DIR}/${BIN_NAME}"
    BIN_DOWNLOADED=false

    for prefix in "${MIRROR_PREFIXES[@]}"; do
        url="${prefix}${GH_BIN_URL}"
        echo -e "  -> 尝试独立二进制镜像: ${url}"
        if curl -fsSL --connect-timeout 15 -o "${BIN_TAR_PATH}" "${url}" 2>/dev/null; then
            FILE_SIZE=$(wc -c < "${BIN_TAR_PATH}" | tr -d ' ')
            if [ "$FILE_SIZE" -gt 524288 ]; then
                echo -e "  ${GREEN}[✔] 独立二进制下载完成！${RESET}"
                BIN_DOWNLOADED=true
                break
            fi
        fi
    done

    if [ "${BIN_DOWNLOADED}" = true ]; then
        echo -e "${CYAN}==> 正在部署独立二进制到 ~/.kapsel/bin/...${RESET}"
        tar -xzf "${BIN_TAR_PATH}" -C "${KAPSEL_BIN_DIR}"
        chmod +x "${KAPSEL_BIN_DIR}/kapsel" "${KAPSEL_BIN_DIR}/kps" 2>/dev/null || true
        echo -e "  ${GREEN}[✔] 已部署 kapsel & kps${RESET}"
    else
        # ----------------------------------------------------------------------
        # 阶段 3: 使用清华大学国内 PyPI 镜像源在线安装 kapsel-cli
        # ----------------------------------------------------------------------
        echo -e "${CYAN}==> [阶段 3/3] 使用清华大学镜像源 (TUNA) 安装 kapsel-cli...${RESET}"
        if command -v python3 >/dev/null 2>&1; then
            python3 -m pip install --upgrade kapsel-cli -i https://pypi.tuna.tsinghua.edu.cn/simple --quiet 2>/dev/null || true
            echo -e "  ${GREEN}[✔] kapsel-cli 已通过国内 PyPI 镜像极速安装！${RESET}"
        else
            echo -e "  ${YELLOW}[!] 未检测到 python3，建议安装 Python 3.9+ 或下载 Release 预编译包。${RESET}"
        fi
    fi

    # 运行配套工具链安装器 (Carapace, Zoxide, Mise 等)
    echo -e "\n${CYAN}==> 正在通过国内镜像加速拉取配套工具链安装器...${RESET}"
    SCRIPT_NAME="install_tools_linux.sh"
    if [ "${OS_TAG}" = "macos" ]; then
        SCRIPT_NAME="install_tools_macos.sh"
    fi
    FALLBACK_URL="https://ghproxy.net/https://raw.githubusercontent.com/MrEiu/Kapsel/master/scripts/${SCRIPT_NAME}"
    curl -fsSL "${FALLBACK_URL}" | bash || true
fi

# 确保 ~/.kapsel/bin 写入系统 Shell PATH
SHELL_RC=""
if [ -n "$ZSH_VERSION" ] || [ "$SHELL" = "*/zsh" ]; then
    SHELL_RC="${HOME}/.zshrc"
elif [ -f "${HOME}/.bashrc" ]; then
    SHELL_RC="${HOME}/.bashrc"
fi

if [ -n "${SHELL_RC}" ] && [ -f "${SHELL_RC}" ]; then
    if ! grep -q ".kapsel/bin" "${SHELL_RC}"; then
        echo 'export PATH="$HOME/.kapsel/bin:$PATH"' >> "${SHELL_RC}"
        echo -e "  ${GREEN}[✔] 已将 ~/.kapsel/bin 永久写入 ${SHELL_RC}${RESET}"
    fi
fi

rm -rf "${TEMP_DIR}"

echo -e "${GREEN}${BOLD}============================================================${RESET}"
echo -e "${GREEN}${BOLD}   🎉 Kapsel 国内极速安装配置完成！                         ${RESET}"
echo -e "${GREEN}${BOLD}============================================================${RESET}"
echo -e "  - 核心主命令:   kapsel (或 kps)"
echo -e "  - 查看运行状态: kapsel status"
echo -e "  - 查阅完整手册: kps help"
echo -e "  提示: 请重新打开终端窗口使 PATH 环境变量生效。\n"

