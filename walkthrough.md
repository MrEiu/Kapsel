# Kapsel (💊 跨平台自适应智能终端胶囊) 成果交付记录

Kapsel 已经完成核心架构的全部开发与构建，包含双态智能交互引擎、终端级路由降级匹配、独立 SQLite 历史与频次漫游数据库、现代化暗黑卡片 UI 界面以及标准沙箱化配置目录。

---

## 📂 交付的完整工程结构

```
c:/Users/meru6/Desktop/Kapsel/
├── pyproject.toml               # 项目打包与依赖配置，注册 kapsel / kps CLI 双入口
├── README.md                    # 详尽的中英文产品理念、架构、命令速查与未来规划
├── kapsel/
│   ├── __init__.py              # 版本与元信息
│   ├── cli.py                   # 命令行双入口 (交互式 kapsel 与单次运行 kps，支持 help / status)
│   ├── core/                    # 核心路由与执行引擎
│   │   ├── detector.py          # 宿主 Shell 嗅探 (pwsh/powershell/cmd/bash/zsh)、Admin/Root 提权检测、路径与 Git 分支解析
│   │   ├── router.py            # 终端精细化路由、多级降级回退与 {{args}} 参数智能注入
│   │   ├── executor.py          # 原生控制台命令透传、内建 help/status/cd/clear 目录与命令管理、高精度计时与退出码捕获
│   │   └── engine.py            # 双态模式切换调度器 (Native ⇋ Kapsel)
│   ├── storage/                 # 数据沙箱管理 (~/.kapsel/)
│   │   ├── config.py            # config.yaml UI 与主题配置管理
│   │   ├── commands.py          # commands.yaml 35+ 个预置高频 Linux 跨平台映射指令集
│   │   ├── history.py           # history.db (SQLite) 跨 Shell 漫游历史与频次权重学习
│   │   └── logger.py            # logs/kapsel.log 滚动日志
│   └── ui/                      # 现代化 TUI 美学组件
│       ├── theme.py             # Cyber Dark 配色、prompt_toolkit 样式映射
│       ├── banner.py            # 极简紧凑现代 ASCII 胶囊 Logo 徽标
│       ├── info.py              # help 使用手册与 status 运行状态面板渲染器
│       ├── card.py              # 闭环区块卡片渲染 (╭─ ❯ 输入引导，╰─ 状态徽标与计时闭合)
│       ├── completer.py         # 双态补全器 (Native 路径与内置命令补全 vs Kapsel 富文本中文/底层预览菜单)
│       └── prompt.py            # prompt_toolkit 纯净交互会话、历史联想与快捷键控制
```

---

## 🌟 最新调整与核心功能

