# 📦 Kapsel-CLI 独立免环境可执行文件打包工具箱 (Packager Toolkit)

本目录提供针对 **情况 2：全平台原生单文件可执行二进制程序** 的打包脚本与多系统云编译配置。

---

## 🎯 打包产物规格 (严格只打包 Kapsel-CLI 客户端)

| 目标系统 | 编译产物 | 依赖环境 | 输出路径 |
| :--- | :--- | :--- | :--- |
| **Windows** | `kapsel.exe` & `kps.exe` | **0 依赖**（免装 Python） | `dist/bin/windows/` |
| **Linux** | `kapsel` & `kps` (ELF 64位) | **0 依赖**（免装 Python） | `dist/bin/linux/` |
| **macOS** | `kapsel` & `kps` (Mach-O) | **0 依赖**（免装 Python） | `dist/bin/macos/` |

---

## 🚀 本地一键打包方式

### 1. 打包当前操作系统
直接在终端运行：
```powershell
python packaging/build.py
```
脚本会自动探测当前是 Windows 还是 Linux，清理旧缓存并一键生成对应的原生二进制文件！

### 2. 强制清理并重新编译
```powershell
python packaging/build.py --clean
```

---

## ☁️ 跨 3 大操作系统（Windows + Linux + macOS）云端自动构建

因为生成原生 C/C++ 机器码二进制通常需要目标操作系统的底层库，我们为您配套配置了 **GitHub Actions 3 端矩阵流水线**：

1. 流水线配置文件：`packaging/build_matrix_ci.yml`（已同步至 `.github/workflows/build_binaries.yml`）；
2. **触发方式**：
   - 每次打标签推送：`git push origin v0.2.0`；
   - 或在 GitHub 仓库页面的 **Actions** 标签点击 **Run workflow**。
3. **构建流程**：
   - GitHub 会并行启动 3 台原生虚拟机：`windows-latest`、`ubuntu-latest`、`macos-latest`；
   - 各自执行 `packaging/build.py` 生成原生二进制；
   - 自动打包为 `.zip` 与 `.tar.gz`，并挂载到 Release 页面供全球用户下载！
