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
    $tempFile = Join-Path ([System.IO.Path]::GetTempPath()) ("kapsel_compat_" + [System.Guid]::NewGuid().ToString("N") + ".ps1")
    try {
        Invoke-WebRequest -Uri "https://raw.githubusercontent.com/MrEiu/Kapsel/master/scripts/install.ps1" -OutFile $tempFile -UseBasicParsing
        if ($Lite) { & $tempFile -Lite } else { & $tempFile -Full }
    } catch {
        $content = (Invoke-RestMethod -Uri "https://raw.githubusercontent.com/MrEiu/Kapsel/master/scripts/install.ps1").TrimStart([char]0xFEFF)
        $sb = [ScriptBlock]::Create($content)
        if ($Lite) { & $sb -Lite } else { & $sb -Full }
    } finally {
        if (Test-Path $tempFile) { Remove-Item -Path $tempFile -Force -ErrorAction SilentlyContinue }
    }
}

