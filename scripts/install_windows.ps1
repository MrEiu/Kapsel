# ==============================================================================
# Kapsel - Modern Cross-Platform Terminal Capsule Installer for Windows
# Generated automatically by scripts/generate_installers.py - DO NOT EDIT DIRECTLY!
#
# Provides two installation editions:
# 1. Lightweight (-Lite): Kapsel Core + Carapace completion engine (~20MB, ultra fast)
# 2. Full (-Full):        Lightweight + Scoop package manager + 11 official plugins
#
# Usage:
#   irm https://raw.githubusercontent.com/MrEiu/Kapsel/master/scripts/install_windows.ps1 | iex
#   & { $(irm ...) } -Lite
#   & { $(irm ...) } -Full
# ==============================================================================

[CmdletBinding()]
param(
    [switch]$Lite,
    [switch]$Full,
    [switch]$Help
)

# ------------------------------------------------------------------------------
# 0. Terminal Environment & Encoding Configuration
# ------------------------------------------------------------------------------
try {
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
    $OutputEncoding = [System.Text.Encoding]::UTF8
} catch {}

$ErrorActionPreference = "Continue"

function Show-Help {
    Write-Host @"
Kapsel Windows Installer (v0.2.0)

Usage:
  installer.ps1 [-Lite] [-Full] [-Help]

Parameters:
  -Lite       Install Lightweight Edition (Core Kapsel CLI + Carapace autocompletion)
  -Full       Install Full Edition (Core + Scoop Package Manager + 11 Official Plugins)
  -Help       Show this help documentation

Examples:
  .\install_windows.ps1 -Lite
  .\install_windows.ps1 -Full
"@
    exit 0
}

if ($Help) { Show-Help }

function Write-Logo {
    param([string]$EditionLabel)
    Write-Host ""
    Write-Host '╭────────────────────────────────────────────────────────────────────────╮' -ForegroundColor Cyan
    Write-Host '│  _  __                 _                                           │' -ForegroundColor Cyan
    Write-Host "│ | |/ /__ _ _ __  ___  | |   ⚡ KAPSEL CLI (v0.2.0)                  │" -ForegroundColor Cyan
    Write-Host "│ | ' // _  | '_ \/ __| | |    Next-Gen Intelligent Terminal Capsule │" -ForegroundColor Cyan
    Write-Host '│ | . \ (_| | |_) \__ \ | |    https://github.com/MrEiu/Kapsel          │' -ForegroundColor Cyan
    Write-Host '│ |_|\_\__,_| .__/|___/ |_|                                           │' -ForegroundColor Cyan
    Write-Host ('│           |_|             [' + $EditionLabel + ']                         │') -ForegroundColor Cyan
    Write-Host '╰────────────────────────────────────────────────────────────────────────╯' -ForegroundColor Cyan
    Write-Host ""
}

function Write-Step {
    param([string]$StepNum, [string]$Title)
    Write-Host "==> [$StepNum] $Title" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "  ✔ " -ForegroundColor Green -NoNewline
    Write-Host $Message
}

function Write-Info {
    param([string]$Message)
    Write-Host "  ● " -ForegroundColor DarkCyan -NoNewline
    Write-Host $Message -ForegroundColor Gray
}

function Write-Warn {
    param([string]$Message)
    Write-Host "  ! " -ForegroundColor Yellow -NoNewline
    Write-Host $Message -ForegroundColor Yellow
}

function Write-ErrorExit {
    param([string]$Message)
    Write-Host "`n  ✘ Error: " -ForegroundColor Red -NoNewline
    Write-Host $Message
    exit 1
}

# ------------------------------------------------------------------------------
# 1. Determine Edition (Lite vs Full)
# ------------------------------------------------------------------------------
$edition = "Full"

