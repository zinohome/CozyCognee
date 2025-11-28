# PostgreSQL 和 pgvector 服务分离配置

## 概述

CozyCognee 配置了两个独立的 PostgreSQL 服务：
- **postgres**: 标准 PostgreSQL，用于关系数据
- **pgvector**: 带 pgvector 扩展的 PostgreSQL，用于向量数据

## 服务配置

### PostgreSQL 关系数据库服务

```yaml
postgres:
  image: postgres:15-alpine
  container_name: cognee_postgres
  ports:
    - "5432:5432"
  environment:
    - POSTGRES_USER=cognee_user
    - POSTGRES_PASSWORD=cognee_password
    - POSTGRES_DB=cognee_db
  volumes:
    - /data/cognee/postgres:/var/lib/postgresql/data
```

### pgvector 向量数据库服务

```yaml
pgvector:
  image: pgvector/pgvector:0.8.1-pg17-trixie
  container_name: cognee_pgvector
  ports:
    - "5433:5432"
  environment:
    - POSTGRES_USER=cognee_vector_user
    - POSTGRES_PASSWORD=cognee_vector_password
    - POSTGRES_DB=cognee_vector_db
  volumes:
    - /data/cognee/pgvector:/var/lib/postgresql/data
```

## 代码限制说明

**重要**: Cognee 的 pgvector 实现会从关系数据库配置获取连接信息。这意味着：

1. **如果关系数据库是 PostgreSQL**：pgvector 会使用同一个连接（连接到 postgres 服务）
2. **如果关系数据库不是 PostgreSQL**（如 SQLite）：pgvector 会创建新连接

## 配置方案

### 方案 1: 使用不同的数据库名（推荐）

在同一 PostgreSQL 实例中使用不同的数据库名：

```env
# 关系数据库配置
DB_PROVIDER=postgres
DB_HOST=postgres
DB_NAME=cognee_db

# pgvector 配置
VECTOR_DB_PROVIDER=pgvector
# pgvector 会使用关系数据库配置，但可以通过代码使用不同的数据库名
```

**优点**: 简单，无需修改代码  
**缺点**: 两个数据库在同一 PostgreSQL 实例中

### 方案 2: 修改代码支持独立配置

修改 `project/cognee/cognee/infrastructure/databases/vector/create_vector_engine.py`，添加独立的 pgvector 配置支持：

```python
# 添加环境变量支持
VECTOR_DB_HOST=pgvector
VECTOR_DB_PORT=5432
VECTOR_DB_NAME=cognee_vector_db
VECTOR_DB_USERNAME=cognee_vector_user
VECTOR_DB_PASSWORD=cognee_vector_password
```

**优点**: 真正的服务分离  
**缺点**: 需要修改源码

### 方案 3: 关系数据库使用 SQLite

让关系数据库使用 SQLite，pgvector 使用独立的 PostgreSQL：

```env
# 关系数据库使用 SQLite
DB_PROVIDER=sqlite

# pgvector 使用独立的 PostgreSQL 服务
VECTOR_DB_PROVIDER=pgvector
# pgvector 会创建新连接，可以配置连接到 pgvector 服务
```

**优点**: 实现服务分离  
**缺点**: 关系数据不能使用 PostgreSQL

## 当前配置

当前配置使用两个独立的服务：

- **postgres 服务**: 端口 5432，用于关系数据
- **pgvector 服务**: 端口 5433，用于向量数据

但由于代码限制，pgvector 会连接到 postgres 服务（关系数据库配置）。

## 数据目录

```
/data/cognee/
├── postgres/    # PostgreSQL 关系数据库数据
└── pgvector/    # pgvector 向量数据库数据
```

## 验证服务

```bash
# 检查 postgres 服务
docker ps | grep cognee_postgres
psql -h localhost -p 5432 -U cognee_user -d cognee_db

# 检查 pgvector 服务
docker ps | grep cognee_pgvector
psql -h localhost -p 5433 -U cognee_vector_user -d cognee_vector_db

# 检查 pgvector 扩展
psql -h localhost -p 5433 -U cognee_vector_user -d cognee_vector_db -c "SELECT * FROM pg_extension WHERE extname = 'vector';"
```

## 推荐配置

对于生产环境，推荐使用**方案 1**（同一实例不同数据库），因为：
- 简化部署和管理
- 统一备份和恢复
- 减少资源消耗
- 代码无需修改

如果需要真正的服务分离，建议使用**方案 2**（修改代码支持独立配置）。

