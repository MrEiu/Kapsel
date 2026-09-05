# ==============================================================================
# Kapsel - Complete Toolchain Installer for Windows (PowerShell)
# Installs all required terminal utilities for Kapsel Core and official plugins:
# - Core: carapace (carapace-bin)
# - Plugins: zoxide, mise, chsrc, aichat, pueue, chezmoi, pet, tealdeer, fzf
# - Python CLI: meta-package-manager (mpm), thefuck
#
# Adheres to Kapsel Dependency Philosophy:
# Standard package managers first -> Fallback to ~/.kapsel/bin/ -> Zero virtualenvs.
# ==============================================================================

[CmdletBinding()]
param(
    [switch]$Force,
    [switch]$SkipPythonTools
)

$ErrorActionPreference = "Continue"

function Write-Step {
    param([string]$Title)
    Write-Host "`n====> $Title" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "  [OK] $Message" -ForegroundColor Green
}

function Write-Info {
    param([string]$Message)
    Write-Host "  [INFO] $Message" -ForegroundColor Yellow
}

function Write-Warn {
    param([string]$Message)
    Write-Host "  [WARN] $Message" -ForegroundColor DarkYellow
}

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "   Kapsel All-in-One Toolchain Installer (Windows)          " -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

$userProfile = if ($env:USERPROFILE) { $env:USERPROFILE } else { [Environment]::GetFolderPath("UserProfile") }
$kapselBinDir = Join-Path $userProfile ".kapsel\bin"
if (-not (Test-Path $kapselBinDir)) {
    New-Item -ItemType Directory -Path $kapselBinDir -Force | Out-Null
}

# ------------------------------------------------------------------------------
# 1. Check and Bootstrap Scoop Package Manager (User-level, non-admin)
# ------------------------------------------------------------------------------
Write-Step "Checking Package Manager: Scoop"
$hasScoop = (Get-Command "scoop" -ErrorAction SilentlyContinue) -ne $null

if (-not $hasScoop) {
    Write-Info "Scoop is not installed. Installing Scoop in user scope..."
    try {
        Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
        Invoke-RestMethod -Uri https://get.scoop.sh | Invoke-Expression
        $hasScoop = (Get-Command "scoop" -ErrorAction SilentlyContinue) -ne $null
        if ($hasScoop) {
            Write-Success "Scoop installed successfully."
        }
    } catch {
        Write-Warn "Could not automatically install Scoop. Standalone binaries will be downloaded directly."
    }
} else {
    Write-Success "Scoop is already installed."
}

if ($hasScoop) {
    Write-Info "Ensuring Scoop buckets (extras) are added..."
    scoop bucket add extras 2>$null | Out-Null
}

# ------------------------------------------------------------------------------
# 2. Install Core & Plugin Binary Tools
# ------------------------------------------------------------------------------
Write-Step "Installing Binary Tools (Rust / Go / C)"

$binaryTools = @(
    @{ Name = "carapace"; Cmd = "carapace"; ScoopPkg = "carapace-bin"; Desc = "Core Multi-Shell Autocompletion Engine" },
    @{ Name = "zoxide";   Cmd = "zoxide";   ScoopPkg = "zoxide";       Desc = "Smart Directory Teleportation (portal)" },
    @{ Name = "mise";     Cmd = "mise";     ScoopPkg = "mise";         Desc = "Tool Runtime & Env Manager (init)" },
    @{ Name = "chsrc";    Cmd = "chsrc";    ScoopPkg = "chsrc";        Desc = "Fast Mirror Switcher (shore)" },
    @{ Name = "aichat";   Cmd = "aichat";   ScoopPkg = "aichat";       Desc = "Terminal AI Assistant (ai)" },
    @{ Name = "pueue";    Cmd = "pueue";    ScoopPkg = "pueue";        Desc = "Task Queue & Daemon Manager (autopilot)" },
    @{ Name = "chezmoi";  Cmd = "chezmoi";  ScoopPkg = "chezmoi";      Desc = "Dotfile & Profile Manager (profile)" },
    @{ Name = "pet";      Cmd = "pet";      ScoopPkg = "pet";          Desc = "Command Snippet Recorder (rec)" },
    @{ Name = "tealdeer"; Cmd = "tldr";     ScoopPkg = "tealdeer";     Desc = "Fast Command Cheat Sheets (help)" },
    @{ Name = "fzf";      Cmd = "fzf";      ScoopPkg = "fzf";          Desc = "Interactive Fuzzy Finder (companion)" }
)

