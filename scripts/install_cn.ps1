# ==============================================================================
# Kapsel - 中国大陆用户一键高速安装与激活脚本 (PowerShell)
# 自动通过国内镜像代理从 GitHub Release 极速拉取官方完整大包并一键归位激活。
# 用法:
#   irm https://ghproxy.net/https://raw.githubusercontent.com/MrEiu/Kapsel/master/scripts/install_cn.ps1 | iex
# ==============================================================================

[CmdletBinding()]
param(
    [string]$Version = "latest",
    [switch]$KeepBundle
)

$ErrorActionPreference = "Stop"

function Write-Banner {
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host "   Kapsel 官方完整版国内一键极速激活脚本 (Windows)           " -ForegroundColor Cyan
    Write-Host "============================================================" -ForegroundColor Cyan
}

Write-Banner

# 1. 架构检测
$arch = if ([IntPtr]::Size -eq 8) { "x64" } else { "x86" }
if ($env:PROCESSOR_ARCHITECTURE -eq "ARM64") {
    $arch = "arm64"
}

$bundleName = "kapsel-bundle-windows-${arch}.zip"
$relTag = if ($Version -eq "latest") { "latest/download" } else { "download/v${Version}" }

$ghReleaseUrl = "https://github.com/MrEiu/Kapsel/releases/${relTag}/${bundleName}"

# 国内高速镜像代理矩阵
$acceleratorUrls = @(
    "https://ghproxy.net/${ghReleaseUrl}",
    "https://mirror.ghproxy.com/${ghReleaseUrl}",
    "https://gh-proxy.com/${ghReleaseUrl}",
    $ghReleaseUrl
)

$tempDir = Join-Path ([System.IO.Path]::GetTempPath()) ("kapsel_install_" + [System.Guid]::NewGuid().ToString().Substring(0, 8))
New-Item -ItemType Directory -Path $tempDir -Force | Out-Null

$zipPath = Join-Path $tempDir $bundleName
$downloadSuccess = $false

Write-Host "==> 正在连接高速镜像拉取完整一体包 ($bundleName)..." -ForegroundColor Cyan

foreach ($url in $acceleratorUrls) {
    try {
        Write-Host "  -> 尝试镜像源: $url" -ForegroundColor DarkGray
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        $ProgressPreference = 'SilentlyContinue'
        Invoke-WebRequest -Uri $url -OutFile $zipPath -TimeoutSec 45
        if ((Test-Path $zipPath) -and ((Get-Item $zipPath).Length -gt 1048576)) {
            Write-Host "  [✔] 极速下载完成！包体积: $([math]::Round((Get-Item $zipPath).Length / 1MB, 2)) MB" -ForegroundColor Green
            $downloadSuccess = $true
            break
        }
    } catch {
        Write-Host "  [!] 镜像连接超时或暂未发布该版本大包，尝试下一个通道..." -ForegroundColor DarkYellow
    }
}

$unpackDir = Join-Path $tempDir "unpacked"

if ($downloadSuccess) {
    Write-Host "==> 正在解压完整一体包并分发归位..." -ForegroundColor Cyan
    Expand-Archive -Path $zipPath -DestinationPath $unpackDir -Force
    
    # 查找 setup.ps1 脚本
    $setupScript = Get-ChildItem -Path $unpackDir -Filter "setup.ps1" -Recurse | Select-Object -First 1
    if ($setupScript) {
        Write-Host "==> 正在启动全自动归位激活程序..." -ForegroundColor Cyan
        & $setupScript.FullName
    } else {
        Write-Error "解压后未找到 setup.ps1 激活脚本。"
    }
} else {
    Write-Host "`n[提示] GitHub Release 大包尚未发布或网络完全阻断。" -ForegroundColor Yellow
    Write-Host "==> 自动启动智能降级安装器 (直接配置国内镜像与工具链)..." -ForegroundColor Cyan
    
    # 降级模式：从本地脚本或源码拉取
    $scriptUrl = "https://ghproxy.net/https://raw.githubusercontent.com/MrEiu/Kapsel/master/scripts/install_tools_windows.ps1"
    $fallbackScript = Join-Path $tempDir "install_tools_windows.ps1"
    try {
        Invoke-WebRequest -Uri $scriptUrl -OutFile $fallbackScript -TimeoutSec 20
        & $fallbackScript
    } catch {
        Write-Error "无法获取降级脚本，请检查网络设置。"
    }
}

# 清理临时文件
if (-not $KeepBundle -and (Test-Path $tempDir)) {
    Remove-Item -Path $tempDir -Recurse -Force -ErrorAction SilentlyContinue
}

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "部署全部就绪！打开新终端输入 kapsel 即可体验完整版 Kapsel。" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
