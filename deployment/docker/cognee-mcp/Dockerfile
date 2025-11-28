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
# 参考 cognee Dockerfile 的构建方式，避免从 PyPI 安装包含 docs extra 的完整包
# 
# 关键优化：
# 1. 先复制 cognee 源代码，然后修改 pyproject.toml 使用本地路径
# 2. 移除 docs extra（unstructured 包占用 3-5GB）
# 3. 只安装必要的 extras（postgres, neo4j）

# 1. 先复制 cognee 源代码（必须在修改 pyproject.toml 之前）
COPY project/cognee/cognee /app/cognee
COPY project/cognee/distributed /app/distributed
COPY project/cognee/pyproject.toml /app/cognee-pyproject.toml

# 2. 复制 cognee-mcp 的依赖文件
COPY project/cognee/cognee-mcp/pyproject.toml project/cognee/cognee-mcp/uv.lock project/cognee/cognee-mcp/entrypoint.sh ./

# 3. 修改 pyproject.toml：使用本地 cognee 源代码，移除 docs extra
# 这样可以避免从 PyPI 安装包含 unstructured 的完整包
RUN sed -i 's|"cognee\[postgres,docs,neo4j\]==0.3.7"|"cognee[postgres,neo4j] @ file:///app"|' pyproject.toml

# 4. 安装依赖（使用本地 cognee 源代码，不包含 docs extra）
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev --no-editable

# 5. 复制 Alembic 配置（如果需要数据库迁移）
COPY project/cognee/alembic.ini /app/alembic.ini
COPY project/cognee/alembic/ /app/alembic

# 6. 复制 cognee-mcp 源代码并安装项目
COPY project/cognee/cognee-mcp/src /app/src
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-editable

FROM python:3.12-slim-bookworm

RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy the virtual environment from the uv stage
COPY --from=uv /usr/local /usr/local
COPY --from=uv /app /app

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

