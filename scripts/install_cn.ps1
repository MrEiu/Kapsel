# ==============================================================================
# Kapsel - 中国大陆用户高速安装与全自动配置脚本 (Windows PowerShell)
# 自动通过国内高速镜像代理拉取安装包与工具链，免翻墙，一键归位激活。
#
# 【推荐用法】先使用国内镜像下载脚本到本地，再执行脚本安装（最稳健，规避网络中断与策略限制）：
#   Invoke-WebRequest -Uri "https://ghproxy.net/https://raw.githubusercontent.com/MrEiu/Kapsel/master/scripts/install_cn.ps1" -OutFile "install_cn.ps1"
#   Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned -Force
#   .\install_cn.ps1
#
# 【极速用法】一行流管道直接执行：
#   irm https://ghproxy.net/https://raw.githubusercontent.com/MrEiu/Kapsel/master/scripts/install_cn.ps1 | iex
# ==============================================================================

[CmdletBinding()]
param(
    [string]$Version = "latest",
    [switch]$KeepBundle
)

$ErrorActionPreference = "Continue"

function Write-Banner {
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host "   Kapsel 官方完整版国内一键极速激活脚本 (Windows)           " -ForegroundColor Cyan
    Write-Host "============================================================" -ForegroundColor Cyan
}

Write-Banner

# 1. 架构检测与用户目录定义
$arch = if ([IntPtr]::Size -eq 8) { "x64" } else { "x86" }
if ($env:PROCESSOR_ARCHITECTURE -eq "ARM64") {
    $arch = "arm64"
}

$userProfile = if ($env:USERPROFILE) { $env:USERPROFILE } else { [Environment]::GetFolderPath("UserProfile") }
$kapselHome = Join-Path $userProfile ".kapsel"
$kapselBinDir = Join-Path $kapselHome "bin"
if (-not (Test-Path $kapselBinDir)) {
    New-Item -ItemType Directory -Path $kapselBinDir -Force | Out-Null
}

$relTag = if ($Version -eq "latest") { "latest/download" } else { "download/v${Version}" }
$tempDir = Join-Path ([System.IO.Path]::GetTempPath()) ("kapsel_install_" + [System.Guid]::NewGuid().ToString().Substring(0, 8))
New-Item -ItemType Directory -Path $tempDir -Force | Out-Null

$downloadSuccess = $false

# 国内高速镜像代理前缀列表
$mirrorPrefixes = @(
    "https://ghproxy.net/",
    "https://mirror.ghproxy.com/",
    "https://gh-proxy.com/"
)

# ------------------------------------------------------------------------------
# 阶段 1: 优先尝试从 GitHub Releases 拉取全功能一体包 (kapsel-bundle-windows-*.zip)
# ------------------------------------------------------------------------------
$bundleName = "kapsel-bundle-windows-${arch}.zip"
$ghBundleUrl = "https://github.com/MrEiu/Kapsel/releases/${relTag}/${bundleName}"
$zipPath = Join-Path $tempDir $bundleName

Write-Host "==> [阶段 1/3] 正在尝试通过高速镜像拉取全量一体离线包..." -ForegroundColor Cyan

foreach ($prefix in $mirrorPrefixes) {
    $url = "${prefix}${ghBundleUrl}"
    try {
        Write-Host "  -> 尝试镜像源: $url" -ForegroundColor DarkGray
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        $ProgressPreference = 'SilentlyContinue'
        Invoke-WebRequest -Uri $url -OutFile $zipPath -TimeoutSec 30
        if ((Test-Path $zipPath) -and ((Get-Item $zipPath).Length -gt 1048576)) {
            Write-Host "  [✔] 极速下载完成！包体积: $([math]::Round((Get-Item $zipPath).Length / 1MB, 2)) MB" -ForegroundColor Green
            $downloadSuccess = $true
            break
        }
    } catch {
        # Continue to next mirror
    }
}