foreach ($tool in $binaryTools) {
    $cmdExists = (Get-Command $tool.Cmd -ErrorAction SilentlyContinue) -ne $null
    $localBinExists = (Test-Path (Join-Path $kapselBinDir "$($tool.Cmd).exe"))

    if ($cmdExists -or $localBinExists) {
        Write-Success "$($tool.Name) ($($tool.Desc)) is already installed."
        continue
    }

    Write-Info "Installing $($tool.Name)..."

    $installed = $false
    # Method A: Try Scoop
    if ($hasScoop) {
        scoop install $tool.ScoopPkg 2>$null | Out-Null
        if ((Get-Command $tool.Cmd -ErrorAction SilentlyContinue) -ne $null) {
            Write-Success "Installed $($tool.Name) via Scoop."
            $installed = $true
        }
    }

    # Method B: Try Winget fallback
    if (-not $installed -and (Get-Command "winget" -ErrorAction SilentlyContinue)) {
        winget install --id $tool.ScoopPkg --accept-source-agreements --accept-package-agreements --silent 2>$null | Out-Null
        if ((Get-Command $tool.Cmd -ErrorAction SilentlyContinue) -ne $null) {
            Write-Success "Installed $($tool.Name) via Winget."
            $installed = $true
        }
    }

    # Special handler for carapace if package managers failed
    if (-not $installed -and $tool.Name -eq "carapace") {
        Write-Info "Bootstrapping Carapace binary via Kapsel standalone installer..."
        $carapaceScript = Join-Path $PSScriptRoot "install_carapace.ps1"
        if (Test-Path $carapaceScript) {
            & $carapaceScript
            $installed = (Test-Path (Join-Path $kapselBinDir "carapace.exe"))
        }
    }

    # Special handler for chsrc if package manager failed
    if (-not $installed -and $tool.Name -eq "chsrc") {
        Write-Info "Downloading precompiled chsrc.exe into ~/.kapsel/bin..."
        try {
            $chsrcUrl = "https://github.com/RubyMetric/chsrc/releases/latest/download/chsrc-x64-windows.exe"
            $chsrcDest = Join-Path $kapselBinDir "chsrc.exe"
            [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
            Invoke-WebRequest -Uri $chsrcUrl -OutFile $chsrcDest -TimeoutSec 30
            Write-Success "Installed chsrc into ~/.kapsel/bin/chsrc.exe"
            $installed = $true
        } catch {
            Write-Warn "Direct download for chsrc failed."
        }
    }

    if (-not $installed) {
        Write-Warn "Could not automatically install $($tool.Name). You can install it manually via Scoop or Winget."
    }
}

# ------------------------------------------------------------------------------
# 3. Install Python CLI Tools (mpm, thefuck)
# ------------------------------------------------------------------------------
if (-not $SkipPythonTools) {
    Write-Step "Installing Python CLI Tools (mpm, thefuck)"

    $hasPython = (Get-Command "python" -ErrorAction SilentlyContinue) -ne $null
    if (-not $hasPython) {
        Write-Warn "Python 3 is not found in PATH. Skipping Python CLI tools."
    } else {
        # Check pipx
        $hasPipx = (Get-Command "pipx" -ErrorAction SilentlyContinue) -ne $null
        if (-not $hasPipx) {
            Write-Info "Installing pipx via python -m pip..."
            python -m pip install --user pipx --quiet 2>$null
            python -m pipx ensurepath --force 2>$null | Out-Null
            $hasPipx = (Get-Command "pipx" -ErrorAction SilentlyContinue) -ne $null
        }

        # 3a. meta-package-manager (mpm)
        $hasMpm = (Get-Command "mpm" -ErrorAction SilentlyContinue) -ne $null
        if ($hasMpm) {
            Write-Success "mpm (meta-package-manager) is already installed."
        } else {
            Write-Info "Installing meta-package-manager (mpm)..."
            if ($hasPipx) {
                pipx install meta-package-manager --quiet 2>$null
            } else {
                python -m pip install --user meta-package-manager --quiet 2>$null
            }
            if ((Get-Command "mpm" -ErrorAction SilentlyContinue) -ne $null) {
                Write-Success "mpm installed successfully."
            } else {
                Write-Warn "mpm installed into user scripts. Please restart your terminal to reload PATH."
            }
        }

        # 3b. thefuck
        $hasFuck = (Get-Command "thefuck" -ErrorAction SilentlyContinue) -ne $null
        if ($hasFuck) {
            Write-Success "thefuck is already installed."
        } else {
            Write-Info "Installing thefuck..."
            if ($hasPipx) {
                pipx install thefuck --quiet 2>$null
            } else {
                python -m pip install --user thefuck --quiet 2>$null
            }
            if ((Get-Command "thefuck" -ErrorAction SilentlyContinue) -ne $null) {
                Write-Success "thefuck installed successfully."
            }
        }
    }
}

# ------------------------------------------------------------------------------
# 4. Ensure ~/.kapsel/bin is in User PATH
# ------------------------------------------------------------------------------
Write-Step "Configuring User PATH"
$currentUserPath = [Environment]::GetEnvironmentVariable("Path", [EnvironmentVariableTarget]::User)
if ($currentUserPath -notlike "*$kapselBinDir*") {
    Write-Info "Adding $kapselBinDir to User PATH..."
    [Environment]::SetEnvironmentVariable("Path", "$currentUserPath;$kapselBinDir", [EnvironmentVariableTarget]::User)
    $env:Path = "$env:Path;$kapselBinDir"
    Write-Success "Added ~/.kapsel/bin to User PATH."
} else {
    Write-Success "~/.kapsel/bin is already in User PATH."
}

# ------------------------------------------------------------------------------
# 5. Trigger Spec Synchronization
# ------------------------------------------------------------------------------
Write-Step "Synchronizing Kapsel Completion Specifications"
if (Get-Command "kps" -ErrorAction SilentlyContinue) {
    kps completion sync
} else {
    Write-Info "Kapsel CLI command not yet globally bound. Running spec sync via Python..."
    python -c "from kapsel.completion.spec_manager import CarapaceSpecManager; CarapaceSpecManager().sync_specs(force=True)" 2>$null
}

Write-Host "`n============================================================" -ForegroundColor Green
Write-Host "   All Kapsel Tools Installation Complete!                  " -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host "You can now run 'kapsel' or 'kps status' to enjoy the full experience.`n"
