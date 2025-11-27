# 快速启动 Cognee 后端

## 前提条件

- 远程服务器 192.168.66.11 上的依赖服务已启动
- 本地已安装 Python 3.10+ 和 uv（或 pip）

## 快速步骤

### 1. 进入项目目录

```bash
cd /Users/zhangjun/CursorProjects/CozyCognee/project/cognee
```

### 2. 创建环境变量文件

```bash
cat > .env << 'EOF'
# 基础配置
DEBUG=true
ENVIRONMENT=local
LOG_LEVEL=DEBUG
HOST=0.0.0.0
HTTP_PORT=8000
PYTHONUNBUFFERED=1

# LLM 配置（必需）
LLM_API_KEY=your-llm-api-key-here
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini

# 数据库配置 - 连接到远程服务器
DB_PROVIDER=postgres
DB_HOST=192.168.66.11
DB_PORT=5432
DB_NAME=cognee_db
DB_USERNAME=cognee_user
DB_PASSWORD=cognee_password
DATABASE_URL=postgresql://cognee_user:cognee_password@192.168.66.11:5432/cognee_db

# Redis 配置
REDIS_URL=redis://:cognee_redis_password@192.168.66.11:6379/0

# 向量数据库配置
VECTOR_DB_PROVIDER=qdrant
QDRANT_URL=http://192.168.66.11:6333

# 图数据库配置
GRAPH_DATABASE_PROVIDER=neo4j
NEO4J_URL=bolt://192.168.66.11:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=pleaseletmein

# 对象存储配置
S3_ENDPOINT=http://192.168.66.11:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
S3_BUCKET_NAME=cognee-storage
S3_USE_SSL=false

# 其他配置
EXTRAS=api,postgres,neo4j
EOF
```

**重要**: 编辑 `.env` 文件，将 `LLM_API_KEY` 替换为您的实际 API 密钥！

### 3. 安装依赖

```bash
# 使用 uv（推荐）
uv sync --extra api --extra postgres --extra neo4j

# 或使用 pip
pip install -e ".[api,postgres,neo4j]"
```

### 4. 运行数据库迁移

```bash
alembic upgrade head
```

### 5. 启动服务

```bash
# 方式一：使用 Python 直接运行（推荐用于开发）
uv run python -m cognee.api.client

# 方式二：使用 gunicorn（更接近生产环境）
uv run gunicorn -w 1 -k uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --log-level debug \
    --reload \
    cognee.api.client:app
```

### 6. 验证

```bash
# 在另一个终端测试
curl http://localhost:8000/health

# 访问 API 文档
open http://localhost:8000/docs
```

## 测试远程连接

在启动前，可以测试远程服务连接：

```bash
# 测试 PostgreSQL
psql -h 192.168.66.11 -U cognee_user -d cognee_db -c "SELECT 1;"

# 测试 Redis
redis-cli -h 192.168.66.11 -p 6379 -a cognee_redis_password ping

# 测试 Qdrant
curl http://192.168.66.11:6333/health

# 测试 Neo4j
curl http://192.168.66.11:7474
```

## 常见问题

### 1. 连接被拒绝

- 检查远程服务器 IP 是否正确
- 检查防火墙是否开放端口
- 检查远程服务是否运行：`ssh user@192.168.66.11 "docker ps"`

### 2. 数据库迁移失败

```bash
# 检查数据库连接
psql -h 192.168.66.11 -U cognee_user -d cognee_db

# 查看迁移状态
alembic current

# 重新运行迁移
alembic upgrade head
```

### 3. 模块导入错误

```bash
# 确保在正确的目录
pwd  # 应该在 project/cognee

# 检查 Python 路径
python -c "import sys; print(sys.path)"

# 重新安装依赖
uv sync --reinstall
```

## 下一步

启动成功后，继续：
- 启动前端：`cd ../cognee-frontend && npm run dev`
- 启动 MCP：`cd ../cognee-mcp && uv run cognee-mcp --transport sse --host 0.0.0.0 --port 8001`