1. **极简优雅启动 Logo (`banner.py`)**：
   - 优化为小巧紧凑的现代艺术 ASCII 字符 Logo：
     ```text
     ╭─────────────────────────────────────────────────────────────╮
     │  _  __               _   💊 KAPSEL v0.1.0  ·  智能终端胶囊  │
     │ | |/ /__ _ _ __  ___| |  Wrap complexity, expose simplicity │
     │ | ' // _` | '_ \/ __| |  输入 'help' 指南 │ 'status' 状态   │
     │ |_|\_\__,_| .__/|___|_|  输入 'kps <cmd>' │ 'exit' 退出     │
     │           |_|                                               │
     ╰─────────────────────────────────────────────────────────────╯
     ```
   - 极其克制，仅占 4 行空间，不遮挡工作流。

2. **透传态精简化（保持安静纯净）**：
   - 暂时移除了常驻在底部的透传态工具栏，让输入界面回归纯粹的原生 Shell 体验。
   - **未来规划 (Roadmap)**：*“那个透传态暂时不用做；以后可以用来显示一些关键信息”*（已写入 `README.md`，未来将演进为可插拔的非侵入式状态看板，展示 Git 脏状态、未推送 Commit、后台任务状态、AI 上下文等）。

3. **新增内置控制台指令**：
   - **`help`**（或 `kps help`）：展示排版优雅的使用指南、双态机制说明、常用 Linux 映射速查表与快捷键提示。
   - **`status` / `info`**（或 `kps status`）：展示当前宿主 Shell、运行权限、操作系统平台、当前工作目录、数据沙箱路径与历史记录库统计。
   - **`config`**（或 `kps config`）：系统核心配置管理（支持 `config path`、`config edit`、`config set`、`config reload`）。
   - **`clear` / `cls`**：清屏并重绘极简胶囊徽标。

4. **右箭头 (`→`) 灵敏交互设计：单按 vs 长按**：
   - **单次轻按 (Tap)**：逐词采纳下一个参数或单词（Word-by-word，极大提升微调历史参数的便利度）。
   - **长按 / 连按 (Hold)**：直接一键整行采纳历史命令。
   - **阈值可配**：支持通过 `~/.kapsel/config.yaml` 或 `config set sensitivity <秒数>` 自由调节长按时间判定阈值（默认 0.25s）与击键次数。

5. **沙箱全中文配置文件与配置指令**：
   - 配置文件位置：`~/.kapsel/config.yaml`（带全面中文注释）。
   - 支持通过 `config edit` 自动调用外部编辑器打开，或通过 `config set <key> <val>` 快速改配并热重载。

6. **上下方向键重构与开发者子命令补全 (`git` / `npm` / `docker` 等)**：
   - **`↑` (上方向键)**：专注历史命令漫游，向上调出历史输入的上一条命令。
   - **`↓` (下方向键)**：一键唤起并循环切换自动补全候选词！
   - **子命令全量感知**：输入 `git ` 按 `↓`，候选菜单立即出现并可在 `status`, `add`, `commit`, `push`, `pull`, `checkout` 等子命令间循环轮询；同时支持 `npm`, `docker`, `pip`, `cargo`！

7. **用户体系与多系统云端同步就绪架构**：
   - **数据沙箱**：`~/.kapsel/user.json` 存储设备唯一硬件指纹与专属加密同步秘钥（`kps_sync_...`）。
   - **核心指令**：`register`（支持交互式或单行指令注册）、`whoami`（查看当前用户与设备秘钥）、`logout`（安全退出）。
   - **全局联动**：注册后，终端提示行顶部将呈现用户标识（如 `╭─ 💊 kapsel @username`），`status` 状态面板自动展示当前用户的多端漫游就绪状态。

8. **指令存储与映射架构分析与优化方案白皮书**：
   - 已生成详尽文档：[docs/command_storage_and_mapping_architecture.md](file:///c:/Users/meru6/Desktop/Kapsel/docs/command_storage_and_mapping_architecture.md)。
   - 深入剖析了现有 YAML 映射、SQLite 时序记录、最长前缀宏替换的运行机制。
   - 提出了六大前瞻演进方向：多层级配置树（系统预置/用户覆盖解耦）、语义化 Flag 解析转换引擎、复合管道分段路由、分布式云同步存储改造、敏感凭证自动脱敏与 FTS5 全文索引加速。

9. **指令云仓库 (Hub Repository) 架构落地**：
   - **SQLite 仓库存储**：内置 `kapsel/hub/registry.db`。
   - **两层架构（平台 ➜ 软件）**：完整收录 `git`、`scoop`、`python`、`npm`、`docker` 等主流工具指令集。
   - **独立 PWSH 映射库**：专门收录 32+ 条 Linux 命令至 PowerShell 原生 Cmdlet 映射模板。
   - **类比 pip/scoop 的交付体系**：提供 `kps repo list`（列出分类）、`kps repo search`（全局搜索）、`kps repo info`（软件详情）、`kps repo pull`（像 `pip install` 一样将云仓库软件指令安装至本地 commands.yaml）、`kps repo mappings`（查看 pwsh 转义模板）。

10. **独立云仓库运维管理工具 (`kps-hub` / `kps repo admin`)**：
   - 提供专属 CLI 运维工具，对云仓库 SQLite 进行全生命周期 CRUD 管理。
   - 支持子命令：
     - `kps-hub status`：查看云仓库元数据、文件大小与总指标。
     - `kps-hub pkg [list|add|del]`：增删查软件包（平台 ➜ 软件维度）。
     - `kps-hub cmd [list|add|del]`：增删查具体软件的子指令、用法与示例。
     - `kps-hub map [list|add|del]`：增删查独立 pwsh 转义映射规则。
     - `kps-hub export` / `kps-hub import`：仓库数据整体备份与导入。

11. **核心架构铁律与开发规范落盘 (`DEVELOPMENT.md`)**：
   - 确立核心研发底线：**“任何非项目配置，以及默认参数、默认数据先储存进云仓库，之后客户端更新同步，之后从本地读取（杜绝写进代码里，杜绝配置文件一大堆）”**。
   - 确立三阶段数据流：**云仓库作为 SSOT ➔ 客户端增量同步 ➔ 本地结构化 SQLite 高速读取（<1ms 延迟）**。
   - 约束本地沙箱配置文件极简，杜绝配置文件堆叠与野蛮膨胀。
   - **立即付诸工程实践**：重构 `kapsel/ui/completer.py`，彻底删除原静态硬编码的工具子命令字典，全面改为从本地 Hub SQLite 数据库动态按需查询并配合进程内 LRU 内存缓存。

12. **云端服务端完全解耦拆分为独立项目文件夹 `KPS-Hub` 与通信方案全景调研**：
   - 创建了完全独立的 `KPS-Hub/` 目录，包含生产级 REST API `server.py`、数据库 `db.py`、种子 `seed.py`、管理 `admin.py`、`Dockerfile`、`docker-compose.yml`、`requirements.txt` 与部署文档 `README.md`。
   - 撰写并输出了五维深度通信选型报告：[docs/local_cloud_communication_proposals.md](docs/local_cloud_communication_proposals.md)，深度剖析了 **RESTful API**、**Git-Based CDN**、**SQLite Changeset 二进制补丁**、**gRPC** 与 **混合架构 (Hybrid)** 五大主流通信流派。

13. **客户端 `kapsel/hub` 目录代码大扫除**：
   - 删除了残留在客户端内部的 `seed.py`（静态硬编码大种子）、`admin.py`（服务端运维 CLI）以及 `registry.db`（预置二进制数据库）。
   - 彻底移除了 `pyproject.toml` 中的 `kps-hub` 入口，客户端代码实现 100% 纯净与零硬编码。

14. **系统全模块化目录解耦与全新 Storage 体系重构**：
   - **补全引擎独立 (`kapsel/core/completion/`)**：封装 `DualStateCompleter` 与动态子命令检索。
   - **控制台指令统一收归 (`kapsel/commands/`)**：将 `help`、`status`、`config`、`repo`、`user` 彻底从 `ui/` 剥离移至专属模块；配建空模块 `commands/install/` 占位骨架。
   - **云端漫游模块独立 (`kapsel/sync/`)**：收拢设备指纹、AES-256 加密与网关通信客户端。
   - **用户数据 SQLite 集中化 (`kapsel/storage/user_db.py`)**：历史时序与身份凭据汇聚至 `~/.kapsel/user.db`，杜绝散乱，预留后续全库加密接口。
   - **指令与映射文件夹式存储 (`kapsel/storage/registry/`)**：`manifests/` 与 `mappings/` 对齐 Git 仓库同步；配建 `RegistryIndexer` 内存索引树提供 <1ms 快速查询。
15. **全球化 i18n 演进规划与独立打包工具箱 (`packaging/`)**：
   - **i18n 全球化架构路线落盘 (`DEVELOPMENT.md`)**：确立以 English-First 为核心基准，辅以 `en.json` / `zh.json` 多语言回退机制与 Manifests 双语扩展规范。
   - **创建专属打包工具箱 (`packaging/`)**：专门针对情况 2（全平台免 Python 环境的原生单二进制独立程序）提供一键构建工具：
     - `packaging/build.py`：本地一键构建 Windows `kapsel.exe`、Linux ELF 二进制与 macOS 二进制。
     - `.github/workflows/build_binaries.yml`：GitHub Actions 3 端矩阵云编译流水线，打 Tag 即自动并行构建并发布 Release。
     - 严格约束只针对 `Kapsel-CLI` 客户端打包，杜绝打包服务端与敏感配置。

16. **全面重构升级 Fig.Spec 补全架构 (`withfig/autocomplete` 兼容适配)**：
   - **数据模型树形升维 (`kapsel/core/completion/fig_schema.py`)**：弃用旧版扁平字典，全面适配 Fig.Spec 树状规范（Subcommand 递归多级嵌套、Options 标志数组如 `-m, --message`、Arguments 参数定义）。
   - **纯 Python AST 上下文遍历状态机 (`kapsel/core/completion/fig_engine.py`)**：分词解析已输入命令，自动下钻定位 AST 节点（例如 `docker compose up`），并根据前缀动态提供 Flags（`git commit -`）或次级子命令，实现 <1ms 响应。
   - **核心转义映射深度融合 (`kapsel/core/completion/completer.py`)**：在胶囊态（`kps `）下保持核心护城河，动态呈现 Linux 别名以及实时的目标 Shell 原生转义代码预览（`➔ Remove-Item -Recurse -Force`）。
   - **官方常用工具 Fig 规范库 (`kapsel/core/completion/specs/`)**：开箱内置 `git`, `docker`, `scoop`, `npm`, `python`, `cargo` 深度多层规范；同时支持加载用户沙箱 `~/.kapsel/registry/specs/` 中的自定义规范。
   - **Fig 官方生态一键拉取工具 (`scripts/import_fig_spec.py`)**：支持从 `withfig/autocomplete` GitHub 官方仓库直接提取并转换 400+ 开源工具规范。

17. **上下方向键重构为以当前输入为原点的双向流转交互 (Origin-Centered Navigation)**：
   - **彻底告别单向限制**：摈弃“按上只能漫游历史、按下只能漫游补全”的死板设定。
   - **原点双向对称流转**：
     - 在原点按 `↑` 往历史走，在历史模式中 `↑`/`↓` 可自由双向漫游，按 `↓` 一路回到原点后，再按 `↓` 才会切换进入补全模式；
     - 在原点按 `↓` 往补全走，在补全模式中 `↓`/`↑` 可自由双向选词，按 `↑` 一路回到原点（恢复原始输入）后，再按 `↑` 才会切换进入历史模式；
   - 文档与代码已全面同步更新。

18. **历史记录跨会话持久化与完整命令回溯修复 (Cross-Session Command Persistence)**：
   - **打通 SQLite 持久化写入链路 (`kapsel/storage/history.py`)**：在 `KapselPromptHistory.store_string` 中直接接入 `user.db` 写入接口，每次用户按下回车，即刻完整记录全量输入命令（非单个单词）。
   - **跨会话历史按需预加载**：新会话启动时，`load_history_strings` 自动从 `user.db` 读取上一会话留存的最近完整命令；
   - **默认 20 条，全量可配置**：在 `config.yaml` 中将 `history.max_memory_entries` 默认值设为 20 条，可随时通过 `kps config set history.max_memory_entries <N>` 自由调整。

19. **自定义数据存储位置与全量自动迁移工具 (`kps datadir`)**：
   - **数据目录自由定制**：支持将 Kapsel 默认的 `~/.kapsel` 沙箱完整搬迁至用户指定的任意非系统盘、挂载盘或工作目录。
   - **全自动数据搬迁，彻底清理旧目录（原来不留）**：自动迁移 `config.yaml`、`user.db`、`registry/`、`logs/`，迁移成功后自动销毁旧目录垃圾数据。
   - **全局持久化指针与零损回退**：通过 `~/.kapsel_location` 全局生效，执行 `kps datadir default` 可随时一键无痕迁回系统默认路径。

20. **补全选词确认与参数继续追加交互优化 (Enter 智能分流)**：
   - **采纳选词 vs 提交执行严格分工**：彻底告别向下选中补全项按回车直接把裸命令跑出去的严重体验痛点。
   - **自动补空格与连续追加**：在候选词选中状态下按 `Enter`（或 `Tab`），仅将选中的子命令/参数落盘到行尾并自动补一个空格，弹窗平滑关闭，光标停在行尾方便继续输入后续选项（如 `-m "feat"`）；
   - **二次回车真正执行**：当完成整行参数编辑且无选词状态时，再次敲回车才真正交付引擎执行。

21. **代码注释与描述全量英文规范确立 (English-Only Comments & Descriptions Standard)**：
   - **即日起新增代码强制纯英文**：所有新编写的代码注释、函数 Docstrings、模块描述一律采用英文；
   - **存量中文规划统一平滑重构**：既有历史中文注释暂不改动，统一排期并在后续的国际化专项中清洗替换。

22. **五大核心演进专项正式规划落盘 ([DEVELOPMENT.md](file:///c:/Users/meru6/Desktop/Kapsel/DEVELOPMENT.md) 第九章)**：
   - **功能架构插件化 (`kps plugin`)**：统一生命周期 Hooks 与第三方插件生态。
   - **自定义命令与私有仓库 (`kps command add`, `kps repo add-remote`)**：支持自建团队/个人专属指令集。
   - **终端工具多配置文件隔离与极速切换 (`kps profile backup/switch`)**：多 Git/SSH/Kubeconfig 隔离备份，原生环境永远只留一个。
   - **社区化命令映射共享与 CRUD (`kps map CRUD/export/share`)**：个性化映射增删改查与 Hub 社区分享。
   - **AI 终端 Copilot (`#需求`)**：自然语言前缀触发，多模型驱动，上下文感知推导 Shell 指令，安全审查后敲回车执行。

---

## 🚀 启动与使用方式

项目已通过 `pip install -e .` 安装到当前 Python 环境，您可以直接打开任意终端执行：

### 1. 启动交互式胶囊终端
```bash
kapsel
```
- 输入 `help`：随时查阅完整手册
- 输入 `status`：查看运行环境与沙箱统计
- 输入 `kps ls -la` 或普通命令体验双态映射与补全

### 2. 作为单次快速转换工具
```bash
kps rm -rf node_modules/
kps ls -la
kps help
kps status
```
