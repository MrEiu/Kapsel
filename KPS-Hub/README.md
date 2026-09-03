# 🚀 KPS-Hub：Kapsel 指令云仓库独立服务端

`KPS-Hub` 是专门为 **Kapsel 智能终端胶囊** 提供中央指令仓库、软件包索引、pwsh 原生映射与跨端漫游账号服务的独立后端项目。

它完全与客户端解耦，拥有独立的数据存储、管理工具与 REST API 服务，支持容器化（Docker）与一键独立部署。

---

## 📂 目录结构与模块说明

```
KPS-Hub/
├── server.py              # 独立 REST API 服务（纯 Python 标准库零依赖，可平滑启用 FastAPI/Uvicorn）
├── db.py                  # 服务端专用 SQLite 数据库引擎 (registry.db)
├── seed.py                # 官方默认基线种子数据（git, scoop, python, npm, docker 等及 pwsh 映射）
├── admin.py               # 服务端独立运维 CLI 工具（增删改查软件包、指令、映射与导入导出）
├── Dockerfile             # 官方轻量容器构建清单
├── docker-compose.yml     # 一键生产环境容器编排文件
├── requirements.txt       # 可选性能加速依赖 (fastapi, uvicorn)
└── registry.db            # 服务端主数据源 (SQLite Master)
```

---

## 🛠️ 快速启动与运维管理

### 1. 本地免安装极速运行（零依赖）
无需安装任何额外第三方依赖，直接使用系统 Python 启动服务：
```bash
cd KPS-Hub
python server.py --port 8000
```
服务将在 `http://0.0.0.0:8000` 监听。

### 2. 启用 FastAPI / Uvicorn 高性能并发模式
```bash
pip install -r requirements.txt
python server.py --fastapi --port 8000
```

### 3. Docker 一键容器化部署
```bash
cd KPS-Hub
docker-compose up -d --build
```

---

## 🔌 核心 REST API 接口清单

| 方法 | 接口路径 | 作用说明 |
| :--- | :--- | :--- |
| `GET` | `/health` | 服务健康检查与版本确认 |
| `GET` | `/api/v1/stats` | 查看仓库总量（收录软件数、指令数、pwsh 映射数等） |
| `GET` | `/api/v1/packages` | 获取所有收录的软件包列表（支持 `?platform=windows` 过滤） |
| `GET` | `/api/v1/packages/{software}` | 获取指定软件详情与全部子命令集 |
| `GET` | `/api/v1/mappings` | 获取独立终端转义模板（默认 `?shell=pwsh`） |
| `GET` | `/api/v1/search?q={query}` | 跨软件、指令、映射的全局全文模糊搜索 |
| `GET` | `/api/v1/bundle` | **一键获取全量仓库快照**（供客户端冷启动或全量同步使用） |
| `POST` | `/api/v1/auth/register` | 胶囊用户注册与设备指纹登记（多端云漫游） |

---

## 🧰 服务端命令行运维管理 (`admin.py`)

在服务器端，可以直接通过 `python admin.py` 管理云端仓库：

```bash
# 1. 查看服务端数据库指标与状态
python admin.py status

# 2. 重新初始化官方默认基线数据
python admin.py seed

# 3. 软件包增删查
python admin.py pkg list
python admin.py pkg add rust --desc "Rust 编译工具链" --platform universal
python admin.py pkg del rust

# 4. 软件子指令增删查
python admin.py cmd list git
python admin.py cmd add git rebase "git rebase" --desc "变基操作"

# 5. 原生映射增删查
python admin.py map list --shell pwsh
python admin.py map add "grep" "Select-String {{args}}" --desc "文本过滤" --shell pwsh

# 6. 全量数据导出与导入备份
python admin.py export -o backup.json
python admin.py import backup.json
```
