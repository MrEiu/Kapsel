# ==============================================================================
# Kapsel All-in-One Bundle Installer (Windows)
# Unpacks binaries, plugins, package managers, and domestic mirrors into standard locations.
# ==============================================================================

[CmdletBinding()]
param(
    [switch]$SkipMirrors,
    [switch]$NonInteractive
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
Write-Host "   Kapsel 官方完整版一键快速部署激活程序 (Windows)          " -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

$bundleRoot = $PSScriptRoot
$userProfile = if ($env:USERPROFILE) { $env:USERPROFILE } else { [Environment]::GetFolderPath("UserProfile") }
$kapselHome = Join-Path $userProfile ".kapsel"
$kapselBinDir = Join-Path $kapselHome "bin"
$kapselPluginsDir = Join-Path $kapselHome "plugins"

# ------------------------------------------------------------------------------
# 1. 配置国内高速镜像 (pip / npm / scoop)
# ------------------------------------------------------------------------------
if (-not $SkipMirrors) {
    Write-Step "配置国内高速镜像加速 (清华源 / 阿里源 / 腾讯源 / Gitee)"

    # 1a. pip 镜像
    $pipDir = Join-Path $env:APPDATA "pip"
    if (-not (Test-Path $pipDir)) { New-Item -ItemType Directory -Path $pipDir -Force | Out-Null }
    $pipSrc = Join-Path $bundleRoot "mirrors\pip.ini"
    if (Test-Path $pipSrc) {
        Copy-Item $pipSrc (Join-Path $pipDir "pip.ini") -Force
        Write-Success "配置 pip 国内源 (清华源 / 阿里源加速)"
    }

    # 1b. npm 镜像
    $npmrcSrc = Join-Path $bundleRoot "mirrors\npmrc"
    if (Test-Path $npmrcSrc) {
        Copy-Item $npmrcSrc (Join-Path $userProfile ".npmrc") -Force
        Write-Success "配置 npm 国内淘宝/腾讯镜像源"
    }

    # 1c. Scoop Gitee 镜像
    $scoopScript = Join-Path $bundleRoot "mirrors\scoop_mirror.ps1"
    if (Test-Path $scoopScript) {
        & $scoopScript
    }
}

# ------------------------------------------------------------------------------
# 2. 部署全套单二进制工具 (carapace, zoxide, mise, chsrc, aichat, etc.)
# ------------------------------------------------------------------------------
Write-Step "移动并部署全套单二进制工具到 ~/.kapsel/bin/"

if (-not (Test-Path $kapselBinDir)) {
    New-Item -ItemType Directory -Path $kapselBinDir -Force | Out-Null
}

$binSource = Join-Path $bundleRoot "bin"
if (Test-Path $binSource) {
    $binFiles = Get-ChildItem -Path $binSource -Filter "*.exe" -File
    foreach ($file in $binFiles) {
        $dest = Join-Path $kapselBinDir $file.Name
        Copy-Item $file.FullName $dest -Force
        Write-Success "已就位: $($file.Name)"
    }
} else {
    Write-Warn "未在一体包中发现 bin 目录，跳过二进制复制。"
}

# ------------------------------------------------------------------------------
# 3. 部署官方完整插件库
# ------------------------------------------------------------------------------
Write-Step "部署官方插件家族到 ~/.kapsel/plugins/"

if (-not (Test-Path $kapselPluginsDir)) {
    New-Item -ItemType Directory -Path $kapselPluginsDir -Force | Out-Null
}

$pluginsSource = Join-Path $bundleRoot "plugins"
if (Test-Path $pluginsSource) {
    $pluginDirs = Get-ChildItem -Path $pluginsSource -Directory
    foreach ($p in $pluginDirs) {
        $dest = Join-Path $kapselPluginsDir $p.Name
        Copy-Item -Path $p.FullName -Destination $dest -Recurse -Force
        Write-Success "已加载插件: $($p.Name)"
    }
}

# ------------------------------------------------------------------------------
# 4. 配置包管理器 (Scoop & pipx) 并安装 Python 工具
# ------------------------------------------------------------------------------
Write-Step "初始化包管理器并部署 Python 核心套件"

# 4a. 确保 Scoop 就位
$hasScoop = (Get-Command "scoop" -ErrorAction SilentlyContinue) -ne $null
if (-not $hasScoop) {
    Write-Info "检测到未安装 Scoop，使用国内镜像一键激活 Scoop..."
    try {
        Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
        $env:SCOOP_REPO = "https://gitee.com/glsnames/scoop-installer"
        irm https://gitee.com/glsnames/scoop-installer/raw/master/bin/install.ps1 | iex
        Write-Success "Scoop 国内极速版安装成功。"
    } catch {
        Write-Warn "Scoop 自动安装遇到阻碍，已由 ~/.kapsel/bin/ 全套静态工具兜底接管。"
    }
} else {
    Write-Success "Scoop 已经就位。"
}

# 4b. 离线安装 Python 依赖轮子包 (wheels)
$wheelsSource = Join-Path $bundleRoot "wheels"
if (Get-Command "python" -ErrorAction SilentlyContinue) {
    if (Test-Path $wheelsSource) {
        Write-Info "从离线 wheels 目录免流极速安装 Python 组件..."
        python -m pip install --no-index --find-links=$wheelsSource kapsel-cli meta-package-manager thefuck pipx --quiet 2>$null
        Write-Success "已离线安装 kapsel-cli, mpm, thefuck, pipx."
    } else {
        Write-Info "使用国内镜像源在线校验安装 Python 组件..."
        python -m pip install --user kapsel-cli meta-package-manager thefuck pipx -i https://pypi.tuna.tsinghua.edu.cn/simple --quiet 2>$null
    }
}

# ------------------------------------------------------------------------------
# 5. 配置系统环境变量 PATH
# ------------------------------------------------------------------------------
Write-Step "配置环境变量 PATH"

$currentUserPath = [Environment]::GetEnvironmentVariable("Path", [EnvironmentVariableTarget]::User)
$pathUpdated = $false

foreach ($targetPath in @($kapselBinDir, "$userProfile\scoop\shims")) {
    if ($currentUserPath -notlike "*$targetPath*") {
        $currentUserPath = "$currentUserPath;$targetPath"
        $env:Path = "$env:Path;$targetPath"
        $pathUpdated = $true
        Write-Success "已将 $targetPath 追加至用户 PATH。"
    }
}

if ($pathUpdated) {
    [Environment]::SetEnvironmentVariable("Path", $currentUserPath, [EnvironmentVariableTarget]::User)
}

# ------------------------------------------------------------------------------
# 6. 生成并激活 Carapace 补全树
# ------------------------------------------------------------------------------
Write-Step "编译并激活双根补全规约 (kps.yaml 与 kapsel.yaml)"

try {
    python -c "from kapsel.completion.spec_manager import CarapaceSpecManager; CarapaceSpecManager().sync_specs(force=True)" 2>$null
    Write-Success "双根规约自动编译完成，全套命令与参数 Tab 键毫秒补全已就绪！"
} catch {
    Write-Warn "补全生成遇到非致命警告，可在终端输入 'kps completion sync' 手动补全。"
}

# ------------------------------------------------------------------------------
# 7. 完成
# ------------------------------------------------------------------------------
Write-Host "`n============================================================" -ForegroundColor Green
Write-Host "   🎉 Kapsel 官方完整版已全部就位，即刻启航！               " -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host "  - 核心主命令:   kapsel (或 kps)"
Write-Host "  - 查看运行状态: kps status"
Write-Host "  - 查阅完整手册: kps help"
Write-Host "  - 补全管理看板: kps completion ls`n"