if ($downloadSuccess) {
    $unpackDir = Join-Path $tempDir "unpacked"
    Write-Host "==> 正在解压完整一体包并分发归位..." -ForegroundColor Cyan
    Expand-Archive -Path $zipPath -DestinationPath $unpackDir -Force
    $setupScript = Get-ChildItem -Path $unpackDir -Filter "setup.ps1" -Recurse | Select-Object -First 1
    if ($setupScript) {
        Write-Host "==> 正在启动全自动归位激活程序..." -ForegroundColor Cyan
        & $setupScript.FullName
    }
} else {
    # --------------------------------------------------------------------------
    # 阶段 2: 尝试拉取轻量级预编译独立二进制包 (kapsel-windows-x86_64.zip)
    # --------------------------------------------------------------------------
    Write-Host "==> [阶段 2/3] 正在尝试通过高速镜像拉取预编译独立二进制单文件..." -ForegroundColor Cyan
    $binZipName = "kapsel-windows-x86_64.zip"
    $ghBinUrl = "https://github.com/MrEiu/Kapsel/releases/${relTag}/${binZipName}"
    $binZipPath = Join-Path $tempDir $binZipName
    $binDownloaded = $false

    foreach ($prefix in $mirrorPrefixes) {
        $url = "${prefix}${ghBinUrl}"
        try {
            Write-Host "  -> 尝试独立二进制镜像: $url" -ForegroundColor DarkGray
            [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
            $ProgressPreference = 'SilentlyContinue'
            Invoke-WebRequest -Uri $url -OutFile $binZipPath -TimeoutSec 25
            if ((Test-Path $binZipPath) -and ((Get-Item $binZipPath).Length -gt 524288)) {
                Write-Host "  [✔] 独立二进制下载完成！" -ForegroundColor Green
                $binDownloaded = $true
                break
            }
        } catch {
            # Try next mirror
        }
    }

    if ($binDownloaded) {
        Write-Host "==> 正在部署独立二进制到 ~/.kapsel/bin/..." -ForegroundColor Cyan
        $unpackBinDir = Join-Path $tempDir "unpacked_bin"
        Expand-Archive -Path $binZipPath -DestinationPath $unpackBinDir -Force
        Get-ChildItem -Path $unpackBinDir -Filter "*.exe" -Recurse | ForEach-Object {
            Copy-Item -Path $_.FullName -Destination (Join-Path $kapselBinDir $_.Name) -Force
            Write-Host "  [✔] 已部署: $($_.Name)" -ForegroundColor Green
        }
    } else {
        # ----------------------------------------------------------------------
        # 阶段 3: 使用清华大学国内 PyPI 镜像源在线安装 kapsel-cli
        # ----------------------------------------------------------------------
        Write-Host "==> [阶段 3/3] 使用国内清华大学镜像源 (TUNA) 安装 kapsel-cli..." -ForegroundColor Cyan
        $hasPython = (Get-Command "python" -ErrorAction SilentlyContinue) -ne $null
        if ($hasPython) {
            try {
                python -m pip install --upgrade kapsel-cli -i https://pypi.tuna.tsinghua.edu.cn/simple --quiet
                Write-Host "  [✔] kapsel-cli 已通过国内 PyPI 镜像极速安装成功！" -ForegroundColor Green
            } catch {
                Write-Host "  [!] PyPI 镜像安装警告，继续配置系统环境..." -ForegroundColor Yellow
            }
        } else {
            Write-Host "  [!] 未检测到系统 Python，建议安装 Python 3.9+ 或下载 Release 预编译独立包。" -ForegroundColor Yellow
        }
    }

    # 运行工具链补充安装器 (Carapace, Zoxide, Mise 等)
    Write-Host "`n==> 正在通过国内镜像加速拉取配套工具链安装器..." -ForegroundColor Cyan
    $toolsScriptUrl = "https://ghproxy.net/https://raw.githubusercontent.com/MrEiu/Kapsel/master/scripts/install_tools_windows.ps1"
    $fallbackScript = Join-Path $tempDir "install_tools_windows.ps1"
    try {
        Invoke-WebRequest -Uri $toolsScriptUrl -OutFile $fallbackScript -TimeoutSec 25
        & $fallbackScript
    } catch {
        Write-Host "  [!] 工具链安装脚本已跳过，您可以随时运行 kps 自动补充缺失工具。" -ForegroundColor DarkYellow
    }
}

# 确保 ~/.kapsel/bin 位于用户 PATH
$currentUserPath = [Environment]::GetEnvironmentVariable("Path", [EnvironmentVariableTarget]::User)
if ($currentUserPath -notlike "*$kapselBinDir*") {
    [Environment]::SetEnvironmentVariable("Path", "$currentUserPath;$kapselBinDir", [EnvironmentVariableTarget]::User)
    $env:Path = "$env:Path;$kapselBinDir"
    Write-Host "  [✔] 已将 $kapselBinDir 永久添加至用户 PATH。" -ForegroundColor Green
}

# 清理临时文件
if (-not $KeepBundle -and (Test-Path $tempDir)) {
    Remove-Item -Path $tempDir -Recurse -Force -ErrorAction SilentlyContinue
}

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "   🎉 Kapsel 国内极速安装配置完成！" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  - 核心主命令:   kapsel (或 kps)"
Write-Host "  - 查看运行状态: kapsel status"
Write-Host "  - 查阅完整手册: kps help"
Write-Host "  提示: 请重新打开一个新的 PowerShell 窗口使全局 PATH 环境变量生效。`n"

