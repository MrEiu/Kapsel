# 💊 Kapsel 架构设计与开发规范 (DEVELOPMENT.md)

本文档是 Kapsel 项目的核心架构宪章与开发准则。所有功能迭代、代码贡献与重构均必须严格遵守本规范。

---

## 🌟 核心架构铁律 (Core Architectural Manifesto)

> ### 📌 **核心原则：**
> **“任何非项目配置，以及默认参数、默认数据先储存进云仓库，之后客户端更新同步，之后从本地读取（杜绝写进代码里，杜绝配置文件一大堆）。”**

---

## 一、 为什么必须坚持这一原则？（痛点与哲学）

在传统 CLI 工具与终端增强工具的发展过程中，开发者往往容易陷入两大设计陷阱：
1. **代码内硬编码（Data Hardcoding in Code）**：
   将大量的命令映射、工具子命令树、语法用例甚至默认参数以静态字典形式写死在 `.py` 代码中。
   - **恶果**：每次新增一条工具指令或修改模板，都必须改动核心源代码、发版重新打包。业务数据污染了底层引擎逻辑。
2. **配置文件野蛮膨胀（Config File Bloat / Sprawl）**：
   走向另一个极端，每加一个功能就往用户磁盘写一个 YAML/JSON 散装文件，导致 `~/.kapsel/` 目录出现几十个分散的配置文件。
   - **恶果**：用户不知从何改起，升级时版本冲突频繁，文件 IO 开销剧增，云端同步时难以进行原子级管理。

### 💡 Kapsel 的架构解法
通过**“云仓库集中管理 (Hub) ➔ 客户端增量同步 (Sync) ➔ 本地结构化高速读取 (Local Fast-Path)”**三阶段数据流，实现：
- **代码纯粹**：Python 源码中只有算法、执行器与交互调度逻辑，零数据硬编码。
- **磁盘清爽**：本地杜绝配置文件杂乱堆叠，所有默认指令、子命令集、平台映射统一收敛至结构化的本地 SQLite 数据库中。
- **更新即时**：云端维护一套中央指令仓库，客户端一条指令完成秒级同步更新，离线状态下毫秒级本地命中。

---

## 二、 三阶段数据流模型 (Three-Stage Data Flow)

```mermaid
flowchart TD
    subgraph 阶段 1：云仓库集中存储 (Cloud Hub SSOT)
        AdminCLI["仓库运维工具 (kps-hub)"] --> HubDB["云端中央 SQLite 仓库 (registry.db)"]
        HubDB --> TblPkg["hub_packages (平台-软件元数据)"]
        HubDB --> TblCmd["hub_commands (软件子命令集)"]
        HubDB --> TblMap["hub_mappings (独立终端转义模板)"]
    end

    subgraph 阶段 2：客户端更新同步 (Client Sync Engine)
        HubDB -->|"kps repo pull / kps repo sync"| SyncEngine["客户端增量同步器"]
        SyncEngine --> LocalDB["本地沙箱 SQLite 缓存 (~/.kapsel/registry.db)"]
    end

    subgraph 阶段 3：本地结构化高速读取 (Local Fast-Path)
        LocalDB --> LocalRuntime["本地运行时引擎 (Completer / Router / Card)"]
        LocalRuntime --> InMemCache["LRU 内存热点缓存 (0ms 击键延迟)"]
    end
```

### 1. 阶段 1：云仓库作为唯一真实数据源 (Single Source of Truth)
- 所有**非项目本身的基础配置**（如各软件的子命令清单、Linux 到 PowerShell 的转义模板、生态扩展包、各种第三方工具的语法示例等）必须首先录入到云仓库 SQLite (`registry.db`) 中。
- 严禁在代码中写死大段的静态候选字典。
- 维护人员与开发者使用独立的 `kps-hub` 命令行运维工具执行增删改查（CRUD）或批量 JSON 导入导出。

### 2. 阶段 2：客户端存储体系解耦与 Git 仓库对齐
- **指令集与映射集（文件夹式存储对齐 Git 仓库）**：
  - 本地沙箱维护 `~/.kapsel/registry/manifests/*.json` 与 `~/.kapsel/registry/mappings/*.json`。
  - 格式与 `KPS-Hub` 公开 Git 仓库 100% 对齐，可直接通过 `git pull` 或 `kps repo pull` 实现单文件精准同步。
  - 配备内存级 `RegistryIndexer` 倒排检索树，保证击键自动补全达到 **< 1ms** 的极致速度。
- **用户私有数据（SQLite 集中化存储与未来整库加密）**：
  - 用户执行时序历史 (`history`) 与个人漫游凭据 (`user_profile`) 全部收敛到单一数据库 `~/.kapsel/user.db` 中。
  - 杜绝多份散装小文件。
  - 🔮 **未来规划（加密路线）**：架构已预留整库加密与 AES 密文信封扩展点，后续可在不改变业务接口的前提下平滑接入 SQLCipher 或端到端密文同步。

