# ==============================================================================
# Kapsel - Carapace Completion Engine Installer for Windows (PowerShell)
# Automatically downloads and installs the official 'carapace-bin' standalone binary
# into ~/.kapsel/bin/carapace.exe (No administrator permissions required).
# ==============================================================================

[CmdletBinding()]
param(
    [string]$Version = "1.7.3"
)

$ErrorActionPreference = "Stop"

Write-Host "=== Kapsel Carapace Completion Engine Installer ===" -ForegroundColor Cyan

# 1. Detect Architecture
$arch = if ([IntPtr]::Size -eq 8) { "amd64" } else { "386" }
if ($env:PROCESSOR_ARCHITECTURE -eq "ARM64") {
    $arch = "arm64"
}

$zipName = "carapace-bin_${Version}_windows_${arch}.zip"
$downloadUrl = "https://github.com/carapace-sh/carapace-bin/releases/download/v${Version}/${zipName}"
$mirrorUrl = "https://ghproxy.net/${downloadUrl}"

$userProfile = if ($env:USERPROFILE) { $env:USERPROFILE } else { [Environment]::GetFolderPath("UserProfile") }
$installDir = Join-Path $userProfile ".kapsel\bin"
$targetExe = Join-Path $installDir "carapace.exe"

Write-Host "Platform: Windows ($arch)"
Write-Host "Version:  v$Version"
Write-Host "Target:   $targetExe"
Write-Host ""

if (-not (Test-Path $installDir)) {
    New-Item -ItemType Directory -Path $installDir -Force | Out-Null
}

$tempDir = Join-Path ([System.IO.Path]::GetTempPath()) ([System.Guid]::NewGuid().ToString())
New-Item -ItemType Directory -Path $tempDir -Force | Out-Null

try {
    $zipPath = Join-Path $tempDir $zipName
    Write-Host "==> Downloading $zipName..." -ForegroundColor Cyan

    $downloaded = $false
    try {
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        Invoke-WebRequest -Uri $downloadUrl -OutFile $zipPath -TimeoutSec 30
        $downloaded = $true
    } catch {
        Write-Host "Notice: Direct GitHub download failed. Trying mirror fallback..." -ForegroundColor Yellow
        try {
            Invoke-WebRequest -Uri $mirrorUrl -OutFile $zipPath -TimeoutSec 30
            $downloaded = $true
        } catch {
            Write-Error "Failed to download $zipName. Please check your network connection."
        }
    }

    if ($downloaded) {
        Write-Host "==> Extracting carapace.exe..." -ForegroundColor Cyan
        Expand-Archive -Path $zipPath -DestinationPath $tempDir -Force
        $extractedExe = Join-Path $tempDir "carapace.exe"
        if (Test-Path $extractedExe) {
            Move-Item -Path $extractedExe -Destination $targetExe -Force
            Write-Host "==> Verifying installation..." -ForegroundColor Cyan
            $ver = & $targetExe --version
            Write-Host "✔ Successfully installed Carapace ($ver)!" -ForegroundColor Green
            Write-Host "Location: $targetExe" -ForegroundColor Green
            Write-Host "Kapsel will automatically detect Carapace in ~/.kapsel/bin."
        } else {
            Write-Error "carapace.exe was not found inside the downloaded archive."
        }
    }
} finally {
    if (Test-Path $tempDir) {
        Remove-Item -Path $tempDir -Recurse -Force -ErrorAction SilentlyContinue
    }
}
