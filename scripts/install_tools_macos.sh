#!/usr/bin/env bash
# ==============================================================================
# Kapsel - Backward compatibility forwarder for install_tools_macos.sh
# Delegates to unified modern installer: scripts/install_macos.sh --full
# ==============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd || echo "")"
LOCAL_INSTALLER="${SCRIPT_DIR}/install_macos.sh"

if [ -n "${SCRIPT_DIR}" ] && [ -f "${LOCAL_INSTALLER}" ]; then
    bash "${LOCAL_INSTALLER}" --full "$@"
else
    curl -fsSL https://raw.githubusercontent.com/MrEiu/Kapsel/master/scripts/install_macos.sh | bash -s -- --full "$@"
fi
