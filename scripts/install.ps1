# ==============================================================================
# Kapsel - Universal Windows Installer Dispatcher
# Generated automatically by scripts/generate_installers.py - DO NOT EDIT DIRECTLY!
#
# Single universal command for Windows:
#   irm https://raw.githubusercontent.com/MrEiu/Kapsel/master/scripts/install.ps1 | iex
#
# Options:
#   & { $(irm ...) } -Lite
#   & { $(irm ...) } -Full
# ==============================================================================

[CmdletBinding()]
param(
    [switch]$Lite,
    [switch]$Full,
    [switch]$Help
)

try {
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
    $OutputEncoding = [System.Text.Encoding]::UTF8
} catch {}

if ($Help) {
    Write-Host @"
Kapsel Windows Universal Installer (v0.1.9)

Usage:
  installer.ps1 [-Lite] [-Full] [-Help]

Parameters:
  -Lite       Install Lightweight Edition (Core Kapsel CLI + Carapace autocompletion)
  -Full       Install Full Edition (Core + Scoop Package Manager + 11 Official Plugins)
  -Help       Show this help documentation

Online Usage:
  irm https://raw.githubusercontent.com/MrEiu/Kapsel/master/scripts/install.ps1 | iex
"@
    exit 0
}

# Cross-platform safety: If running in PowerShell Core on Linux or macOS
if ($IsLinux -or $IsMacOS) {
    Write-Host "● Detected POSIX environment under PowerShell Core. Handing off to shell installer..." -ForegroundColor Cyan
    $posixEdition = if ($Lite) { "--lite" } else { "--full" }
    bash -c "curl -fsSL https://raw.githubusercontent.com/MrEiu/Kapsel/master/scripts/install.sh | bash -s -- $posixEdition"
    exit $LASTEXITCODE
}

# Determine Edition (Lite vs Full)
$edition = "Full"
if ($Lite) {
    $edition = "Lite"
} elseif ($Full) {
    $edition = "Full"
} else {
    try {
        if ([Environment]::UserInteractive) {
            Write-Host ""
            Write-Host '╭────────────────────────────────────────────────────────────────────────╮' -ForegroundColor Cyan
            Write-Host '│  _  __                 _                                           │' -ForegroundColor Cyan
            Write-Host "│ | |/ /__ _ _ __  ___  | |   ⚡ KAPSEL CLI (v0.1.9)                  │" -ForegroundColor Cyan
            Write-Host "│ | ' // _  | '_ \/ __| | |    Next-Gen Intelligent Terminal Capsule │" -ForegroundColor Cyan
            Write-Host '│ |_|\_\__,_| .__/|___/ |_|    https://github.com/MrEiu/Kapsel          │' -ForegroundColor Cyan
            Write-Host '│           |_|                                                         │' -ForegroundColor Cyan
            Write-Host '├────────────────────────────────────────────────────────────────────────┤' -ForegroundColor Cyan
            Write-Host '│  Please select your installation edition:                               │' -ForegroundColor Cyan
            Write-Host '│                                                                        │' -ForegroundColor Cyan
            Write-Host '│  [1] Lightweight Edition (Core + Carapace completions) ~20MB           │' -ForegroundColor Green
            Write-Host '│  [2] Full Toolchain Edition (Core + Scoop + All 11 Plugins) [Default]  │' -ForegroundColor Magenta
            Write-Host '│                                                                        │' -ForegroundColor Cyan
            Write-Host '╰────────────────────────────────────────────────────────────────────────╯' -ForegroundColor Cyan
            
            $choice = $null
            if ($Host.UI -and $Host.UI.ReadLine) {
                Write-Host -NoNewline "Enter selection [1 or 2, default 2]: "
                $choice = $Host.UI.ReadLine()
            } else {
                $choice = Read-Host "Enter selection [1 or 2, default 2]"
            }
            if ($choice -eq "1") {
                $edition = "Lite"
            } else {
                $edition = "Full"
            }
        }
    } catch {
        $edition = "Full"
    }
}

$flag = if ($edition -eq "Lite") { "-Lite" } else { "-Full" }

# Check Local vs Remote Target
$localScript = $null
if ($PSScriptRoot) {
    $cand = Join-Path $PSScriptRoot "install_windows.ps1"
    if (Test-Path $cand) {
        $localScript = $cand
    }
}

$remoteUrl = "https://raw.githubusercontent.com/MrEiu/Kapsel/master/scripts/install_windows.ps1"

Write-Host "● Platform detected: Windows | Edition: $edition" -ForegroundColor Cyan
Write-Host "  Fetching specific installer..." -ForegroundColor Gray

if ($localScript) {
    if ($edition -eq "Lite") {
        & $localScript -Lite
    } else {
        & $localScript -Full
    }
} else {
    $scriptContent = Invoke-RestMethod -Uri $remoteUrl
    $sb = [ScriptBlock]::Create($scriptContent)
    if ($edition -eq "Lite") {
        & $sb -Lite
    } else {
        & $sb -Full
    }
}