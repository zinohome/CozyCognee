# Dockerfile 对比分析

本文档对比了 CozyCognee 项目中的三个 Dockerfile 与官方源码中的 Dockerfile 的差异。

## 📋 目录

- [后端 (cognee) Dockerfile 对比](#后端-cognee-dockerfile-对比)
- [前端 (cognee-frontend) Dockerfile 对比](#前端-cognee-frontend-dockerfile-对比)
- [MCP (cognee-mcp) Dockerfile 对比](#mcp-cognee-mcp-dockerfile-对比)
- [entrypoint.sh 对比](#entrypointsh-对比)
- [潜在问题分析](#潜在问题分析)

---

## 后端 (cognee) Dockerfile 对比

### 文件位置
- **我们的**: `deployment/docker/cognee/Dockerfile`
- **官方的**: `project/cognee/Dockerfile`

### 主要差异

#### 1. 构建上下文路径
- **我们的**: 使用 `project/cognee/...` 路径（构建上下文是项目根目录）
- **官方的**: 使用相对路径（构建上下文是 `project/cognee/` 目录）

```diff
# 我们的
COPY project/cognee/README.md project/cognee/pyproject.toml project/cognee/uv.lock project/cognee/entrypoint.sh ./

# 官方的
COPY README.md pyproject.toml uv.lock entrypoint.sh ./
```

#### 2. 系统依赖
- **我们的**: 添加了 `cmake`（第25行）
- **官方的**: 没有 `cmake`

```diff
# 我们的
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    git \
    curl \
+   cmake \
    clang \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 官方的
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    git \
    curl \
    clang \
    build-essential \
    && rm -rf /var/lib/apt/lists/*
```

#### 3. 依赖安装 - 添加了 `scraping` extra
- **我们的**: 添加了 `--extra scraping` 参数（第37行和第57行）
- **官方的**: 没有 `scraping` extra

```diff
# 我们的
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --extra debug --extra api --extra postgres --extra neo4j --extra llama-index --extra ollama --extra mistral --extra groq --extra anthropic --extra scraping --frozen --no-install-project --no-dev --no-editable

# 官方的
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --extra debug --extra api --extra postgres --extra neo4j --extra llama-index --extra ollama --extra mistral --extra groq --extra anthropic --frozen --no-install-project --no-dev --no-editable
```

#### 4. CORS 补丁
- **我们的**: 添加了 CORS 补丁（第53-54行）
- **官方的**: 没有补丁

```diff
# 我们的
# Apply CozyCognee patches (CORS configuration)
# Copy patch script and apply it to client.py
COPY deployment/docker/cognee/patch_cors.py /tmp/patch_cors.py
RUN python3 /tmp/patch_cors.py /app/cognee/api/client.py && rm /tmp/patch_cors.py

# 官方的
# 没有补丁
```

#### 5. Playwright 浏览器安装
- **我们的**: 添加了 playwright 浏览器安装（第63行）
- **官方的**: 没有安装

```diff
# 我们的
# Install playwright browsers (消除警告)
RUN PLAYWRIGHT_BROWSERS_PATH=/app/.cache/ms-playwright python3 -m playwright install --with-deps chromium 2>/dev/null || echo "Playwright browsers installation skipped (optional)"

# 官方的
# 没有安装
```

#### 6. 最终阶段系统依赖
- **我们的**: 添加了 playwright 运行时依赖（第73-88行）
- **官方的**: 只安装了 `libpq5`

```diff
# 我们的
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    wget \
    # playwright 浏览器运行时依赖
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

# 官方的
RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*
```

#### 7. Playwright 环境变量
- **我们的**: 设置了 `PLAYWRIGHT_BROWSERS_PATH`（第96行）
- **官方的**: 没有设置

```diff
# 我们的
ENV PLAYWRIGHT_BROWSERS_PATH=/app/.cache/ms-playwright

# 官方的
# 没有设置
```

---

## 前端 (cognee-frontend) Dockerfile 对比

### 文件位置
- **我们的**: `deployment/docker/cognee-frontend/Dockerfile`
- **官方的**: `project/cognee/cognee-frontend/Dockerfile`

### 主要差异

#### 1. 构建上下文路径
- **我们的**: 使用 `project/cognee/cognee-frontend/...` 路径
- **官方的**: 使用相对路径

```diff
# 我们的
COPY project/cognee/cognee-frontend/package.json project/cognee/cognee-frontend/package-lock.json ./

# 官方的
COPY package.json package-lock.json ./
```

#### 2. next.config.mjs 处理
- **我们的**: 使用补丁版本的 `next.config.mjs`（第19行）
- **官方的**: 直接复制原始文件

```diff
# 我们的
# Apply CozyCognee patches: 使用补丁版本的 next.config.mjs 来禁用 devIndicators
COPY deployment/docker/cognee-frontend/patches/next.config.mjs ./next.config.mjs

# 官方的
COPY next.config.mjs .
```

#### 3. 环境变量配置
- **我们的**: 添加了构建参数和环境变量（第25-36行）
- **官方的**: 没有环境变量配置

```diff
# 我们的
# Build arguments for environment variables (NEXT_PUBLIC_*)
ARG NEXT_PUBLIC_BACKEND_API_URL=http://cognee:8000/api
ARG NEXT_PUBLIC_CLOUD_API_URL=http://cognee-mcp:8000
ARG NEXT_PUBLIC_MCP_API_URL=http://cognee-mcp:8000
ARG NEXT_PUBLIC_COGWIT_API_KEY=
ARG NEXT_PUBLIC_IS_CLOUD_ENVIRONMENT=false

# Set environment variables (这些会在运行时可用)
ENV NEXT_PUBLIC_BACKEND_API_URL=${NEXT_PUBLIC_BACKEND_API_URL}
ENV NEXT_PUBLIC_CLOUD_API_URL=${NEXT_PUBLIC_CLOUD_API_URL}
ENV NEXT_PUBLIC_MCP_API_URL=${NEXT_PUBLIC_MCP_API_URL}
ENV NEXT_PUBLIC_COGWIT_API_KEY=${NEXT_PUBLIC_COGWIT_API_KEY}
ENV NEXT_PUBLIC_IS_CLOUD_ENVIRONMENT=${NEXT_PUBLIC_IS_CLOUD_ENVIRONMENT}

# 官方的
# 没有环境变量配置
```

#### 4. 开发指示器禁用
- **我们的**: 添加了 `NEXT_DISABLE_DEV_INDICATORS` 环境变量（第44行）
- **官方的**: 没有设置

```diff
# 我们的
ENV NEXT_DISABLE_DEV_INDICATORS=true

# 官方的
# 没有设置
```

---

## MCP (cognee-mcp) Dockerfile 对比

### 文件位置
- **我们的**: `deployment/docker/cognee-mcp/Dockerfile`
- **官方的**: `project/cognee/cognee-mcp/Dockerfile`

### 主要差异

#### 1. 构建上下文路径
- **我们的**: 使用 `project/cognee/...` 路径
- **官方的**: 使用相对路径

#### 2. 系统依赖
- **我们的**: 没有 `cmake`（第25行）
- **官方的**: 也没有 `cmake`（一致）

#### 3. 依赖安装策略（重要差异）
- **我们的**: 使用本地 cognee 源代码，移除 `docs` extra，添加 `scraping` extra
- **官方的**: 从 PyPI 安装 cognee 包（包含 `docs` extra）

```diff
# 我们的
# 优化：使用源代码而不是 PyPI 包，大幅减小镜像体积（从 8.5GB 减少到 ~1.5-2GB）
# 1. 将 cognee 源代码放在子目录中
COPY project/cognee/README.md /app/cognee-source/README.md
COPY project/cognee/pyproject.toml /app/cognee-source/pyproject.toml
COPY project/cognee/cognee /app/cognee-source/cognee
COPY project/cognee/cognee/distributed /app/cognee-source/distributed

# 2. 修改 pyproject.toml：使用本地 cognee 源代码，移除 docs extra，添加 scraping extra
RUN sed -i 's|"cognee\[postgres,docs,neo4j\]==0.3.7"|"cognee[postgres,neo4j,scraping] @ file:///app/cognee-source"|' pyproject.toml

# 3. 安装依赖（不使用 --frozen，因为 lock 文件不匹配）
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-install-project --no-dev --no-editable

# 官方的
# 从 PyPI 安装 cognee 包（包含 docs extra）
COPY ./cognee-mcp/pyproject.toml ./cognee-mcp/uv.lock ./cognee-mcp/entrypoint.sh ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev --no-editable
```

#### 4. Alembic 配置
- **我们的**: 复制了 Alembic 配置（第63-64行）
- **官方的**: 也复制了 Alembic 配置（第37-38行），但路径不同

```diff
# 我们的
COPY project/cognee/alembic.ini /app/alembic.ini
COPY project/cognee/alembic/ /app/alembic

# 官方的
COPY alembic.ini /app/alembic.ini
COPY alembic/ /app/alembic
```

#### 5. CORS 补丁
- **我们的**: 添加了 CORS 补丁（第71-72行）
- **官方的**: 没有补丁

#### 6. Playwright 浏览器安装
- **我们的**: 添加了 playwright 浏览器安装（第80行）
- **官方的**: 没有安装

#### 7. 最终阶段系统依赖
- **我们的**: 添加了 playwright 运行时依赖（第88-103行）
- **官方的**: 只安装了 `libpq5`

#### 8. 最终阶段复制
- **我们的**: 复制了 `/usr/local`（第108行）
- **官方的**: 也复制了 `/usr/local`（第55行），但顺序不同

```diff
# 我们的
COPY --from=uv /usr/local /usr/local
COPY --from=uv /app /app

# 官方的
COPY --from=uv /usr/local /usr/local
COPY --from=uv /app /app
```

---

## entrypoint.sh 对比

### 文件位置
- **我们的**: `deployment/docker/cognee/entrypoint.sh`
- **官方的**: `project/cognee/entrypoint.sh`

### 主要差异

#### 1. 生产环境 Gunicorn 配置
- **我们的**: 添加了更详细的配置（第54-67行）
  - `--timeout 300`
  - `--graceful-timeout 30`
  - `--max-requests 1000`
  - `--max-requests-jitter 100`
  - `--access-logfile -`
  - `--error-logfile -`
- **官方的**: 简单配置（第51行）
  - `--timeout 30000`
  - 没有 `--max-requests` 等参数

```diff
# 我们的
else
    # 生产环境：增加 worker 超时时间，添加 max_requests 防止内存泄漏
    gunicorn -w 1 -k uvicorn.workers.UvicornWorker \
        --timeout 300 \
        --graceful-timeout 30 \
        --max-requests 1000 \
        --max-requests-jitter 100 \
        --bind=0.0.0.0:$HTTP_PORT \
        --log-level error \
        --access-logfile - \
        --error-logfile - \
        cognee.api.client:app
fi

# 官方的
else
    gunicorn -w 1 -k uvicorn.workers.UvicornWorker -t 30000 --bind=0.0.0.0:$HTTP_PORT --log-level error cognee.api.client:app
fi
```

#### 2. pgvector 注释
- **我们的**: 添加了 pgvector 相关注释（第37-38行）
- **官方的**: 没有注释

---

## 潜在问题分析

### 🔴 可能导致后端运行问题的差异

#### 1. **依赖安装顺序问题**
我们的 Dockerfile 中，依赖安装分为两步：
1. 第一次：`--no-install-project`（第37行）
2. 第二次：安装项目（第57行）

但在这两步之间，我们：
- 复制了源代码（第48-49行）
- 应用了 CORS 补丁（第54行）

**潜在问题**: 如果补丁修改了依赖关系，可能会导致第二次 `uv sync` 时出现问题。

#### 2. **依赖安装命令格式**
第二次 `uv sync` 时（第57行），命令格式与第一次略有不同（缺少换行和缩进），但功能相同，都使用了 `--frozen` 标志。

**注意**: 虽然功能相同，但格式不一致可能导致维护困难。

#### 3. **Playwright 依赖可能不完整**
我们添加了 playwright 浏览器安装，但可能缺少某些运行时依赖。

#### 4. **构建上下文路径问题**
我们的 Dockerfile 使用 `project/cognee/...` 路径，这意味着构建上下文必须是项目根目录。如果构建上下文不正确，可能导致文件找不到。

### ✅ 建议的修复方案

#### 1. 确保第二次 `uv sync` 使用 `--frozen`
```dockerfile
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --extra debug --extra api --extra postgres --extra neo4j --extra llama-index --extra ollama --extra mistral --extra groq --extra anthropic --extra scraping --frozen --no-dev --no-editable
```

#### 2. 检查构建上下文
确保在构建时使用正确的构建上下文：
```bash
docker build -f deployment/docker/cognee/Dockerfile -t cognee:latest .
```

#### 3. 验证补丁是否正确应用
检查 CORS 补丁是否正确应用，以及是否影响了依赖关系。

#### 4. 检查日志
查看容器启动日志，确认具体的错误信息：
```bash
docker logs <container_name>
```

---

## 📝 总结

### 我们的 Dockerfile 相比官方版本的主要改进：
1. ✅ 添加了 CORS 补丁支持
2. ✅ 添加了 playwright/scraping 支持
3. ✅ 优化了生产环境 Gunicorn 配置
4. ✅ 添加了环境变量配置（前端）

### 可能的问题：
1. ⚠️ 第二次 `uv sync` 缺少 `--frozen` 标志
2. ⚠️ 构建上下文路径需要确认
3. ⚠️ 依赖安装顺序可能需要调整

### 建议：
1. 检查后端容器的启动日志
2. 确认构建上下文是否正确
3. 考虑在第二次 `uv sync` 时添加 `--frozen` 标志
4. 验证所有依赖是否正确安装

