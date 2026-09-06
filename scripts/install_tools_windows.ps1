# ==============================================================================
# Kapsel - Backward compatibility forwarder for install_tools_windows.ps1
# Delegates to unified modern installer: scripts/install.ps1 -Full
# ==============================================================================

[CmdletBinding()]
param(
    [switch]$Lite,
    [switch]$Full,
    [switch]$Help
)

$localInstaller = if ($PSScriptRoot) { Join-Path $PSScriptRoot "install.ps1" } else { $null }
if ($localInstaller -and (Test-Path $localInstaller)) {
    if ($Lite) { & $localInstaller -Lite } else { & $localInstaller -Full }
} else {
    $flag = if ($Lite) { "-Lite" } else { "-Full" }
    $sb = [ScriptBlock]::Create((Invoke-RestMethod -Uri "https://raw.githubusercontent.com/MrEiu/Kapsel/master/scripts/install.ps1"))
    if ($Lite) { & $sb -Lite } else { & $sb -Full }
}
