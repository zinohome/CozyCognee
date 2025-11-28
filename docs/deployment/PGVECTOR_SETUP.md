# pgvector 向量数据库配置指南

本文档说明如何在 CozyCognee 中配置和使用 pgvector 作为向量数据库。

## 概述

pgvector 是 PostgreSQL 的扩展，为 PostgreSQL 添加了向量相似度搜索功能。使用 pgvector 可以将向量数据直接存储在 PostgreSQL 数据库中，无需额外的向量数据库服务。

**优势**:
- ✅ 无需额外的向量数据库服务
- ✅ 向量数据和关系数据在同一数据库中
- ✅ 支持事务和 ACID 特性
- ✅ 简化部署架构
- ✅ 统一的备份和恢复策略

## PostgreSQL 镜像

CozyCognee 使用包含 pgvector 扩展的 PostgreSQL 镜像：

```yaml
postgres:
  image: pgvector/pgvector:0.8.1-pg17-trixie
```

此镜像已预装 pgvector 扩展，无需额外配置。

## 配置

### 环境变量配置

在 `.env` 文件中配置：

```bash
# 向量数据库配置
VECTOR_DB_PROVIDER=pgvector

# PostgreSQL 配置（pgvector 使用相同的连接）
DB_PROVIDER=postgres
DB_HOST=postgres  # 或远程地址
DB_PORT=5432
DB_NAME=cognee_db
DB_USERNAME=cognee_user
DB_PASSWORD=cognee_password
DATABASE_URL=postgresql://cognee_user:cognee_password@postgres:5432/cognee_db
```

**重要**: 使用 pgvector 时，无需配置 `VECTOR_DB_URL` 和 `VECTOR_DB_KEY`，向量数据存储在 PostgreSQL 中。

### Docker Compose 配置

在 `docker-compose.1panel.yml` 中，PostgreSQL 服务已配置为使用 pgvector 镜像：

```yaml
postgres:
  image: pgvector/pgvector:0.8.1-pg17-trixie
  container_name: cognee_postgres
  environment:
    - POSTGRES_USER=cognee_user
    - POSTGRES_PASSWORD=cognee_password
    - POSTGRES_DB=cognee_db
  volumes:
    - /data/cognee/postgres:/var/lib/postgresql/data
```

## 安装依赖

### Docker 镜像

Docker 镜像已包含 pgvector 支持（通过 `postgres` extra 依赖），无需额外安装。

### 本地开发

```bash
cd project/cognee

# 安装包含 pgvector 的依赖
uv sync --extra api --extra postgres --extra neo4j

# 或使用 pip
pip install -e ".[api,postgres,neo4j]"
```

`postgres` extra 依赖包含：
- `psycopg2` - PostgreSQL 适配器
- `pgvector` - pgvector Python 包
- `asyncpg` - 异步 PostgreSQL 驱动

## 验证配置

### 检查 PostgreSQL 和 pgvector

```bash
# 连接到 PostgreSQL
psql -h localhost -U cognee_user -d cognee_db

# 检查 pgvector 扩展是否已安装
SELECT * FROM pg_extension WHERE extname = 'vector';

# 如果未安装，手动安装扩展
CREATE EXTENSION IF NOT EXISTS vector;
```

### 检查 Cognee 配置

启动 Cognee 服务时，查看日志确认使用 pgvector：

```
Vector database provider: pgvector
PostgreSQL connection: OK
```

## 数据存储

使用 pgvector 时，向量数据存储在 PostgreSQL 数据库中：

- **表结构**: Cognee 会自动创建包含向量列的表
- **存储位置**: 与关系数据在同一数据库中
- **备份**: 包含在 PostgreSQL 备份中

## 性能优化

### 索引优化

pgvector 支持多种索引类型：

- **HNSW**: 适合高维向量，查询速度快
- **IVFFlat**: 适合低维向量，索引构建快

Cognee 会自动创建适当的索引。

### 连接池配置

建议配置 PostgreSQL 连接池以提高性能：

```env
# 在 .env 中配置（如果支持）
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10
```

## 迁移现有数据

### 从其他向量数据库迁移

如果从其他向量数据库（如 Qdrant、ChromaDB）迁移到 pgvector：

1. **备份现有数据**
   ```bash
   # 导出现有数据
   cognee.export_data()
   ```

2. **清理系统**
   ```python
   import cognee
   await cognee.prune.prune_system()
   ```

3. **重新添加和处理数据**
   ```python
   await cognee.add(data, dataset_id="my_dataset")
   await cognee.cognify(datasets=["my_dataset"])
   ```

## 故障排查

### pgvector 扩展未安装

**错误**: `extension "vector" does not exist`

**解决**:
```sql
-- 连接到数据库
psql -h localhost -U cognee_user -d cognee_db

-- 安装扩展
CREATE EXTENSION IF NOT EXISTS vector;
```

### 连接失败

**错误**: 无法连接到 PostgreSQL

**解决**:
1. 检查 PostgreSQL 服务是否运行：`docker ps | grep postgres`
2. 检查端口是否正确：`netstat -tulpn | grep 5432`
3. 验证连接信息：`psql -h localhost -U cognee_user -d cognee_db`
4. 检查防火墙设置

### 向量维度不匹配

**错误**: Embedding 维度错误

**解决**:
1. 检查 `EMBEDDING_DIMENSIONS` 环境变量
2. 确认与嵌入模型匹配
3. 如需要，清理并重建表：
   ```python
   await cognee.prune.prune_system()
   ```

### 性能问题

**问题**: 向量搜索速度慢

**解决**:
1. 检查索引是否创建：`\d+ table_name` 在 psql 中
2. 考虑使用 HNSW 索引（适合高维向量）
3. 优化 PostgreSQL 配置（shared_buffers, work_mem 等）
4. 增加连接池大小

## 相关资源

- [pgvector 官方文档](https://github.com/pgvector/pgvector)
- [PostgreSQL 文档](https://www.postgresql.org/docs/)
- [Cognee 向量存储配置](https://docs.cognee.ai/setup-configuration/vector-stores)

## 与 Qdrant 的对比

| 特性 | pgvector | Qdrant |
|------|----------|--------|
| 部署复杂度 | 低（使用现有 PostgreSQL） | 中（需要单独服务） |
| 数据一致性 | 高（ACID 事务） | 中 |
| 查询性能 | 高 | 很高 |
| 扩展性 | 中 | 高 |
| 运维成本 | 低 | 中 |
| 适用场景 | 中小规模，需要事务 | 大规模，高性能搜索 |

对于大多数应用场景，pgvector 提供了更好的集成和简化部署的优势。

