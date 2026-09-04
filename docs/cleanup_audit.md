# Kapsel 代码注释与提示信息清理审计清单 (Code & Prompt Cleanup Audit)

> **审计与执行说明**：
> 本文档基于对当前 Kapsel 代码库的全面检索与分析，梳理出所有**低价值注释**、**CLI 启动冗余提示（help 外部）**、**过时/遗留术语（如“透传态”、“托管态”、“胶囊态”）**以及**违反英文规范的代码注释**，并记录清理执行状态。
>
> *(注：按指令要求，`kapsel/completion/kps/builtins/help.py` 属于系统使用手册，不在本次清理审计范围内。)*

---

## 一、CLI 启动与进入界面的冗余提示 (help 外部)

此类内容在每次用户启动 CLI 或触发交互会话时常驻打印，不仅占用宝贵的终端垂直空间，而且对高频用户造成信息干扰。

| 文件路径 | 行号 | 原始展示文本 / 内容 | 存在的问题 / 清理理由 | 整改结果与方案 | 执行状态 |
| :--- | :--- | :--- | :--- | :--- | :---: |
| [`kapsel/ui/banner.py`](file:///c:/Users/meru6/Desktop/Kapsel/kapsel/ui/banner.py#L46) | 46 | `"[dim]输入 [/][bold #00f0ff]'kapsel help'[/][dim] 使用指南  │  [/][bold #38bdf8]'kapsel status'[/][dim] 运行状态  │  [/][dim]'exit' 退出[/]"` | **典型无价值提示**：每次启动交互式 CLI 时均强制打印这三条提示，反复提示用户输入 help/status/exit，界面冗余。 | **已彻底删除该行**，保持欢迎 Banner 极简纯粹。 | ✅ 已完成 |
| [`kapsel/ui/banner.py`](file:///c:/Users/meru6/Desktop/Kapsel/kapsel/ui/banner.py#L44) | 44 | `"[bold #00f0ff]💊 KAPSEL[/] [dim]v0.1.0[/]  ·  [#e4e4e7]跨平台自适应智能终端胶囊[/]\n"` | 包含“跨平台自适应智能终端胶囊”等宣传性修饰词。 | 动态导入 `__version__` 并简化为 `[bold #00f0ff]💊 KAPSEL[/] [dim]v{__version__}[/]`。 | ✅ 已完成 |
| [`kapsel/cli.py`](file:///c:/Users/meru6/Desktop/Kapsel/kapsel/cli.py#L76-L85) | 76-85 | `Panel("[bold #10b981]✔ Kapsel 终端默认模式已开启！[/]\n\n当前终端已将 Kapsel 作为默认交互环境...\n输入 'kapsel toggle' 或 'toggle' 即可关闭退出...")` | `kapsel toggle` 启动时的全宽弹窗，文字冗长，具有强烈的临时调试卡片感。 | 精简为单行极简通知：`✔ Kapsel active. Type 'toggle' or 'exit' to quit.`。 | ✅ 已完成 |
| [`kapsel/cli.py`](file:///c:/Users/meru6/Desktop/Kapsel/kapsel/cli.py#L112-L121) | 112-121 | `Panel("[bold #00f0ff]🔌 Kapsel 终端默认模式已关闭，已退出并切回宿主终端。[/]\n[dim]随时输入 'kapsel toggle' 即可重新开启。[/]")` | 退出时的全宽提示卡片，多行文字解释，体验不够轻快。 | 精简为单行退出通知：`Exited Kapsel.`，无缝返回宿主 Shell。 | ✅ 已完成 |

---

## 二、未知指令报错与强制 help 提示

当前对于未识别的指令或子命令，存在多处硬编码中文且带有固化提示语的问题。

| 文件路径 | 行号 | 原始代码 / 提示内容 | 存在的问题 / 清理理由 | 整改结果与方案 | 执行状态 |
| :--- | :--- | :--- | :--- | :--- | :---: |
| [`kapsel/core/engine.py`](file:///c:/Users/meru6/Desktop/Kapsel/kapsel/core/engine.py#L117) | 117 | `print(f"kapsel: 未知指令 '{user_input}'。输入 'kapsel help' 查看可用指令。")` | 硬编码中文报错，且与外部现代 CLI 标准不符；冗余教导式提示。 | 改为标准 CLI 格式：`kapsel: unknown command '{user_input}'. See 'kapsel help'.`。 | ✅ 已完成 |
| [`kapsel/completion/kps/dispatcher.py`](file:///c:/Users/meru6/Desktop/Kapsel/kapsel/completion/kps/dispatcher.py#L61) | 61 | `con.print(f"[bold #f43f5e]kapsel: 未知指令 '{cmd_name}'。[/] 输入 'kapsel help' 查阅可用指令。")` | 与 `engine.py` 的报错逻辑重复，用词不一致。 | 统一格式：`kapsel: unknown command '{cmd_name}'. See 'kapsel help'.`。 | ✅ 已完成 |
| [`kapsel/completion/kps/builtins/config.py`](file:///c:/Users/meru6/Desktop/Kapsel/kapsel/completion/kps/builtins/config.py#L112-L113) | 112-113 | `con.print(f"[bold #f43f5e]未知 config 子指令: '{sub}'[/]")`<br>`con.print("[dim]可用指令: config, config path...")` | 硬编码中文，冗余子命令列举。 | 规范化为：`Unknown config subcommand: '{sub}'. See 'kapsel config --help'.`。 | ✅ 已完成 |

---

## 三、过时/遗留术语（“透传态”、“托管态”、“胶囊态” 等）

在早期交互设计中引入的“双态”、“透传态”、“托管态”等概念在迭代后已不再作为核心心智，残留在代码与注释中容易引起理解歧义。

| 文件路径 | 行号 | 原始代码 / 术语出现处 | 遗留术语分类 | 整改结果与方案 | 执行状态 |
| :--- | :--- | :--- | :--- | :--- | :---: |
| [`kapsel/completion/kps/builtins/toggle.py`](file:///c:/Users/meru6/Desktop/Kapsel/kapsel/completion/kps/builtins/toggle.py#L30) | 30, 40 | `🔌 Kapsel 终端托管模式当前处于激活状态 (Active)`<br>`✔ Kapsel 终端托管模式已就绪 (Inactive)` | **托管模式 / 托管态** | 移除大面板与“终端托管模式”，改为单行英文标准状态：`Kapsel session is active` / `Kapsel session is ready`。 | ✅ 已完成 |
| [`kapsel/completion/kps/builtins/status.py`](file:///c:/Users/meru6/Desktop/Kapsel/kapsel/completion/kps/builtins/status.py#L68) | 68, 99-100, 105 | `💊 胶囊内核版本:`<br>`⚙️ 终端默认模式: 🟢 已托管 / ⚪ 未托管`<br>`💊 KAPSEL 系统运行与环境状态看板` | **胶囊内核 / 托管态 / 看板** | 规范化国际标准术语：`Kapsel Version:`，`Session Mode: Active / Standby`，`KAPSEL System & Environment Status`。 | ✅ 已完成 |
| [`kapsel/completion/kps/builtins/datadir.py`](file:///c:/Users/meru6/Desktop/Kapsel/kapsel/completion/kps/builtins/datadir.py#L67-L78) | 67-78 | `📂 当前数据目录:`、`🏷️ 存储位置模式:`、`💊 Kapsel 数据存储目录看板` | **看板 / 中文标签** | 规范化为：`Data Directory:`，`Storage Mode: Custom Location / Default`，`Kapsel Data Directory`。 | ✅ 已完成 |
| [`kapsel/completion/completer.py`](file:///c:/Users/meru6/Desktop/Kapsel/kapsel/completion/completer.py#L175-L182) | 175-182 | `("exit", "退出胶囊会话")`<br>`("git", "Git 分布式版本控制 (Carapace 动态感知就绪)")`<br>`("docker", "Docker 容器生命周期管理 (Carapace 动态感知就绪)")`<br>`...` (全部原生工具均带 Carapace 就绪后缀) | **胶囊会话 / 动态感知就绪（过度修饰）** | 1. `exit` 说明精简为 `"Exit session"`。<br>2. 剔除所有原生工具列表中重复冗余的 `(Carapace 动态感知就绪)` 商业化后缀，统一改为标准英文精简说明。 | ✅ 已完成 |
| [`README.md`](file:///c:/Users/meru6/Desktop/Kapsel/README.md#L338-L339) | 338-339 | `- **透传态交互看板 (Native Context Stream)**：`<br>`  > *“那个透传态暂时不用做；以后可以用来显示一些关键信息”*` | **透传态 / 对话草稿引用** | 删除直接复制自历史会话的草稿式引号内容，更名为 `非侵入式交互看板 (Context Stream)`。 | ✅ 已完成 |

---

## 四、低价值与违反英文规范的代码内注释

项目规范明确要求：“*All code comments and docstrings must strictly remain in English.*” 当前部分代码文件中存在大段中文解释、选词状态注释及口语化引用。

| 文件路径 | 行号 | 原始注释内容 | 存在的问题 | 整改结果与方案 | 执行状态 |
| :--- | :--- | :--- | :--- | :--- | :---: |
| [`kapsel/ui/prompt.py`](file:///c:/Users/meru6/Desktop/Kapsel/kapsel/ui/prompt.py#L167-L173) | 167, 169, 173 | `# Check if this is continuous / long press (连按或长按)`<br>`# 长按/连续按: 直接一键采纳整行完整建议`<br>`# 单次间断按 (Tap): 根据配置逐词或整行采纳` | 夹杂中文与冗余解释。 | 全部改写为纯英文标准逻辑注释：<br>`# Continuous press: accept entire suggestion line`<br>`# Single tap: word-by-word or full line per config` | ✅ 已完成 |
| [`kapsel/ui/prompt.py`](file:///c:/Users/meru6/Desktop/Kapsel/kapsel/ui/prompt.py#L234-L255) | 234, 241-243, 255 | `# Shift-Tab: 在补全菜单中向上回退前一个候选词`<br>`# Enter (回车键):`<br>`# - 若处于候选词选中状态 (向下选定指令后): 确认采纳该词条并自动追加空格...`<br>`# - 若未在选词状态: 正常提交整行命令执行`<br>`# Tab (制表键): 选定候选词时同样一键采纳...` | 冗长的中文按键状态解释（“候选词选中状态”、“未在选词状态”）。 | 替换为简洁标准的英文描述：<br>`# Enter: accept candidate or submit command line` 等。 | ✅ 已完成 |
| [`kapsel/storage/migrate.py`](file:///c:/Users/meru6/Desktop/Kapsel/kapsel/storage/migrate.py#L5) | 5, 81 | `leaving nothing behind in the old directory ("原来不留").`<br>`# 3. Clean up source directory ("原来不留")`<br>`user_db.reset_path()` (悬空废弃引用) | 在 Docstring 与代码注释中夹带口语化的群聊/对话引用 `("原来不留")`，以及已移除的废弃模块调用。 | 清理口语化引用，移除废弃的 `user_db.reset_path()` 调用，所有异常及成功提示均改为纯英文。 | ✅ 已完成 |
| [`kapsel/__init__.py`](file:///c:/Users/meru6/Desktop/Kapsel/kapsel/__init__.py#L2) | 2 | `"""💊 Kapsel：跨平台自适应智能终端胶囊"""` | 模块入口 Docstring 使用非英文宣传语。 | 改为标准英文 docstring：<br>`"""Kapsel: Cross-platform adaptive smart terminal capsule."""` | ✅ 已完成 |
| [`kapsel/storage/config.py`](file:///c:/Users/meru6/Desktop/Kapsel/kapsel/storage/config.py#L19-L22) | 19-22 | `# "word" (逐词采纳) 或 "full" (一键采纳整行)` 等行内中文注释 | 代码内部字典注释包含中文。 | 改为纯英文枚举解释：`# "word" (word-by-word) or "full" (entire line)`。 | ✅ 已完成 |
