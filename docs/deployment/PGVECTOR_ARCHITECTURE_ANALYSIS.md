# pgvector 架构分析与问题根源

## 🔍 问题根源分析

### 核心发现

**Cognee 的设计逻辑**：当使用 `pgvector` 作为向量数据库时，**向量数据存储在关系数据库中**，而不是独立的向量数据库。

### 代码证据

#### 1. 向量引擎创建逻辑

在 `project/cognee/cognee/infrastructure/databases/vector/create_vector_engine.py` 的第 50-66 行：

```python
if vector_db_provider.lower() == "pgvector":
    from cognee.infrastructure.databases.relational import get_relational_config

    # Get configuration for postgres database
    relational_config = get_relational_config()  # ⚠️ 使用关系数据库配置！
    db_username = relational_config.db_username
    db_password = relational_config.db_password
    db_host = relational_config.db_host
    db_port = relational_config.db_port
    db_name = relational_config.db_name

    if not (db_host and db_port and db_name and db_username and db_password):
        raise EnvironmentError("Missing requred pgvector credentials!")

    connection_string: str = (
        f"postgresql+asyncpg://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}"
    )  # ⚠️ 使用关系数据库的连接字符串！

    return PGVectorAdapter(
        connection_string,
        vector_db_key,
        embedding_engine,
    )
```

**关键问题**：
- ❌ **完全忽略** `VECTOR_DB_URL` 环境变量
- ✅ **使用** `get_relational_config()` 获取关系数据库配置
- ✅ **使用** `DATABASE_URL` 指向的数据库连接

#### 2. 扩展创建逻辑

在 `project/cognee/cognee/infrastructure/databases/vector/pgvector/create_db_and_tables.py` 的第 10-12 行：

```python
async def create_db_and_tables():
    vector_config = get_vectordb_context_config()
    vector_engine = get_vector_engine()

    if vector_config["vector_db_provider"] == "pgvector":
        async with vector_engine.engine.begin() as connection:
            await connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
            # ⚠️ 在关系数据库连接上创建扩展！
```

**关键问题**：
- 扩展创建在 `vector_engine` 指向的数据库上
- 而 `vector_engine` 使用的是关系数据库的连接（见上面第1点）
- 所以扩展会在 `DATABASE_URL` 指向的数据库中创建

#### 3. API 调用流程

当调用 `/api/v1/add` 时：

1. `get_add_router.py` → `add()` 函数
2. `add.py` → `setup()` 函数（第188行）
3. `setup.py` → `create_pgvector_db_and_tables()`（第17行）
4. `create_db_and_tables.py` → 在关系数据库上创建 `vector` 扩展（第12行）

## 📊 架构设计分析

### Cognee 的 pgvector 设计理念

Cognee 的设计是：**pgvector 是 PostgreSQL 的扩展，向量数据应该和关系数据存储在同一个数据库中**。

这种设计的**优点**：
- ✅ 简化架构：不需要独立的向量数据库服务
- ✅ 数据一致性：向量数据和关系数据在同一事务中
- ✅ 简化部署：只需要一个 PostgreSQL 实例

这种设计的**缺点**：
- ❌ 无法将向量数据和关系数据分离到不同的数据库
- ❌ 即使配置了 `VECTOR_DB_URL`，也会被忽略
- ❌ 如果关系数据库没有 pgvector 扩展，会报错

### 当前配置的问题

在 `docker-compose.1panel.yml` 中：

```yaml
# 关系数据库（没有 pgvector 扩展）
postgres:
  image: postgres:15-alpine  # ❌ 没有 pgvector

# 向量数据库（有 pgvector 扩展，但不会被使用）
pgvector:
  image: pgvector/pgvector:0.8.1-pg17-trixie  # ✅ 有 pgvector，但被忽略

# Cognee 配置
cognee:
  environment:
    - DATABASE_URL=postgresql://...@postgres:5432/cognee_db  # 关系数据库
    - VECTOR_DB_PROVIDER=pgvector
    - VECTOR_DB_URL=postgresql://...@pgvector:5432/cognee_vector_db  # ⚠️ 被忽略！
```

**问题**：
- `VECTOR_DB_URL` 配置了独立的 `pgvector` 服务
- 但 Cognee 代码会忽略它，使用 `DATABASE_URL` 指向的 `postgres` 服务
- `postgres` 服务没有 pgvector 扩展，导致错误

## ✅ 解决方案

### 方案 1：将 postgres 服务改为带 pgvector 的镜像（推荐，已修复）

