# Use a Python image with uv pre-installed
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS uv

# Install the project into `/app`
WORKDIR /app

# Enable bytecode compilation
# ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Set build argument
ARG DEBUG

# Set environment variable based on the build argument
ENV DEBUG=${DEBUG}

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    git \
    curl \
    clang \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 优化：使用源代码而不是 PyPI 包，大幅减小镜像体积（从 8.5GB 减少到 ~1.5-2GB）
# 完全按照 cognee Dockerfile 的构建方式，确保一致性
# 
# 关键优化：
# 1. 使用本地 cognee 源代码（避免从 PyPI 安装包含 docs extra 的完整包）
# 2. 移除 docs extra（unstructured 包占用 3-5GB）
# 3. 只安装必要的 extras（postgres, neo4j, scraping）
# 注意：onnxruntime 和 fastembed 默认安装 CPU 版本，不会安装 NVIDIA 驱动（与 cognee 一致）

# 1. 将 cognee 源代码放在子目录中，避免与 cognee-mcp 的 pyproject.toml 冲突
# 与 cognee Dockerfile 保持一致：需要 README.md 用于构建
COPY project/cognee/README.md /app/cognee-source/README.md
COPY project/cognee/pyproject.toml /app/cognee-source/pyproject.toml
COPY project/cognee/cognee /app/cognee-source/cognee
COPY project/cognee/distributed /app/cognee-source/distributed

# 2. 复制 cognee-mcp 的依赖文件（包括 README.md，因为 pyproject.toml 中声明了 readme = "README.md"）
COPY project/cognee/cognee-mcp/pyproject.toml project/cognee/cognee-mcp/uv.lock project/cognee/cognee-mcp/entrypoint.sh ./
COPY project/cognee/cognee-mcp/README.md ./README.md

# 3. 修改 pyproject.toml：使用本地 cognee 源代码，移除 docs extra，添加 scraping extra
# 使用 file:///app/cognee-source 指向 cognee 源代码目录
# 这样可以避免从 PyPI 安装包含 unstructured 的完整包
# 添加 scraping extra 以安装 protego 和 playwright（消除警告，与 cognee 一致）
RUN sed -i 's|"cognee\[postgres,docs,neo4j\]==0.3.7"|"cognee[postgres,neo4j,scraping] @ file:///app/cognee-source"|' pyproject.toml

# 4. 安装依赖（使用本地 cognee 源代码，不包含 docs extra，包含 scraping extra）
# 注意：由于使用本地路径，不能使用 --frozen（lock 文件不匹配）
# onnxruntime 和 fastembed 默认安装 CPU 版本，不会安装 NVIDIA 驱动（与 cognee 一致）
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-install-project --no-dev --no-editable

# 5. 复制 Alembic 配置（如果需要数据库迁移）
# 注意：Alembic 配置用于 cognee 的数据库迁移，在 Direct Mode 下可能需要
COPY project/cognee/alembic.ini /app/alembic.ini
COPY project/cognee/alembic/ /app/alembic

# 6. 复制 cognee-mcp 源代码并安装项目（与 cognee Dockerfile 一致）
COPY project/cognee/cognee-mcp/src /app/src

# 应用 CozyCognee patches (CORS 配置)
# 复制 patch 脚本并应用到 server.py
COPY deployment/docker/cognee-mcp/patch_cors.py /tmp/patch_cors.py
RUN python3 /tmp/patch_cors.py /app/src/server.py && rm /tmp/patch_cors.py

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-dev --no-editable

# 7. 安装 playwright 浏览器（可选，消除警告）
# 注意：这会增加镜像大小（约 200MB），如果不需要 web scraping 功能可以注释掉
# 与 cognee Dockerfile 保持一致
RUN PLAYWRIGHT_BROWSERS_PATH=/app/.cache/ms-playwright python3 -m playwright install --with-deps chromium 2>/dev/null || echo "Playwright browsers installation skipped (optional)"

FROM python:3.12-slim-bookworm

RUN apt-get update && apt-get install -y \
    libpq5 \
    # playwright 浏览器运行时依赖（与 cognee Dockerfile 一致）
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

WORKDIR /app

# Copy the virtual environment from the uv stage
COPY --from=uv /usr/local /usr/local
COPY --from=uv /app /app
# playwright 浏览器已经通过 COPY --from=uv /app /app 一起复制过来了（在 /app/.cache/ms-playwright）
# 设置环境变量指向 playwright 浏览器位置（与 cognee Dockerfile 一致）
ENV PLAYWRIGHT_BROWSERS_PATH=/app/.cache/ms-playwright

RUN chmod +x /app/entrypoint.sh

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# Set environment variables for MCP server
ENV PYTHONUNBUFFERED=1
ENV MCP_LOG_LEVEL=DEBUG
ENV PYTHONPATH=/app

# Add labels for API mode usage
LABEL org.opencontainers.image.description="Cognee MCP Server with API mode support"

# Use the application name from pyproject.toml for normal operation
# For testing, we'll override this with a direct command
ENTRYPOINT ["/app/entrypoint.sh"]

