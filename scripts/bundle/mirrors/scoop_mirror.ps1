# ==============================================================================
# Kapsel - Scoop Domestic Mirror Configuration (China Fast Mirror)
# Switches Scoop repo and official buckets to Gitee / Domestic Mirrors
# ==============================================================================

[CmdletBinding()]
param()

$ErrorActionPreference = "Continue"

Write-Host "Configuring Scoop with domestic high-speed mirrors..." -ForegroundColor Cyan

if (-not (Get-Command "scoop" -ErrorAction SilentlyContinue)) {
    Write-Host "Notice: Scoop not detected. Setting environment for fresh domestic install..." -ForegroundColor Yellow
    $env:SCOOP_REPO = "https://gitee.com/glsnames/scoop-installer"
    return
}

try {
    # 1. Configure Gitee mirror for Scoop core
    scoop config SCOOP_REPO "https://gitee.com/squalls/scoop" 2>$null | Out-Null
    
    # 2. Re-point main and extras bucket to Gitee mirrors
    scoop bucket rm main 2>$null | Out-Null
    scoop bucket add main https://gitee.com/squalls/scoop-main 2>$null | Out-Null

    scoop bucket rm extras 2>$null | Out-Null
    scoop bucket add extras https://gitee.com/squalls/scoop-extras 2>$null | Out-Null

    Write-Host "  [OK] Scoop configured with domestic Gitee mirrors successfully." -ForegroundColor Green
} catch {
    Write-Host "  [WARN] Failed to configure domestic Scoop buckets: $_" -ForegroundColor DarkYellow
}
