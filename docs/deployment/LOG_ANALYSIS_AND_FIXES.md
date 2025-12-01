# 服务端日志分析与问题解决方案

## 📋 问题概述

根据服务端日志分析，发现了以下问题：

1. **🔴 严重错误**：pgvector 扩展未安装
2. **⚠️ 警告**：protego 和 playwright 导入失败
3. **⚠️ 非致命错误**：CloudApiKeyMissingError

---

## 🔴 问题 1：pgvector 扩展未安装（严重）

### 错误信息

```
Error: Conflict
{
  "error": "(sqlalchemy.dialects.postgresql.asyncpg.Error) <class 'asyncpg.exceptions.FeatureNotSupportedError'>: extension \"vector\" is not available\nDETAIL:  Could not open extension control file \"/usr/local/share/postgresql/extension/vector.control\": No such file or directory.\nHINT:  The extension must first be installed on the system where PostgreSQL is running.\n[SQL: CREATE EXTENSION IF NOT EXISTS vector;]"
}
```

### 问题原因

1. **配置分离**：项目配置了两个 PostgreSQL 实例：
   - `postgres`: 标准 PostgreSQL（`postgres:15-alpine`）- 用于关系数据
   - `pgvector`: 带 pgvector 扩展的 PostgreSQL（`pgvector/pgvector:0.8.1-pg17-trixie`）- 用于向量数据

2. **扩展创建位置错误**：Cognee 在 `DATABASE_URL` 指向的 `postgres` 数据库中尝试创建 `vector` 扩展，但该数据库使用的是 `postgres:15-alpine` 镜像，**没有** pgvector 扩展。

3. **配置不一致**：虽然配置了 `VECTOR_DB_URL` 指向 `pgvector` 服务，但 Cognee 可能在某些初始化操作中仍然在 `DATABASE_URL` 指向的数据库中创建扩展。

### 解决方案

#### 方案 1：将 postgres 服务改为带 pgvector 的镜像（推荐）

**优点**：
- 关系数据和向量数据可以在同一个数据库中
- 简化配置
- 减少资源占用

**修改步骤**：

1. 修改 `docker-compose.1panel.yml` 中的 `postgres` 服务：

```yaml
postgres:
  # 修改前
  image: postgres:15-alpine
  
  # 修改后
  image: pgvector/pgvector:0.8.1-pg17-trixie
```

2. 如果使用 pgvector，可以移除独立的 `pgvector` 服务，或者保留作为备用。

3. 更新环境变量配置（如果合并数据库）：

```yaml
# 如果合并到同一个数据库
- DATABASE_URL=postgresql://cognee_user:cognee_password@postgres:5432/cognee_db
- VECTOR_DB_PROVIDER=pgvector
# 注意：如果使用同一个数据库，可能不需要单独的 VECTOR_DB_URL
```

#### 方案 2：确保只在 pgvector 服务中创建扩展

如果必须保持两个独立的 PostgreSQL 实例，需要确保：

1. Cognee 只在 `VECTOR_DB_URL` 指向的数据库中创建 `vector` 扩展
2. 检查 Cognee 的初始化代码，确保不会在 `DATABASE_URL` 指向的数据库中创建扩展

#### 方案 3：手动在 postgres 数据库中安装 pgvector 扩展

如果必须使用 `postgres:15-alpine` 镜像，可以：

1. 创建一个自定义 Dockerfile，基于 `postgres:15-alpine` 并安装 pgvector
2. 或者使用初始化脚本在数据库启动后安装扩展

### 推荐操作步骤（方案 1）

1. **备份数据**（如果已有数据）：
   ```bash
   docker-compose -f deployment/docker-compose.1panel.yml exec postgres pg_dump -U cognee_user cognee_db > backup.sql
   ```

2. **停止服务**：
   ```bash
   docker-compose -f deployment/docker-compose.1panel.yml down
   ```

3. **修改 docker-compose.1panel.yml**：
   ```yaml
   postgres:
     image: pgvector/pgvector:0.8.1-pg17-trixie  # 改为带 pgvector 的镜像
     container_name: cognee_postgres
     restart: unless-stopped
     ports:
       - "5432:5432"
     environment:
       - POSTGRES_USER=cognee_user
       - POSTGRES_PASSWORD=cognee_password
       - POSTGRES_DB=cognee_db
       - PGDATA=/var/lib/postgresql/data/pgdata
     volumes:
       - /data/cognee/postgres:/var/lib/postgresql/data
   ```

4. **启动服务**：
   ```bash
   docker-compose -f deployment/docker-compose.1panel.yml up -d postgres
   ```

5. **等待数据库启动后，重启 cognee 服务**：
   ```bash
   docker-compose -f deployment/docker-compose.1panel.yml restart cognee
   ```

6. **验证扩展是否创建**：
   ```bash
   docker-compose -f deployment/docker-compose.1panel.yml exec postgres psql -U cognee_user -d cognee_db -c "\dx"
   ```

   应该能看到 `vector` 扩展。

---

## ⚠️ 问题 2：protego 和 playwright 导入失败

### 错误信息

