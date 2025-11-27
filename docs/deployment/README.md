# 部署文档

本文档介绍 CozyCognee 的部署方法和配置说明。

## 目录

- [标准 Docker Compose 部署](#标准-docker-compose-部署)
- [1Panel 部署](#1panel-部署)
- [环境配置](#环境配置)
- [服务说明](#服务说明)
- [故障排查](#故障排查)

## 标准 Docker Compose 部署

### 前置要求

- Docker 20.10+
- Docker Compose 2.0+
- 至少 8GB 可用内存
- 至少 20GB 可用磁盘空间

### 部署步骤

1. **准备环境变量**

   ```bash
   cd deployment
   cp env.example .env
   # 编辑 .env 文件
   ```

2. **配置必需的环境变量**

   至少需要配置以下变量：
   - `LLM_API_KEY`: 您的 LLM API 密钥

3. **启动核心服务**

   ```bash
   # 启动 Cognee 后端
   docker-compose up -d cognee
   
   # 查看日志
   docker-compose logs -f cognee
   ```

4. **启动可选服务**

   ```bash
   # 启动前端
   docker-compose --profile ui up -d frontend
   
   # 启动 PostgreSQL
   docker-compose --profile postgres up -d postgres
   
   # 启动 Neo4j
   docker-compose --profile neo4j up -d neo4j
   
   # 启动 ChromaDB
   docker-compose --profile chromadb up -d chromadb
   
   # 启动 Redis
   docker-compose --profile redis up -d redis
   ```

5. **验证部署**

   ```bash
   # 检查服务状态
   docker-compose ps
   
   # 测试 API
   curl http://localhost:8000/health
   ```

## 1Panel 部署

### 前置要求

- 已安装 1Panel
- Docker 和 Docker Compose（通常 1Panel 已包含）

### 部署步骤

1. **在 1Panel 中创建应用**

   - 登录 1Panel 管理界面
   - 进入"应用商店"或"容器"页面
   - 选择"Compose 项目"或"自定义应用"

2. **上传配置文件**

   - 使用 `deployment/docker-compose.1panel.yml` 文件
   - 或直接在 1Panel 中创建 Compose 项目

3. **配置环境变量**

   - 在 1Panel 界面中配置环境变量
   - 或使用 `.env` 文件

4. **配置数据卷**

   确保以下目录已正确挂载：
   - `./data/cognee` - Cognee 数据目录
   - `./data/cognee-mcp` - MCP 数据目录
   - `./data/frontend` - 前端构建缓存

5. **启动服务**

   - 在 1Panel 界面中启动服务
   - 或使用命令行：
     ```bash
     cd deployment
     docker-compose -f docker-compose.1panel.yml up -d
     ```

### 1Panel 特定配置

1Panel 版本的配置特点：

- 所有服务都设置了 `restart: unless-stopped`
- 添加了健康检查（healthcheck）
- 配置了资源限制和预留
- 数据目录使用相对路径，便于 1Panel 管理

## 环境配置

### 必需配置

- `LLM_API_KEY`: LLM API 密钥（必需）

### 数据库配置

#### SQLite（默认）

无需额外配置，适合开发和测试。

#### PostgreSQL

```env
DB_PROVIDER=postgres
DB_HOST=postgres
DB_PORT=5432
DB_NAME=cognee_db
DB_USERNAME=cognee
DB_PASSWORD=cognee
```

#### Neo4j

```env
GRAPH_DATABASE_PROVIDER=neo4j
NEO4J_URL=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=pleaseletmein
```

### 向量数据库配置

#### ChromaDB（默认）

```env
VECTOR_DB_PROVIDER=chroma
VECTOR_DB_KEY=your-secret-token
```

### LLM 提供商配置

#### OpenAI

```env
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
LLM_API_KEY=sk-...
```

#### Anthropic

```env
LLM_PROVIDER=anthropic
LLM_MODEL=claude-3-5-sonnet-20241022
LLM_API_KEY=sk-ant-...
```

#### Groq

```env
LLM_PROVIDER=groq
LLM_MODEL=llama-3.1-70b-versatile
LLM_API_KEY=gsk_...
```

## 服务说明

### 核心服务

#### cognee

- **端口**: 8000
- **功能**: Cognee 核心后端 API 服务
- **健康检查**: `http://localhost:8000/health`

#### cognee-frontend

- **端口**: 3000
- **功能**: Cognee Web 前端界面
- **启动**: `docker-compose --profile ui up -d frontend`

#### cognee-mcp

- **端口**: 8001
- **功能**: Model Context Protocol 服务器
- **启动**: `docker-compose --profile mcp up -d cognee-mcp`

### 数据库服务

#### postgres

- **端口**: 5432
- **功能**: PostgreSQL 关系型数据库（支持 pgvector）
- **启动**: `docker-compose --profile postgres up -d postgres`

#### neo4j

- **端口**: 7474 (HTTP), 7687 (Bolt)
- **功能**: Neo4j 图数据库
- **启动**: `docker-compose --profile neo4j up -d neo4j`
- **Web界面**: http://localhost:7474

#### chromadb

- **端口**: 3002
- **功能**: ChromaDB 向量数据库
- **启动**: `docker-compose --profile chromadb up -d chromadb`

#### redis

- **端口**: 6379
- **功能**: Redis 缓存和队列
- **启动**: `docker-compose --profile redis up -d redis`

## 故障排查

### 常见问题

1. **服务无法启动**

   ```bash
   # 查看日志
   docker-compose logs cognee
   
   # 检查端口占用
   netstat -tulpn | grep 8000
   ```

2. **数据库连接失败**

   - 确保数据库服务已启动
   - 检查环境变量配置
   - 验证网络连接：`docker-compose exec cognee ping postgres`

3. **LLM API 调用失败**

   - 验证 `LLM_API_KEY` 是否正确
   - 检查网络连接
   - 查看日志中的错误信息

4. **内存不足**

   - 调整 `docker-compose.yml` 中的资源限制
   - 关闭不必要的服务
   - 增加系统内存

### 日志查看

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f cognee

# 查看最近 100 行日志
docker-compose logs --tail=100 cognee
```

### 服务重启

```bash
# 重启单个服务
docker-compose restart cognee

# 重启所有服务
docker-compose restart

# 停止并重新创建服务
docker-compose down
docker-compose up -d
```

### 数据备份

```bash
# 备份 PostgreSQL
docker-compose exec postgres pg_dump -U cognee cognee_db > backup.sql

# 备份数据卷
docker run --rm -v cognee_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz /data
```

## 生产环境建议

1. **使用外部数据库**: 生产环境建议使用独立的数据库服务，而不是容器内的数据库

2. **配置 HTTPS**: 使用反向代理（如 Nginx）配置 HTTPS

3. **设置资源限制**: 根据实际需求调整 CPU 和内存限制

4. **启用日志轮转**: 配置日志管理，避免日志文件过大

5. **定期备份**: 设置自动备份策略

6. **监控告警**: 配置监控和告警系统

7. **安全加固**: 
   - 修改默认密码
   - 使用强密码
   - 限制网络访问
   - 定期更新镜像

