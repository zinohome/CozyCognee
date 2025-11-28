# Cognee MCP 部署指南

## 概述

Cognee MCP (Model Context Protocol) 服务器提供了将 Cognee 知识图谱功能通过 MCP 协议暴露给 IDE（如 Cursor、Claude Desktop）的能力。

## 运行模式

Cognee MCP 支持两种运行模式：

### 1. Direct Mode（直接模式）

MCP 服务器直接使用 cognee 库，需要配置所有 cognee 的环境变量。

**适用场景：**
- 独立部署 MCP 服务器
- 需要完整的 cognee 功能（包括 codify、prune 等）
- MCP 服务器和 API 服务器使用不同的数据库

**需要的环境变量：**
- 所有 cognee 的环境变量（LLM_API_KEY、数据库配置、向量数据库、图数据库等）

### 2. API Mode（API 模式）

MCP 服务器通过 HTTP 请求连接到已运行的 Cognee FastAPI 服务器。

**适用场景：**
- 已有 Cognee API 服务器在运行
- 多个 MCP 服务器共享同一个知识图谱
- 简化部署配置（不需要重复配置环境变量）

**需要的环境变量：**
- `API_URL`: Cognee API 服务器的 URL（必需）
- `API_TOKEN`: API 认证令牌（可选，如果 API 启用了认证）

**API Mode 限制：**
以下功能仅在 Direct Mode 可用：
- `codify` (代码图谱管道)
- `cognify_status` / `codify_status` (管道状态跟踪)
- `prune` (数据重置)
- `get_developer_rules` (开发者规则检索)
- `list_data` 带特定 dataset_id (详细数据列表)

基本操作（`cognify`、`search`、`delete`、`list_data` 所有数据集）在两种模式下都可用。

## Docker Compose 配置

### Direct Mode 配置

在 `docker-compose.1panel.yml` 中，cognee-mcp 服务已配置为 Direct Mode：

```yaml
cognee-mcp:
  image: cognee-mcp:latest
  container_name: cognee-mcp
  restart: unless-stopped
  profiles:
    - mcp
  ports:
    - "8001:8000"
  environment:
    # ==================== 基础配置 ====================
    - DEBUG=false
    - ENVIRONMENT=production
    - LOG_LEVEL=ERROR
    - PYTHONUNBUFFERED=1
    # ==================== LLM 配置 ====================
    - LLM_API_KEY=your-llm-api-key-here
    - LLM_PROVIDER=openai
    - LLM_MODEL=gpt-4o-mini
    - LLM_ENDPOINT=https://oneapi.naivehero.top/v1
    - LLM_MAX_TOKENS=16384
    # ==================== 数据库配置 ====================
    - DATABASE_URL=postgresql://cognee_user:cognee_password@postgres:5432/cognee_db
    - DB_PROVIDER=postgres
    - DB_HOST=postgres
    - DB_PORT=5432
    - DB_NAME=cognee_db
    - DB_USERNAME=cognee_user
    - DB_PASSWORD=cognee_password
    # ==================== 向量数据库配置 ====================
    - VECTOR_DB_PROVIDER=pgvector
    # ==================== 图数据库配置 ====================
    - GRAPH_DATABASE_PROVIDER=neo4j
    - NEO4J_URL=bolt://neo4j:7687
    - NEO4J_USER=neo4j
    - NEO4J_PASSWORD=pleaseletmein
    # ==================== Redis 配置 ====================
    - REDIS_URL=redis://:cognee_redis_password@redis:6379/0
    # ==================== 对象存储配置 ====================
    - S3_ENDPOINT=http://minio:9000
    - S3_ACCESS_KEY=minioadmin
    - S3_SECRET_KEY=minioadmin
    - S3_BUCKET_NAME=cognee-storage
    - S3_USE_SSL=false
    # ==================== MCP 配置 ====================
    - TRANSPORT_MODE=sse  # 可选: stdio, sse, http
    - MCP_LOG_LEVEL=INFO
    # ==================== 其他配置 ====================
    - EXTRAS=api,postgres,neo4j
    - TELEMETRY_DISABLED=1
  depends_on:
    cognee:
      condition: service_healthy
    postgres:
      condition: service_healthy
  volumes:
    - /data/cognee/mcp:/app/data
  networks:
    - 1panel-network
```

### API Mode 配置

如果使用 API Mode，可以简化配置：

```yaml
cognee-mcp:
  image: cognee-mcp:latest
  container_name: cognee-mcp
  restart: unless-stopped
  profiles:
    - mcp
  ports:
    - "8001:8000"
  environment:
    # ==================== 基础配置 ====================
    - DEBUG=false
    - ENVIRONMENT=production
    - PYTHONUNBUFFERED=1
    # ==================== MCP 配置 ====================
    - TRANSPORT_MODE=sse
    - MCP_LOG_LEVEL=INFO
    # ==================== API Mode 配置 ====================
    - API_URL=http://cognee:8000
    # - API_TOKEN=your-api-token  # 如果 API 启用了认证
  depends_on:
    cognee:
      condition: service_healthy
  volumes:
    - /data/cognee/mcp:/app/data
  networks:
    - 1panel-network
```

**注意：** 在 API Mode 下，不需要配置数据库、LLM、向量数据库等环境变量，因为这些都由 Cognee API 服务器处理。

## 环境变量说明

### Direct Mode 必需的环境变量