```
2025-11-30T15:40:04.740374 [warning  ] Failed to import protego, make sure to install using pip install protego>=0.1
2025-11-30T15:40:04.740987 [warning  ] Failed to import playwright, make sure to install using pip install playwright>=1.9.0
```

### 问题原因

虽然我们在 Dockerfile 中添加了 `--extra scraping`，但可能：
1. 依赖没有正确安装
2. 或者 playwright 浏览器没有正确安装

### 解决方案

#### 检查 Dockerfile 中的依赖安装

确认 `deployment/docker/cognee/Dockerfile` 中：

1. **第一次 uv sync**（第37行）应该包含 `--extra scraping`：
   ```dockerfile
   RUN --mount=type=cache,target=/root/.cache/uv \
       uv sync --extra debug --extra api --extra postgres --extra neo4j --extra llama-index --extra ollama --extra mistral --extra groq --extra anthropic --extra scraping --frozen --no-install-project --no-dev --no-editable
   ```

2. **第二次 uv sync**（第57行）也应该包含 `--extra scraping`：
   ```dockerfile
   RUN --mount=type=cache,target=/root/.cache/uv \
       uv sync --extra debug --extra api --extra postgres --extra neo4j --extra llama-index --extra ollama --extra mistral --extra groq --extra anthropic --extra scraping --frozen --no-dev --no-editable
   ```

3. **Playwright 浏览器安装**（第63行）应该正确执行：
   ```dockerfile
   RUN PLAYWRIGHT_BROWSERS_PATH=/app/.cache/ms-playwright python3 -m playwright install --with-deps chromium 2>/dev/null || echo "Playwright browsers installation skipped (optional)"
   ```

#### 验证安装

1. **检查容器中是否安装了依赖**：
   ```bash
   docker-compose -f deployment/docker-compose.1panel.yml exec cognee python3 -c "import protego; print('protego OK')"
   docker-compose -f deployment/docker-compose.1panel.yml exec cognee python3 -c "import playwright; print('playwright OK')"
   ```

2. **如果未安装，重新构建镜像**：
   ```bash
   cd deployment/docker/cognee
   docker build -t cognee:0.4.1 -f Dockerfile ../..
   ```

#### 临时解决方案

如果不需要 web scraping 功能，这些警告可以忽略。它们不会影响核心功能。

---

## ⚠️ 问题 3：CloudApiKeyMissingError（非致命）

### 错误信息

```
2025-11-30T15:40:31.547876 [error    ] CloudApiKeyMissingError: Failed to connect to the cloud service. Please add your API key to local instance. (Status code: 400)
```

### 问题原因

这是 Cognee 尝试连接云服务时的错误，但这是**非致命错误**，不会影响本地运行。

### 解决方案

1. **如果不需要云服务功能**：可以忽略此错误
2. **如果需要云服务功能**：配置相应的 API key

---

## 📝 其他发现

### SyntaxWarning

```
/app/cognee/modules/visualization/cognee_network_visualization.py:195: SyntaxWarning: invalid escape sequence '\s'
```

这是一个代码警告，不影响功能，但建议修复。

---

## 🎯 优先级修复建议

### 立即修复（阻塞功能）

1. **修复 pgvector 扩展问题**（方案 1：将 postgres 镜像改为带 pgvector 的版本）

### 可选修复（不影响核心功能）

2. 修复 protego/playwright 导入警告（如果需要 web scraping 功能）
3. 修复 SyntaxWarning（代码质量改进）
4. 配置云服务 API key（如果需要云服务功能）

---

## 🔧 快速修复脚本

创建一个修复脚本 `fix-pgvector.sh`：

```bash
#!/bin/bash

# 备份数据
echo "备份数据库..."
docker-compose -f deployment/docker-compose.1panel.yml exec postgres pg_dump -U cognee_user cognee_db > backup_$(date +%Y%m%d_%H%M%S).sql

# 停止服务
echo "停止服务..."
docker-compose -f deployment/docker-compose.1panel.yml down

# 修改 docker-compose.1panel.yml（需要手动编辑）
echo "请手动编辑 deployment/docker-compose.1panel.yml，将 postgres 服务的镜像改为："
echo "  image: pgvector/pgvector:0.8.1-pg17-trixie"
echo ""
read -p "按 Enter 继续..."

# 启动 postgres 服务
echo "启动 postgres 服务..."
docker-compose -f deployment/docker-compose.1panel.yml up -d postgres

# 等待数据库启动
echo "等待数据库启动..."
sleep 10

# 验证扩展
echo "验证 pgvector 扩展..."
docker-compose -f deployment/docker-compose.1panel.yml exec postgres psql -U cognee_user -d cognee_db -c "\dx"

# 重启 cognee 服务
echo "重启 cognee 服务..."
docker-compose -f deployment/docker-compose.1panel.yml restart cognee

echo "修复完成！"
```

---

## 📚 相关文档

- [pgvector 配置指南](../deployment/PGVECTOR_SETUP.md)
- [Dockerfile 对比分析](../deployment/DOCKERFILE_COMPARISON.md)
- [部署文档](../deployment/README.md)

