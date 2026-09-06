#!/usr/bin/env bash
# ==============================================================================
# Kapsel - Backward compatibility forwarder for install_tools_linux.sh
# Delegates to unified modern installer: scripts/install_linux.sh --full
# ==============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd || echo "")"
LOCAL_INSTALLER="${SCRIPT_DIR}/install_linux.sh"

if [ -n "${SCRIPT_DIR}" ] && [ -f "${LOCAL_INSTALLER}" ]; then
    bash "${LOCAL_INSTALLER}" --full "$@"
else
    curl -fsSL https://raw.githubusercontent.com/MrEiu/Kapsel/master/scripts/install_linux.sh | bash -s -- --full "$@"
fi
