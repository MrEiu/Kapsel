# ☁️ KPS-Server：Kapsel 云端用户与多端加密漫游网关

`KPS-Server` 是一个独立的轻量级云服务，专门负责：
1. **用户注册与设备配对**（`device_id` 与 `sync_key` 鉴权）；
2. **端到端加密漫游同步**（只保存用户在本地经 AES-256 加密的配置密文 Blob，保护用户隐私）。

---

## 🚀 部署方式

### 1. 本地单机或 VPS 运行（零外部依赖）
```bash
python server.py --port 8000
```

### 2. Docker 容器化一键部署
```bash
docker-compose up -d
```
