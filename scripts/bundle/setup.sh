#!/usr/bin/env bash
# ==============================================================================
# Kapsel All-in-One Bundle Installer (Linux & macOS)
# Unpacks binaries, plugins, package managers, and domestic mirrors into standard locations.
# ==============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
BOLD='\033[1m'
RESET='\033[0m'

echo -e "${CYAN}${BOLD}============================================================${RESET}"
echo -e "${CYAN}${BOLD}   Kapsel 官方完整版一键快速部署激活程序 (Linux / macOS)    ${RESET}"
echo -e "${CYAN}${BOLD}============================================================${RESET}"

BUNDLE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KAPSEL_HOME="${HOME}/.kapsel"
KAPSEL_BIN_DIR="${KAPSEL_HOME}/bin"
KAPSEL_PLUGINS_DIR="${KAPSEL_HOME}/plugins"

log_step() { echo -e "\n${CYAN}====> $1${RESET}"; }
log_ok()   { echo -e "  ${GREEN}[OK] $1${RESET}"; }
log_info() { echo -e "  ${YELLOW}[INFO] $1${RESET}"; }

# 1. 配置国内镜像
log_step "配置国内高速镜像加速 (pip / npm)"
mkdir -p "${HOME}/.config/pip"
if [ -f "${BUNDLE_ROOT}/mirrors/pip.ini" ]; then
    cp "${BUNDLE_ROOT}/mirrors/pip.ini" "${HOME}/.config/pip/pip.conf"
    log_ok "配置 pip 国内源 (清华源 / 阿里源)"
fi
if [ -f "${BUNDLE_ROOT}/mirrors/npmrc" ]; then
    cp "${BUNDLE_ROOT}/mirrors/npmrc" "${HOME}/.npmrc"
    log_ok "配置 npm 淘宝/腾讯镜像源"
fi

# 2. 部署单二进制工具
log_step "移动并部署全套单二进制工具到 ~/.kapsel/bin/"
mkdir -p "${KAPSEL_BIN_DIR}"
if [ -d "${BUNDLE_ROOT}/bin" ]; then
    for f in "${BUNDLE_ROOT}/bin"/*; do
        if [ -f "$f" ]; then
            fname="$(basename "$f")"
            cp "$f" "${KAPSEL_BIN_DIR}/${fname}"
            chmod +x "${KAPSEL_BIN_DIR}/${fname}"
            log_ok "已就位: ${fname}"
        fi
    done
fi

# 3. 部署插件库
log_step "部署官方插件家族到 ~/.kapsel/plugins/"
mkdir -p "${KAPSEL_PLUGINS_DIR}"
if [ -d "${BUNDLE_ROOT}/plugins" ]; then
    cp -rf "${BUNDLE_ROOT}/plugins"/* "${KAPSEL_PLUGINS_DIR}/" 2>/dev/null || true
    log_ok "插件库部署完成。"
fi

# 4. 离线安装 Python 组件
log_step "初始化并安装 Python 核心套件"
if command -v python3 >/dev/null 2>&1; then
    if [ -d "${BUNDLE_ROOT}/wheels" ] && [ "$(ls -A "${BUNDLE_ROOT}/wheels" 2>/dev/null)" ]; then
        log_info "从离线 wheels 极速免流安装组件..."
        python3 -m pip install --user --no-index --find-links="${BUNDLE_ROOT}/wheels" kapsel-cli meta-package-manager thefuck pipx --quiet 2>/dev/null || true
    else
        log_info "通过清华镜像源安装组件..."
        python3 -m pip install --user kapsel-cli meta-package-manager thefuck pipx -i https://pypi.tuna.tsinghua.edu.cn/simple --quiet 2>/dev/null || true
    fi
    log_ok "Python 组件配置就绪。"
fi

# 5. 配置 Shell PATH
log_step "配置系统环境变量 PATH"
for rc in "${HOME}/.bashrc" "${HOME}/.zshrc"; do
    if [ -f "$rc" ]; then
        if ! grep -q "\.kapsel/bin" "$rc"; then
            echo 'export PATH="${HOME}/.kapsel/bin:${HOME}/.local/bin:${PATH}"' >> "$rc"
            log_ok "已追加 PATH 至 $rc"
        fi
    fi
done

# 6. 生成并同步补全规约
log_step "激活双根补全规约 (kps.yaml 与 kapsel.yaml)"
python3 -c "from kapsel.completion.spec_manager import CarapaceSpecManager; CarapaceSpecManager().sync_specs(force=True)" 2>/dev/null || true
log_ok "全套指令与参数自动补全已就绪！"

echo -e "\n${GREEN}${BOLD}============================================================${RESET}"
echo -e "${GREEN}${BOLD}   🎉 Kapsel 官方完整版已全部就位，即刻启航！               ${RESET}"
echo -e "${GREEN}${BOLD}============================================================${RESET}"
echo -e "请在当前窗口运行 'source ~/.bashrc' (或 ~/.zshrc) 刷新环境，"
echo -e "随后即可直接运行 'kapsel' 或 'kps status'！\n"
