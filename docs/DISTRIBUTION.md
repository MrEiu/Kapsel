# 📦 Kapsel 跨平台发布与分发体系规范 (DISTRIBUTION.md)

本文档面向项目维护者，详细规范 Kapsel-CLI 在各大主流包管理平台（**PyPI**, **Scoop**, **Homebrew**, **APT/Debian**）的发布、构建与上架流程。

---

## 🗺️ 架构分发矩阵 (Distribution Architecture)

```mermaid
flowchart TD
    Repo["Kapsel Core (Git Repository)"] -->|"git push origin v0.1.3"| GHA["GitHub Actions CI/CD (build_binaries.yml)"]
    
    subgraph 自动云编译三端机器码 (GitHub Actions)
        GHA --> Win["Windows Runner ➔ kapsel-windows-x86_64.zip"]
        GHA --> Mac["macOS Runner ➔ kapsel-macos-universal.tar.gz"]
        GHA --> Lin["Ubuntu Runner ➔ kapsel-linux-x86_64.tar.gz & kapsel_amd64.deb"]
        Win & Mac & Lin --> Checksums["自动计算 checksums.txt (SHA256)"]
        Checksums --> GHRelease["GitHub Releases 附件发布"]
    end
    
    subgraph 各主流平台生态接入
        GHRelease -->|"提供二进制 zip"| ScoopBucket["Windows: Scoop (MrEiu/scoop-bucket)"]
        GHRelease -->|"提供 tar.gz"| BrewTap["macOS/Linux: Homebrew (MrEiu/homebrew-tap)"]
        GHRelease -->|"提供 .deb"| DebianAPT["Linux: APT / dpkg -i kapsel_amd64.deb"]
        Repo -->|"twine upload"| PyPI["全平台 Python: PyPI (kapsel-cli)"]
    end
```

---

## 1. 🐍 PyPI 官方源发布 (已打通)

- **软件包名称**：`kapsel-cli`
- **发布页面**：[https://pypi.org/project/kapsel-cli/](https://pypi.org/project/kapsel-cli/)
- **用户安装指令**：
  ```bash
  # 推荐隔离安装
  pipx install kapsel-cli
  
  # 或标准全局升级
  pip install --upgrade kapsel-cli
  ```
- **维护者一键发布指令**：
  ```powershell
  # 1. 推进版本号并构建
  python -m build
  
  # 2. 上传到 PyPI (使用 UTF-8 编码避免 Windows GBK 字符异常)
  $env:PYTHONUTF8="1"; python -m twine upload dist/kapsel_cli-<version>*
  ```

---

## 2. 🪟 Windows: Scoop 上架指南

Scoop 是 Windows 开发者首选的命令行包管理器。

### 步骤 1：在 GitHub 创建专属 Bucket 仓库
1. 在 GitHub 创建公开仓库：**`https://github.com/MrEiu/scoop-bucket`**；
2. 在该仓库根目录下新建 `bucket/` 文件夹；
3. 将 Kapsel 项目中的 [`packaging/scoop/kapsel.json`](file:///c:/Users/meru6/Desktop/Kapsel/packaging/scoop/kapsel.json) 复制到该仓库的 `bucket/kapsel.json` 并提交。

### 步骤 2：用户端安装体验
全球任何 Windows 用户只需在 PowerShell 中运行：
```powershell
# 1. 添加您的官方 Bucket
scoop bucket add kapsel https://github.com/MrEiu/scoop-bucket

# 2. 安装 Kapsel
scoop install kapsel
```

### 自动升级机制 (`autoupdate`):
`kapsel.json` 已配置 `checkver: "github"` 和 `autoupdate`，当 GitHub 产生新 Release 时，Scoop 官方或自建同步机器人会自动检测新版本并更新哈希。

---

## 3. 🍎 macOS & Linux: Homebrew (Brew) 上架指南

Homebrew 是 macOS 与众多 Linux 开发者的标配。

### 步骤 1：在 GitHub 创建 Tap 仓库
1. 在 GitHub 创建公开仓库，命名必须是：**`https://github.com/MrEiu/homebrew-tap`**；
2. 在该仓库根目录创建 `Formula/` 文件夹；
3. 将本项目中的 [`packaging/homebrew/kapsel.rb`](file:///c:/Users/meru6/Desktop/Kapsel/packaging/homebrew/kapsel.rb) 复制到 `Formula/kapsel.rb` 并提交。

### 步骤 2：用户端安装体验
```bash
# 1. 关联您的官方 Tap
brew tap MrEiu/tap

# 2. 安装 Kapsel
brew install kapsel
```

---

## 4. 🐧 Linux (Debian / Ubuntu): APT (.deb) 上架指南

### 方案 A：直接分发 GitHub Releases `.deb`（推荐）
每次发版，GitHub Actions 均会自动调用 [`packaging/debian/build_deb.py`](file:///c:/Users/meru6/Desktop/Kapsel/packaging/debian/build_deb.py)，生成标准 Debian 安装包 `kapsel_<version>_amd64.deb`。

**用户端一行流安装体验**：
```bash
# 下载并安装
curl -LO https://github.com/MrEiu/Kapsel/releases/latest/download/kapsel_amd64.deb
sudo dpkg -i kapsel_amd64.deb

# 校验安装
kapsel --version
kps --version
```

### 方案 B：通过 GitHub Pages 免费搭建 APT 软件源
1. 创建 `MrEiu/apt-repo` 仓库并开启 GitHub Pages；
2. 利用开源 Action（如 `apt-repo-action`），每次发版自动将生成的 `.deb` 索引并签名推送到 Pages；
3. 用户端只需添加一次 source.list：
   ```bash
   echo "deb [trusted=yes] https://mreiu.github.io/apt-repo/ stable main" | sudo tee /etc/apt/sources.list.d/kapsel.list
   sudo apt update && sudo apt install kapsel
   ```

---

## 5. 🚀 维护者发版标准 Checklist (一次发版，全网就绪)

每次需要发布新版本时：
1. **修改版本号**：遵循“逢 9 进 1”更新 `pyproject.toml` 和 `kapsel/__init__.py`（如 `0.1.3` ➔ `0.1.4`）；
2. **PyPI 立即就位**：
   ```powershell
   python -m build
   $env:PYTHONUTF8="1"; python -m twine upload dist/kapsel_cli-<new_version>*
   ```
3. **推送 Git Tag 触发全平台多系统云编译**：
   ```powershell
   git commit -am "chore(release): bump version to v0.1.4"
   git tag v0.1.4
   git push origin master --tags
   ```
4. **云端自动收获产物**：
   - GitHub Actions 自动生成 Windows `.zip`、Linux `.tar.gz`、macOS `.tar.gz`、Debian `.deb` 以及 `checksums.txt`；
   - 自动在 GitHub Releases 上创建发布包；
   - Scoop 和 Brew 用户立即同步更新！