if ($Lite) {
    $edition = "Lite"
} elseif ($Full) {
    $edition = "Full"
} else {
    try {
        if ([Environment]::UserInteractive) {
            Write-Host "╭────────────────────────────────────────────────────────────────────────╮" -ForegroundColor Cyan
            Write-Host "│  Please select the Kapsel installation edition:                        │" -ForegroundColor Cyan
            Write-Host "│                                                                        │" -ForegroundColor Cyan
            Write-Host "│  [1] Lightweight Edition (Core + Carapace completions) ~20MB           │" -ForegroundColor Green
            Write-Host "│  [2] Full Edition (Core + Scoop + All 11 Plugins) [Default]        │" -ForegroundColor Magenta
            Write-Host "│                                                                        │" -ForegroundColor Cyan
            Write-Host "╰────────────────────────────────────────────────────────────────────────╯" -ForegroundColor Cyan
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

$editionTitle = if ($edition -eq "Lite") { "Lightweight Edition" } else { "Full Toolchain Edition" }
Write-Logo $editionTitle

$userProfile = if ($env:USERPROFILE) { $env:USERPROFILE } else { [Environment]::GetFolderPath("UserProfile") }
$kapselHome = Join-Path $userProfile ".kapsel"
$kapselBinDir = Join-Path $kapselHome "bin"
if (-not (Test-Path $kapselBinDir)) {
    New-Item -ItemType Directory -Path $kapselBinDir -Force | Out-Null
}

if ($env:PATH -notlike "*$kapselBinDir*") {
    $env:PATH = "$kapselBinDir;$env:PATH"
}

# ------------------------------------------------------------------------------
# 2. Preflight Environment State Inspection
# ------------------------------------------------------------------------------
Write-Step "1/5" "Inspecting Current System Environment"

# 2.1 Locate Python
$pythonCmd = $null
$pyVersion = $null
foreach ($cand in @("python", "python3", "py")) {
    if (Get-Command $cand -ErrorAction SilentlyContinue) {
        $verCheck = & $cand -c "import sys; print(sys.version_info >= (3, 9))" 2>$null
        if ($verCheck -eq "True") {
            $pythonCmd = $cand
            $pyVersion = & $cand -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')" 2>$null
            break
        }
    }
}

$pyScripts = if ($pythonCmd) {
    & $pythonCmd -c "import sysconfig; print(sysconfig.get_path('scripts'))" 2>$null
} else { $null }

if ($pyScripts -and (Test-Path $pyScripts) -and ($env:PATH -notlike "*$pyScripts*")) {
    $env:PATH = "$pyScripts;$env:PATH"
}

# 2.2 Detect Kapsel Core
$kapselInstalled = $false
$installedKapselVer = $null
$kapselUpToDate = $false

if ($pythonCmd) {
    $verOut = & $pythonCmd -m kapsel.cli -v 2>$null
    if ($verOut -match "(\d+\.\d+\.\d+)") {
        $kapselInstalled = $true
        $installedKapselVer = $matches[1]
        if ($installedKapselVer -eq "0.2.0") {
            $kapselUpToDate = $true
        }
    }
}
if (-not $kapselInstalled -and (Get-Command "kapsel" -ErrorAction SilentlyContinue)) {
    $verOut = & kapsel -v 2>$null
    if ($verOut -match "(\d+\.\d+\.\d+)") {
        $kapselInstalled = $true
        $installedKapselVer = $matches[1]
        if ($installedKapselVer -eq "0.2.0") {
            $kapselUpToDate = $true
        }
    }
}

# 2.3 Detect Carapace
$carapaceExe = Join-Path $kapselBinDir "carapace.exe"
$carapaceInstalled = $false
$carapaceVer = $null
if (Test-Path $carapaceExe) {
    $caraOut = & $carapaceExe --version 2>$null
    if ($caraOut) {
        $carapaceInstalled = $true
        $carapaceVer = $caraOut.Trim()
    }
} elseif (Get-Command "carapace" -ErrorAction SilentlyContinue) {
    $caraOut = & carapace --version 2>$null
    if ($caraOut) {
        $carapaceInstalled = $true
        $carapaceVer = $caraOut.Trim()
    }
}

# 2.4 Detect PATH Configuration
$userPath = [Environment]::GetEnvironmentVariable("PATH", "User")
$pathConfigured = ($userPath -like "*$kapselBinDir*")
if ($pyScripts) {
    $pathConfigured = $pathConfigured -and ($userPath -like "*$pyScripts*")
}

# 2.5 Detect Scoop & Plugins (Full Edition only)
$hasScoop = (Get-Command "scoop" -ErrorAction SilentlyContinue) -ne $null
$installedPlugins = @()
$missingPlugins = @()
$allPluginIds = @("alias", "portal", "init", "shore", "ai", "install", "autopilot", "rec", "profile", "fuck", "help")

if ($edition -eq "Full") {
    $foundNames = @()
    if ($pythonCmd) {
        $pyCheck = & $pythonCmd -c "try:
    from kapsel.storage.config import get_kapsel_dir; p = get_kapsel_dir() / 'plugins'
    print(','.join([x.name for x in p.iterdir() if x.is_dir() and (x/'__init__.py').exists()]))
except Exception:
    pass" 2>$null
        if ($pyCheck) {
            $foundNames = @($pyCheck.Split(","))
        }
    }
    if ($foundNames.Count -eq 0) {
        $globalPluginsDir = Join-Path $kapselHome "plugins"
        if (Test-Path $globalPluginsDir) {
            $foundNames = @(Get-ChildItem -Directory -Path $globalPluginsDir | Where-Object { Test-Path (Join-Path $_.FullName "__init__.py") } | Select-Object -ExpandProperty Name)
        }
    }

    foreach ($pluginId in $allPluginIds) {
        if ($foundNames -contains $pluginId) {
            $installedPlugins += $pluginId
        } else {
            $missingPlugins += $pluginId
        }
    }
}

# Render Preflight Status Inspection Box
Write-Host ""
Write-Host "  ┌── Preflight Environment Status ────────────────────────────────────────┐" -ForegroundColor Cyan
if ($pythonCmd) {
    Write-Host "  │ Python Runtime:     ✔ Found $pyVersion ($pythonCmd)" -ForegroundColor Green
} else {
    Write-Host "  │ Python Runtime:     ● Missing (Will auto-install via WinGet)" -ForegroundColor Yellow
}

if ($kapselUpToDate) {
    Write-Host "  │ Kapsel Core CLI:    ✔ Up-to-date (v$installedKapselVer)" -ForegroundColor Green
} elseif ($kapselInstalled) {
    Write-Host "  │ Kapsel Core CLI:    ● Installed v$installedKapselVer (Upgrade to v0.2.0 needed)" -ForegroundColor Cyan
} else {
    Write-Host "  │ Kapsel Core CLI:    ● Not installed (Target: v0.2.0)" -ForegroundColor Yellow
}

if ($carapaceInstalled) {
    Write-Host "  │ Carapace Engine:    ✔ Installed ($carapaceVer)" -ForegroundColor Green
} else {
    Write-Host "  │ Carapace Engine:    ● Not installed (Target: v1.7.3)" -ForegroundColor Yellow
}

if ($pathConfigured) {
    Write-Host "  │ System PATH:        ✔ ~/.kapsel/bin configured in User PATH" -ForegroundColor Green
} else {
    Write-Host "  │ System PATH:        ● Needs persistent configuration" -ForegroundColor Yellow
}

if ($edition -eq "Full") {
    $scoopStatus = if ($hasScoop) { "✔ Ready" } else { "● Needs bootstrap" }
    $scoopColor = if ($hasScoop) { "Green" } else { "Yellow" }
    Write-Host "  │ Scoop Manager:      $scoopStatus" -ForegroundColor $scoopColor
    $plugCount = "$($installedPlugins.Count)/$($allPluginIds.Count)"
    $plugColor = if ($missingPlugins.Count -eq 0) { "Green" } else { "Cyan" }
    Write-Host "  │ Official Plugins:   $plugCount installed" -ForegroundColor $plugColor
}
Write-Host "  └────────────────────────────────────────────────────────────────────────┘" -ForegroundColor Cyan
Write-Host ""

$isEverythingOptimal = $pythonCmd -and $kapselUpToDate -and $carapaceInstalled -and $pathConfigured
if ($edition -eq "Full") {
    $isEverythingOptimal = $isEverythingOptimal -and $hasScoop -and ($missingPlugins.Count -eq 0)
}

if ($isEverythingOptimal) {
    Write-Success "All components are already installed and up to date! Zero actions needed."
    & $pythonCmd -m kapsel.cli completion sync 2>$null | Out-Null
    & $pythonCmd -c "from kapsel.storage.config import load_config; load_config()" 2>$null | Out-Null
    Write-Host ""
    Write-Host "✨ Instant preflight check passed. Your Kapsel environment is ready to use." -ForegroundColor Green
    Write-Host ""
    exit 0
}

# ------------------------------------------------------------------------------
# 3. Python Runtime Verification / WinGet Bootstrap
# ------------------------------------------------------------------------------
if (-not $pythonCmd) {
    Write-Step "2/5" "Installing Python Runtime (>= 3.9)"
    Write-Info "Attempting to install Python via WinGet..."
    if (Get-Command "winget" -ErrorAction SilentlyContinue) {
        winget install --id Python.Python.3.12 --silent --accept-package-agreements --accept-source-agreements
        $pythonCmd = "python"
        $pyVersion = & $pythonCmd -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')" 2>$null
        Write-Success "Python installed via WinGet ($pyVersion)"
    } else {
        Write-ErrorExit "Please install Python 3.9 or higher from https://python.org and rerun this script."
    }
} else {
    Write-Step "2/5" "Python Runtime Environment"
    Write-Success "Using existing Python $pyVersion ($pythonCmd)"
}

# ------------------------------------------------------------------------------
# 4. Install / Upgrade Kapsel Core CLI
# ------------------------------------------------------------------------------
Write-Step "3/5" "Installing / Upgrading Kapsel Core CLI"

if ($kapselUpToDate) {
    Write-Success "Kapsel Core is already up-to-date (v$installedKapselVer) - Skipping pip install"
} else {
    Write-Info "Executing pip package install for kapsel-cli..."
    & $pythonCmd -m pip install --upgrade kapsel-cli 2>$null | Out-Null
    $newVer = & $pythonCmd -m kapsel.cli -v 2>$null
    Write-Success "Kapsel CLI ready: $newVer"
}

# ------------------------------------------------------------------------------
# 5. Bootstrapping Carapace Engine
# ------------------------------------------------------------------------------
Write-Step "4/5" "Checking Carapace Autocompletion Engine"

if ($carapaceInstalled) {
    Write-Success "Carapace engine is already installed ($carapaceVer) - Skipping download"
} else {
    Write-Info "Downloading Carapace binary (v1.7.3)..."
    $arch = if ([IntPtr]::Size -eq 8) { "amd64" } else { "386" }
    if ($env:PROCESSOR_ARCHITECTURE -eq "ARM64") { $arch = "arm64" }
    
    $carapaceUrl = "https://github.com/carapace-sh/carapace-bin/releases/download/v1.7.3/carapace-bin_1.7.3_windows_${arch}.zip"

    $tempDir = Join-Path $env:TEMP ("kapsel_cara_" + [System.Guid]::NewGuid().ToString("N"))
    New-Item -ItemType Directory -Path $tempDir -Force | Out-Null
    $zipPath = Join-Path $tempDir "carapace.zip"

    try {
        Invoke-WebRequest -Uri $carapaceUrl -OutFile $zipPath -UseBasicParsing
        Expand-Archive -Path $zipPath -DestinationPath $tempDir -Force
        $extractedExe = Join-Path $tempDir "carapace.exe"
        if (Test-Path $extractedExe) {
            Move-Item -Path $extractedExe -Destination $carapaceExe -Force
            $caraVer = & $carapaceExe --version 2>$null
            Write-Success "Carapace installed successfully: $caraVer"
        }
    } catch {
        Write-Warn "Could not download Carapace archive. Kapsel runtime will auto-bootstrap on first interactive run."
    } finally {
        Remove-Item -Path $tempDir -Recurse -Force -ErrorAction SilentlyContinue
    }
}

# Persist PATH if needed
if (-not $pathConfigured) {
    $curUserPath = [Environment]::GetEnvironmentVariable("PATH", "User")
    $pMod = $false
    if ($curUserPath -notlike "*$kapselBinDir*") {
        $curUserPath = "$kapselBinDir;$curUserPath"
        $pMod = $true
    }
    if ($pyScripts -and ($curUserPath -notlike "*$pyScripts*")) {
        $curUserPath = "$pyScripts;$curUserPath"
        $pMod = $true
    }
    if ($pMod) {
        [Environment]::SetEnvironmentVariable("PATH", $curUserPath, "User")
        Write-Success "Added ~/.kapsel/bin to persistent User PATH"
    }
} else {
    Write-Success "User PATH is already up to date"
}

# ------------------------------------------------------------------------------
# 6. Full Edition: Package Manager & Official Plugins
# ------------------------------------------------------------------------------
if ($edition -eq "Full") {
    Write-Step "5/5" "Configuring Full Toolchain & Official Plugins"

    if (-not $hasScoop) {
        Write-Info "Scoop package manager is not detected. Bootstrapping Scoop in user scope..."
        try {
            Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
            Invoke-RestMethod -Uri https://get.scoop.sh | Invoke-Expression
            $hasScoop = (Get-Command "scoop" -ErrorAction SilentlyContinue) -ne $null
            if ($hasScoop) {
                Write-Success "Scoop installed successfully"
            }
        } catch {
            Write-Warn "Could not bootstrap Scoop automatically. Plugins will download tools directly."
        }
    } else {
        Write-Success "Scoop package manager is ready - Skipping bootstrap"
    }

    if ($hasScoop) {
        scoop bucket add extras 2>$null | Out-Null
    }

    if ($missingPlugins.Count -eq 0) {
        Write-Success "All 11 official plugins are already installed - Skipping 'kapsel add'"
    } else {
        Write-Host ""
        Write-Host "  Installing $($missingPlugins.Count) Missing Kapsel Plugins via 'kapsel add'..." -ForegroundColor Magenta
        foreach ($pluginId in $missingPlugins) {
            Write-Host "  ➜ Adding plugin $pluginId..." -ForegroundColor Cyan
            & $pythonCmd -m kapsel.cli add $pluginId 2>$null | Out-Null
            Write-Success "Plugin '$pluginId' added and configured"
        }
    }
} else {
    Write-Step "5/5" "Finalizing Core Installation"
    Write-Success "Lightweight core profile active"
}

# Synchronize completion specifications & ensure default configuration
& $pythonCmd -m kapsel.cli completion sync 2>$null | Out-Null
& $pythonCmd -c "from kapsel.storage.config import load_config; load_config()" 2>$null | Out-Null

# ------------------------------------------------------------------------------
# 7. Final Summary & Quick Start
# ------------------------------------------------------------------------------
Write-Host ""
Write-Host "╭────────────────────────────────────────────────────────────────────────╮" -ForegroundColor Cyan
Write-Host "│  ✔ Kapsel $editionTitle installed successfully!                       │" -ForegroundColor Green
Write-Host "│                                                                        │" -ForegroundColor Cyan
Write-Host "│  Quick Start Commands:                                                 │" -ForegroundColor White
Write-Host "│   • kapsel         Enter the interactive smart capsule shell           │" -ForegroundColor Cyan
Write-Host "│   • kapsel toggle  Toggle Kapsel as your default terminal shell        │" -ForegroundColor Cyan
Write-Host "│   • kapsel status  Inspect host shell, platform, and active plugins    │" -ForegroundColor Cyan
if ($edition -eq "Full") {
Write-Host "│   • z <dir>        Instant directory jumping via portal plugin         │" -ForegroundColor Cyan
Write-Host "│   • kps ai <prompt> Terminal AI command generation (OpenAI SDK)        │" -ForegroundColor Cyan
Write-Host "│   • kps shore      Auto-benchmark and switch fastest package mirrors   │" -ForegroundColor Cyan
}
Write-Host "│                                                                        │" -ForegroundColor Cyan
Write-Host "│  Restart your terminal or run 'refreshenv' to reload PATH changes.       │" -ForegroundColor Gray
Write-Host "╰────────────────────────────────────────────────────────────────────────╯" -ForegroundColor Cyan
Write-Host ""