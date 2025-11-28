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
    cmake \
    clang \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy pyproject.toml and lockfile first for better caching
# 构建上下文是项目根目录，所以路径是 project/cognee/...
COPY project/cognee/README.md project/cognee/pyproject.toml project/cognee/uv.lock project/cognee/entrypoint.sh ./

# Install the project's dependencies using the lockfile and settings
# 添加 scraping extra 以安装 protego 和 playwright（消除警告）
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --extra debug --extra api --extra postgres --extra neo4j --extra llama-index --extra ollama --extra mistral --extra groq --extra anthropic --extra scraping --frozen --no-install-project --no-dev --no-editable

# Note: pgvector is included in the postgres extra dependencies
# No additional adapter installation needed for pgvector

# Copy Alembic configuration
COPY project/cognee/alembic.ini /app/alembic.ini
COPY project/cognee/alembic/ /app/alembic

# Then, add the rest of the project source code and install it
# Installing separately from its dependencies allows optimal layer caching
COPY project/cognee/cognee /app/cognee
COPY project/cognee/distributed /app/distributed

# Apply CozyCognee patches (CORS configuration)
# Copy patch script and apply it to client.py
COPY deployment/docker/cognee/patch_cors.py /tmp/patch_cors.py
RUN python3 /tmp/patch_cors.py /app/cognee/api/client.py && rm /tmp/patch_cors.py

RUN --mount=type=cache,target=/root/.cache/uv \
uv sync --extra debug --extra api --extra postgres --extra neo4j --extra llama-index --extra ollama --extra mistral --extra groq --extra anthropic --extra scraping --frozen --no-dev --no-editable

# Install playwright browsers (消除警告)
# 注意：这会增加镜像大小（约 200MB），如果不需要 web scraping 功能可以注释掉
# 在构建阶段安装，因为这里有完整的系统依赖
RUN python3 -m playwright install --with-deps chromium 2>/dev/null || echo "Playwright browsers installation skipped (optional)"

# Note: pgvector support is included via postgres extra dependencies

FROM python:3.12-slim-bookworm

RUN apt-get update && apt-get install -y \
    libpq5 \
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

WORKDIR /app

COPY --from=uv /app /app
# Copy playwright browsers if installed
COPY --from=uv /root/.cache/ms-playwright /root/.cache/ms-playwright 2>/dev/null || true
# COPY --from=uv /app/.venv /app/.venv
# COPY --from=uv /root/.local /root/.local

RUN chmod +x /app/entrypoint.sh

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

ENV PYTHONPATH=/app
# ENV LOG_LEVEL=ERROR
ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["/app/entrypoint.sh"]