**原理**：既然 Cognee 会在关系数据库中创建 vector 扩展，那就让关系数据库支持 pgvector。

**修改**：
```yaml
postgres:
  image: pgvector/pgvector:pg15  # ✅ 改为带 pgvector 的镜像
```

**优点**：
- ✅ 符合 Cognee 的设计理念
- ✅ 简化架构（可以移除独立的 pgvector 服务）
- ✅ 数据一致性更好

**缺点**：
- ❌ 无法将向量数据和关系数据分离（但 Cognee 设计就是这样的）

### 方案 2：修改 Cognee 源代码（不推荐）

如果要让 Cognee 使用独立的 `pgvector` 服务，需要修改源代码：

1. 修改 `create_vector_engine.py`，让它在 `VECTOR_DB_URL` 存在时使用它
2. 修改 `create_db_and_tables.py`，确保在正确的数据库上创建扩展

**缺点**：
- ❌ 违反项目规则（不能修改官方源代码）
- ❌ 需要维护补丁
- ❌ 升级时可能冲突

### 方案 3：使用同一个数据库（推荐）

既然 Cognee 的设计是向量数据和关系数据在同一数据库中，那就：

1. 只使用一个 PostgreSQL 服务（带 pgvector 扩展）
2. 移除独立的 `pgvector` 服务
3. 配置 `DATABASE_URL` 指向这个服务
4. 不需要配置 `VECTOR_DB_URL`（会被忽略）

**配置示例**：
```yaml
# 只保留一个 PostgreSQL 服务
postgres:
  image: pgvector/pgvector:pg15
  container_name: cognee_postgres
  environment:
    - POSTGRES_USER=cognee_user
    - POSTGRES_PASSWORD=cognee_password
    - POSTGRES_DB=cognee_db

# 移除 pgvector 服务（不再需要）

# Cognee 配置
cognee:
  environment:
    - DATABASE_URL=postgresql://cognee_user:cognee_password@postgres:5432/cognee_db
    - VECTOR_DB_PROVIDER=pgvector
    # 不需要 VECTOR_DB_URL（会被忽略）
```

## 🔧 代码流程总结

### 当前流程（导致错误）

```
/api/v1/add
  ↓
add() → setup()
  ↓
create_pgvector_db_and_tables()
  ↓
get_vector_engine()
  ↓
create_vector_engine(vector_db_provider="pgvector")
  ↓
get_relational_config()  # ⚠️ 使用关系数据库配置
  ↓
使用 DATABASE_URL 连接 postgres 服务
  ↓
CREATE EXTENSION IF NOT EXISTS vector;  # ❌ postgres:15-alpine 没有扩展
  ↓
错误：extension "vector" is not available
```

### 修复后的流程

```
/api/v1/add
  ↓
add() → setup()
  ↓
create_pgvector_db_and_tables()
  ↓
get_vector_engine()
  ↓
create_vector_engine(vector_db_provider="pgvector")
  ↓
get_relational_config()  # 使用关系数据库配置
  ↓
使用 DATABASE_URL 连接 postgres 服务（现在是 pgvector/pgvector:pg15）
  ↓
CREATE EXTENSION IF NOT EXISTS vector;  # ✅ 成功创建扩展
  ↓
正常处理数据
```

## 📝 总结

1. **Cognee 的设计**：pgvector 向量数据存储在关系数据库中，不是独立的数据库
2. **代码行为**：当 `VECTOR_DB_PROVIDER=pgvector` 时，会忽略 `VECTOR_DB_URL`，使用 `DATABASE_URL`
3. **问题根源**：`DATABASE_URL` 指向的数据库没有 pgvector 扩展
4. **解决方案**：将 `postgres` 服务改为带 pgvector 的镜像（已修复）

## 🎯 建议

1. **立即修复**：使用 `pgvector/pgvector:pg15` 作为 `postgres` 服务镜像（已完成）
2. **架构优化**：考虑移除独立的 `pgvector` 服务，只使用一个 PostgreSQL 服务
3. **文档更新**：在部署文档中说明 pgvector 的设计理念

## 📚 相关文件

- `project/cognee/cognee/infrastructure/databases/vector/create_vector_engine.py` (第 50-66 行)
- `project/cognee/cognee/infrastructure/databases/vector/pgvector/create_db_and_tables.py` (第 10-12 行)
- `project/cognee/cognee/api/v1/add/add.py` (第 188 行)
- `deployment/docker-compose.1panel.yml` (已修复)

