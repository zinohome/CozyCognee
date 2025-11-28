# 本地开发配置指南

本文档说明如何在本地启动 Cognee 服务并连接到远程服务器上的依赖服务。

## 场景说明

- **远程服务器**: 192.168.66.11
- **远程服务**: PostgreSQL, Redis, Qdrant, MinIO, Neo4j, RedisInsight
- **本地服务**: cognee, cognee-frontend, cognee-mcp

## 第一步：配置和启动 Cognee 后端

### 1. 准备项目环境

```bash
# 确保项目已初始化
cd /Users/zhangjun/CursorProjects/CozyCognee

# 如果 project/cognee 目录不存在，先初始化
./scripts/init-project.sh
```

### 2. 创建本地开发环境变量文件

在 `project/cognee` 目录下创建 `.env` 文件：

```bash
cd project/cognee
cp ../../deployment/env.example .env
```

### 3. 配置环境变量

编辑 `project/cognee/.env` 文件，配置连接到远程服务：

```bash
# ==================== 基础配置 ====================
DEBUG=true                    # 开发模式启用调试
ENVIRONMENT=local
LOG_LEVEL=DEBUG               # 开发时使用 DEBUG 级别
HOST=0.0.0.0
HTTP_PORT=8000

# ==================== LLM 配置 ====================
# 必需：配置您的LLM API密钥
LLM_API_KEY=your-llm-api-key-here
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini

# ==================== 数据库配置 ====================
# 连接到远程 PostgreSQL (192.168.66.11)
DB_PROVIDER=postgres
DB_HOST=192.168.66.11         # 远程服务器 IP
DB_PORT=5432
DB_NAME=cognee_db
DB_USERNAME=cognee_user
DB_PASSWORD=cognee_password

# 或者使用 DATABASE_URL 格式
DATABASE_URL=postgresql://cognee_user:cognee_password@192.168.66.11:5432/cognee_db

# ==================== Redis 配置 ====================
# 连接到远程 Redis (192.168.66.11)
REDIS_URL=redis://:cognee_redis_password@192.168.66.11:6379/0

# ==================== 向量数据库配置 ====================
# 向量数据库配置（使用 pgvector，向量数据存储在 PostgreSQL 中）
VECTOR_DB_PROVIDER=pgvector
# 注意: pgvector 使用与 PostgreSQL 相同的连接配置
# 无需配置 VECTOR_DB_URL 和 VECTOR_DB_KEY
# pgvector 是 PostgreSQL 的扩展，已包含在 postgres extra 依赖中

# ==================== 图数据库配置 ====================
# 连接到远程 Neo4j (192.168.66.11)
GRAPH_DATABASE_PROVIDER=neo4j
NEO4J_URL=bolt://192.168.66.11:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=pleaseletmein

# ==================== 对象存储配置 ====================
# 连接到远程 MinIO (192.168.66.11)
S3_ENDPOINT=http://192.168.66.11:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
S3_BUCKET_NAME=cognee-storage
S3_USE_SSL=false

# ==================== 其他配置 ====================
EXTRAS=api,postgres,neo4j
PYTHONUNBUFFERED=1
```

### 4. 安装依赖

```bash
cd project/cognee

# 使用 uv 安装依赖（推荐）
uv sync --extra api --extra postgres --extra neo4j

# 或使用 pip
pip install -e ".[api,postgres,neo4j]"
```

### 5. 运行数据库迁移

```bash
cd project/cognee

# 运行 Alembic 迁移
alembic upgrade head
```

### 6. 测试远程连接

在启动服务前，先测试是否能连接到远程服务：

```bash
# 测试 PostgreSQL 连接
psql -h 192.168.66.11 -U cognee_user -d cognee_db -c "SELECT 1;"

# 测试 Redis 连接
redis-cli -h 192.168.66.11 -p 6379 -a cognee_redis_password ping

# pgvector 是 PostgreSQL 的扩展，向量数据存储在 PostgreSQL 中
# 无需单独测试，验证 PostgreSQL 连接即可

# 测试 Neo4j 连接
curl http://192.168.66.11:7474
```

### 7. 启动 Cognee 服务

#### 方式一：直接运行（推荐用于开发调试）

```bash
cd project/cognee

# 启动开发服务器
uv run python -m cognee.api.client

# 或使用 gunicorn（生产模式）
uv run gunicorn -w 1 -k uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --log-level debug \
    --reload \
    cognee.api.client:app
```

#### 方式二：使用 Docker（如果需要容器化）

```bash
cd deployment

# 创建本地开发用的 docker-compose 文件
# 或者修改现有的 docker-compose.yml，将服务地址改为 192.168.66.11
```

### 8. 验证服务启动

```bash
# 检查服务是否运行
curl http://localhost:8000/health

# 查看 API 文档
open http://localhost:8000/docs
```

### 9. 查看日志

如果使用直接运行方式，日志会直接输出到终端。

如果使用 Docker，查看日志：
```bash
docker logs -f cognee
```

## 常见问题排查

### 连接失败

1. **检查网络连接**
   ```bash
   ping 192.168.66.11
   telnet 192.168.66.11 5432
   ```

2. **检查防火墙**
   确保远程服务器的端口已开放：
   - 5432 (PostgreSQL)
   - 6379 (Redis)
   - pgvector 使用 PostgreSQL 端口 5432
   - 7687 (Neo4j Bolt)
   - 9000 (MinIO)

3. **检查服务是否运行**
   在远程服务器上检查：
   ```bash
   ssh user@192.168.66.11
   docker ps
   ```

### 数据库迁移失败

```bash
# 检查数据库连接
psql -h 192.168.66.11 -U cognee_user -d cognee_db

# 手动运行迁移
cd project/cognee
alembic upgrade head --sql  # 查看 SQL
alembic upgrade head        # 执行迁移
```

### 环境变量未生效

```bash
# 确认 .env 文件位置
ls -la project/cognee/.env

# 检查环境变量
cd project/cognee
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('DB_HOST'))"
```

## 下一步

启动成功后，继续配置：
- [启动 cognee-frontend](./LOCAL_DEV_SETUP.md#第二步启动前端)
- [启动 cognee-mcp](./LOCAL_DEV_SETUP.md#第三步启动-mcp-服务)

