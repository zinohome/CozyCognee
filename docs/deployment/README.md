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
- 已构建 Docker 镜像（见下方说明）

### 重要提示

**1Panel 版本的 docker-compose 文件不包含 build 配置**，需要先构建镜像：

```bash
cd deployment
# 构建所有镜像
./scripts/build-images.sh [version]

# 或构建单个镜像
./scripts/build-image.sh cognee [version]
```

详细说明请参考 [deployment/scripts/README.md](../deployment/scripts/README.md)

### 部署步骤

1. **构建 Docker 镜像**

   ```bash
   cd deployment
   # 构建所有镜像（推荐）
   ./scripts/build-images.sh v1.0.0
   
   # 或只构建需要的镜像
   ./scripts/build-image.sh cognee v1.0.0
   ./scripts/build-image.sh cognee-frontend v1.0.0  # 可选
   ./scripts/build-image.sh cognee-mcp v1.0.0  # 可选
   ```

2. **在 1Panel 中创建应用**

   - 登录 1Panel 管理界面
   - 进入"应用商店"或"容器"页面
   - 选择"Compose 项目"或"自定义应用"

3. **上传配置文件**

   - 使用 `deployment/docker-compose.1panel.yml` 文件
   - 或直接在 1Panel 中创建 Compose 项目

4. **配置数据目录**

   确保以下目录存在并有正确权限：
   ```bash
   sudo mkdir -p /data/cognee/{data,logs,postgres,pgvector,redis,minio,neo4j/{data,logs,import,plugins},redisinsight,mcp,frontend}
   sudo chown -R $USER:$USER /data/cognee
   ```

5. **配置网络**

   确保 `1panel-network` 网络已存在：
   ```bash
   docker network ls | grep 1panel-network
   # 如果不存在，1Panel 会自动创建
   ```

6. **启动服务**

   - 在 1Panel 界面中启动服务
   - 或使用命令行：
     ```bash
     cd deployment
     docker-compose -f docker-compose.1panel.yml up -d
     ```

### 1Panel 特定配置

1Panel 版本的配置特点：

- **外部网络**: 使用 `1panel-network`（外部网络）
- **数据存储**: 所有数据存储在 `/data/cognee` 目录
- **服务标签**: 所有服务包含 `createdBy: "Apps"` 标签
- **健康检查**: 所有服务配置了健康检查
- **依赖服务**: 包含 PostgreSQL、pgvector、Redis、MinIO
- **无构建**: 不包含 build 配置，镜像需单独构建和管理

### 数据目录结构

```
/data/cognee/
├── data/          # Cognee 应用数据
├── logs/          # 应用日志
├── postgres/      # PostgreSQL 关系数据库数据
├── pgvector/      # pgvector 向量数据库数据
├── redis/         # Redis 数据
├── minio/         # MinIO 对象存储数据
├── neo4j/         # Neo4j 图数据库数据
│   ├── data/      # 数据库文件
│   ├── logs/      # 日志文件
│   ├── import/    # 导入数据目录
│   └── plugins/   # 插件目录
├── redisinsight/  # Redis Insight 数据
├── mcp/           # MCP 服务数据（可选）
└── frontend/      # 前端构建缓存（可选）
```

### 服务配置

- **cognee**: 主应用服务，端口 8000
- **cognee-mcp**: MCP 服务（可选），端口 8001
- **frontend**: 前端服务（可选），端口 3000
- **postgres**: PostgreSQL 关系数据库，端口 5432
- **pgvector**: pgvector 向量数据库（独立的 PostgreSQL 实例），端口 5433
- **redis**: Redis 缓存，端口 6379
- **minio**: MinIO 对象存储，端口 9000/9001
- **neo4j**: Neo4j 图数据库，端口 7474 (HTTP), 7687 (Bolt)
- **redisinsight**: Redis Insight 管理工具，端口 5540

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

#### pgvector（推荐）

pgvector 是 PostgreSQL 的向量扩展，将向量数据存储在 PostgreSQL 中。

```env
VECTOR_DB_PROVIDER=pgvector
# 注意: pgvector 使用关系数据库的连接配置
# 无需配置 VECTOR_DB_URL 和 VECTOR_DB_KEY
```

**配置说明**:
- CozyCognee 配置了两个独立的 PostgreSQL 服务：
  - `postgres`: 标准 PostgreSQL（端口 5432），用于关系数据
  - `pgvector`: 带 pgvector 扩展（端口 5433），用于向量数据
- 由于代码限制，pgvector 会使用关系数据库的配置
- 详细配置请参考 [服务分离配置指南](./PGVECTOR_SEPARATION.md)

**优势**:
- 服务分离，便于独立扩展和管理
- 向量数据和关系数据可以分离存储
- 支持事务和 ACID 特性

#### ChromaDB

```env
VECTOR_DB_PROVIDER=chroma
VECTOR_DB_KEY=your-secret-token
```

#### Qdrant

```env
VECTOR_DB_PROVIDER=qdrant
VECTOR_DB_URL=http://localhost:6333
VECTOR_DB_KEY=  # 可选，用于 Qdrant Cloud
```

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