#### LLM 配置（必需）
- `LLM_API_KEY`: LLM API 密钥（必需）
- `LLM_PROVIDER`: LLM 提供商（可选，默认：openai）
- `LLM_MODEL`: 模型名称（可选，根据 provider 选择）
- `LLM_ENDPOINT`: API 端点（可选）
- `LLM_MAX_TOKENS`: 最大 token 数（可选）

#### 数据库配置
- `DATABASE_URL`: 数据库连接 URL
- `DB_PROVIDER`: 数据库提供商（postgres、sqlite）
- `DB_HOST`: 数据库主机
- `DB_PORT`: 数据库端口
- `DB_NAME`: 数据库名称
- `DB_USERNAME`: 数据库用户名
- `DB_PASSWORD`: 数据库密码

#### 向量数据库配置
- `VECTOR_DB_PROVIDER`: 向量数据库提供商（pgvector、chroma、qdrant 等）

#### 图数据库配置
- `GRAPH_DATABASE_PROVIDER`: 图数据库提供商（kuzu、neo4j）
- `NEO4J_URL`: Neo4j 连接 URL（如果使用 Neo4j）
- `NEO4J_USER`: Neo4j 用户名
- `NEO4J_PASSWORD`: Neo4j 密码

#### Redis 配置
- `REDIS_URL`: Redis 连接 URL

#### 对象存储配置
- `S3_ENDPOINT`: S3 端点
- `S3_ACCESS_KEY`: S3 访问密钥
- `S3_SECRET_KEY`: S3 密钥
- `S3_BUCKET_NAME`: S3 存储桶名称
- `S3_USE_SSL`: 是否使用 SSL

### API Mode 必需的环境变量

- `API_URL`: Cognee API 服务器的 URL（必需）
- `API_TOKEN`: API 认证令牌（可选）

### MCP 特定配置

- `TRANSPORT_MODE`: 传输模式（stdio、sse、http），默认：stdio
- `MCP_LOG_LEVEL`: MCP 日志级别（DEBUG、INFO、WARNING、ERROR）

## 部署步骤

### 1. 使用 Docker Compose 部署

#### Direct Mode

1. 编辑 `deployment/docker-compose.1panel.yml`
2. 确保 cognee-mcp 服务包含所有必需的环境变量（特别是 `LLM_API_KEY`）
3. 启动服务：
   ```bash
   docker-compose -f deployment/docker-compose.1panel.yml --profile mcp up -d
   ```

#### API Mode

1. 编辑 `deployment/docker-compose.1panel.yml`
2. 在 cognee-mcp 服务中：
   - 设置 `API_URL=http://cognee:8000`
   - 移除 LLM、数据库等环境变量（或注释掉）
3. 启动服务：
   ```bash
   docker-compose -f deployment/docker-compose.1panel.yml --profile mcp up -d
   ```

### 2. 使用 Docker 直接运行

#### Direct Mode

```bash
docker run \
  -e TRANSPORT_MODE=sse \
  -e LLM_API_KEY=your-api-key \
  -e DB_PROVIDER=postgres \
  -e DB_HOST=postgres \
  -e DB_PORT=5432 \
  -e DB_NAME=cognee_db \
  -e DB_USERNAME=cognee_user \
  -e DB_PASSWORD=cognee_password \
  --env-file ./.env \
  -p 8001:8000 \
  --rm -it cognee-mcp:latest
```

#### API Mode

```bash
docker run \
  -e TRANSPORT_MODE=sse \
  -e API_URL=http://cognee:8000 \
  -e API_TOKEN=your-api-token \
  -p 8001:8000 \
  --rm -it cognee-mcp:latest
```

## 验证部署

### 检查服务状态

```bash
# 检查容器是否运行
docker ps | grep cognee-mcp

# 检查日志
docker logs cognee-mcp

# 检查健康状态
curl http://localhost:8001/health
```

### 测试 MCP 连接

根据 README.md 中的说明配置 MCP 客户端：

**SSE Transport（推荐）**
```bash
claude mcp add cognee-sse -t sse http://localhost:8001/sse
```

**HTTP Transport**
```bash
claude mcp add cognee-http -t http http://localhost:8001/mcp
```

## 常见问题

### Q: 为什么 MCP 环境变量里没有 LLM_API_KEY？

**A:** 这取决于运行模式：

1. **Direct Mode**: 需要 `LLM_API_KEY` 和所有其他 cognee 环境变量，因为 MCP 服务器直接使用 cognee 库。

2. **API Mode**: 不需要 `LLM_API_KEY`，只需要 `API_URL`，因为 LLM 调用由 Cognee API 服务器处理。

### Q: cognee 下的环境变量都要放到 cognee-mcp 下吗？

**A:** 取决于运行模式：

- **Direct Mode**: 是的，需要所有环境变量（LLM、数据库、向量数据库、图数据库等）
- **API Mode**: 不需要，只需要 `API_URL` 和可选的 `API_TOKEN`

### Q: 如何选择运行模式？

**A:** 
- 如果已有 Cognee API 服务器在运行，使用 **API Mode**（更简单）
- 如果需要独立部署或使用完整功能（codify、prune 等），使用 **Direct Mode**

### Q: 两种模式可以同时使用吗？

**A:** 可以，但通常只需要一种。如果使用 API Mode，确保 Cognee API 服务器已正确配置所有环境变量。

## 参考文档

- [Cognee MCP README](../../project/cognee/cognee-mcp/README.md)
- [Cognee 部署指南](./README.md)
- [MCP 协议文档](https://modelcontextprotocol.io/)