### 3. 阶段 3：本地结构化高速读取 (Local Fast-Path Read)
- 客户端在交互时，所有自动补全、命令解析与参数提示，**一律从本地 SQLite 数据库按索引读取**。
- 辅以进程内 LRU 内存缓存，确保方向键补全与击键响应达到 **< 1ms** 的极致流畅度。
- 保证在无网络/飞机模式等完全断网环境下，依然拥有完整的指令与映射体验。

---

## 三、 本地配置文件极简规范 (Anti-Config-Sprawl)

为了杜绝“配置文件一大堆”，Kapsel 严格限制用户主目录下 `~/.kapsel/` 的文件数量：

```
~/.kapsel/
├── config.yaml          # 【唯一核心配置文件】全中文注释，仅存放用户个性化 UI/灵敏度覆盖
├── user.json            # 【用户身份凭据】设备指纹与加密云同步秘钥
├── history.db           # 【历史数据库】本地执行时序记录与高频词频学习库
├── registry.db          # 【云仓库本地同步副本】平台-软件指令集与 pwsh 独立映射库
└── logs/kapsel.log      # 【滚动运行日志】自动切片轮转
```

- **严禁新增碎片化配置文件**：如果需要新增参数体系，优先设计在 `registry.db` 中作为属性扩展，而非在磁盘上生成新文件。
- **保持 `config.yaml` 极度纯净**：只记录用户显式配置的个性化参数；所有未配置的默认项一律从数据库回退读取。

---

## 四、 代码重构与整改落地标准

根据本原则，项目现有代码已全面执行以下重构标准：

### 1. 工具子命令与参数补全生态架构 (`kapsel/core/completion/`)
- **规范做法**：
  全面兼容并适配 `withfig/autocomplete` 的 `Fig.Spec` 树形规范，支持递归多级子命令与 Flags 选项补全。
- > 🌟 **关于 Fig 生态兼容的特别致谢**：
  > “Fig 是我制作完功能后意外发现的；之后全面兼容了该仓库，感谢各位先贤的贡献。”

### 2. 跨平台映射指令集解耦 (`kapsel/storage/commands.py`)
- **过去做法（反面案例）**：
  在 `.py` 代码中维护数百行的 `DEFAULT_COMMANDS` 静态列表。
- **规范做法（正面案例）**：
  基线数据通过 `kapsel/hub/seed.py` 初始化进 SQLite 仓库。`CommandRegistry` 从数据库或同步流加载，代码中只保留 `CommandEntry` 数据模型与解析算法。

---

## 五、 贡献者开发检查清单 (CheckList for Contributors)

在提交任何 Pull Request 或新增功能前，请对照以下清单自检：

- [ ] **是否硬编码了数据？**：代码中是否出现了命令列表、软件子命令树、参数映射表？（如有，必须迁移至 `registry.db` 中）。
- [ ] **是否增加了新的配置文件？**：是否又在磁盘上创建了新的散装配置文件？（如无极端必要，严禁增加，统一收敛至 SQLite）。
- [ ] **数据是否支持云端同步与本地读取？**：新功能所需的数据是否支持通过 `kps repo pull` 或 `kps-hub` 进行管理并在本地离线读取？
- [ ] **性能与延迟是否达标？**：从本地 SQLite 读取的数据是否有内存缓存防护，确保交互击键响应 < 1ms？

---

## 六、 未来演进路线：全球化 i18n 多语言架构规范 (English-First Roadmap)

面向全球开发者生态，Kapsel 确立以 **“英语为主、中文自适应、优雅回退”** 的国际化标准：

### 1. English-First 核心设计原则
- **基准语言 (Base Language)**：全部代码、内置命令手册、错误排查提示、状态卡片默认以 **`en` (English)** 作为一等公民。
- **动态语言包与回退 (Fallback)**：
  - 建立 `kapsel/i18n/locales/`，收录 `en.json`（主字典）与 `zh.json`（中文语言包）。
  - 若用户语言包中缺少某个词条，系统自动 100% 回退显示英文，绝不发生白屏或抛出 KeyError。
- **Manifests 指令仓库双语规范**：
  - `KPS-Hub/manifests/*.json` 中，以 `desc` 记录标准英文说明，以 `desc_zh` 记录可选的中文对照。

### 2. 语言自适应判定层级
1. **最高优先**：CLI 临时参数（`kps --lang en status`）
2. **用户显式指定**：`config.yaml` 中配置 `core.locale: "auto" | "en" | "zh"`
3. **系统环境兜底**：自动探测 `os.environ.get("LANG")`，非中文系统一律默认纯英文交互。

---

> 💡 **总结**：
> “逻辑归逻辑，数据归仓库。轻量在云端，高速在本地。” 坚守这一原则，Kapsel 才能成为一个架构优雅、启动如飞、维护轻松的下一代终端操作胶囊！
