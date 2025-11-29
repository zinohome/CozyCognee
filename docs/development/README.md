# 开发文档

本文档介绍 CozyCognee 的开发环境配置和开发指南。

## 目录

- [开发环境设置](#开发环境设置)
- [本地开发](#本地开发)
- [Docker 开发](#docker-开发)
- [项目结构](#项目结构)
- [代码同步](#代码同步)
- [构建镜像](#构建镜像)
- [常见问题](#常见问题)

## 详细文档

- [本地开发配置指南](./LOCAL_DEV_SETUP.md) - 详细的本地开发环境配置步骤
- [快速启动指南](./QUICK_START_COGNEE.md) - 快速启动 Cognee 后端
- [CORS 跨域问题排查](./CORS_LOCAL_DEV.md) - 本地开发时的 CORS 问题解决方案

## 开发环境设置

### 前置要求

- Python 3.10 - 3.13
- Node.js 18+ (用于前端开发)
- Docker 和 Docker Compose
- Git

### Python 环境

推荐使用 `uv` 进行 Python 包管理：

```bash
# 安装 uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 或使用 pip
pip install uv
```

### 前端环境

```bash
cd project/cognee/cognee-frontend
npm install
```

## 本地开发

### 运行 Cognee 后端

```bash
cd project/cognee

# 安装依赖
uv sync --extra api --extra postgres --extra neo4j

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件

# 运行数据库迁移
alembic upgrade head

# 启动开发服务器
uv run python -m cognee.api.client
```

### 运行前端

```bash
cd project/cognee/cognee-frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### 运行 MCP 服务

```bash
cd project/cognee/cognee-mcp

# 安装依赖
uv sync

# 运行 MCP 服务器
uv run cognee-mcp --transport sse --host 0.0.0.0 --port 8001
```

## Docker 开发

### 开发模式启动

使用 Docker Compose 进行开发，代码变更会自动反映：

```bash
cd deployment

# 启动开发环境
docker-compose up -d

# 查看日志
docker-compose logs -f cognee
```

### 调试模式

启用调试模式：

```bash
# 修改 .env 文件
DEBUG=true

# 重启服务
docker-compose restart cognee
```

调试端口：5678

### 代码热重载

Docker Compose 配置中已包含代码卷挂载，修改代码后服务会自动重载。

## 项目结构

```
CozyCognee/
├── deployment/              # 部署配置
│   ├── docker/              # Docker 构建文件
│   │   ├── cognee/
│   │   ├── cognee-frontend/
│   │   └── cognee-mcp/
│   └── docker-compose.yml
├── docs/                    # 文档
├── project/                 # 项目源码
│   └── cognee/              # Cognee 官方项目
│       ├── cognee/          # 核心库
│       ├── cognee-frontend/ # 前端
│       ├── cognee-mcp/      # MCP 服务
│       └── ...
└── README.md
```

## 初始化项目

### 首次设置

`project/` 目录在 `.gitignore` 中被忽略，每个开发者需要自己初始化：

```bash
# 使用初始化脚本（推荐）
./scripts/init-project.sh

# 或手动克隆
mkdir -p project
cd project
git clone https://github.com/topoteretes/cognee.git
cd cognee
git remote add upstream https://github.com/topoteretes/cognee.git
```

### 同步官方代码

`project/cognee` 目录用于维护 Cognee 官方项目的副本：

```bash
cd project/cognee

# 获取最新代码
git fetch upstream

# 合并到本地
git merge upstream/main

# 或使用 rebase
git rebase upstream/main
```

### 保持同步

建议定期同步官方代码：

```bash
# 使用初始化脚本更新（推荐）
./scripts/init-project.sh

# 或手动同步
cd project/cognee
git fetch upstream
git merge upstream/main
```

**注意**: `project/` 目录包含完整的 Cognee 官方代码，不会被提交到 Git 仓库。每个开发者需要自己初始化此目录。

## 构建镜像

### 构建单个镜像

```bash
cd deployment

# 构建 Cognee 后端镜像
docker build -f docker/cognee/Dockerfile -t cognee:latest .

# 构建前端镜像
docker build -f docker/cognee-frontend/Dockerfile -t cognee-frontend:latest .

# 构建 MCP 镜像
docker build -f docker/cognee-mcp/Dockerfile -t cognee-mcp:latest .
```

### 使用 Docker Compose 构建

```bash
cd deployment

# 构建所有镜像
docker-compose build

# 构建特定服务
docker-compose build cognee
```

### 生产镜像构建

生产环境建议：

1. **使用多阶段构建优化镜像大小**
2. **使用特定版本标签而非 latest**
3. **扫描镜像安全漏洞**

```bash
# 构建并标记版本
docker build -f docker/cognee/Dockerfile -t cognee:v1.0.0 .
docker build -f docker/cognee/Dockerfile -t cognee:latest .

# 推送到镜像仓库
docker tag cognee:v1.0.0 your-registry/cognee:v1.0.0
docker push your-registry/cognee:v1.0.0
```

## 开发工作流

### 1. 本地开发

- 在 `project/cognee` 中直接修改代码
- 使用本地 Python 环境运行和测试

### 2. Docker 测试

- 使用 Docker Compose 测试完整部署
- 验证容器化环境下的功能

### 3. 构建和部署

- 构建 Docker 镜像
- 部署到测试/生产环境

## 调试技巧

### Python 调试

```python
# 在代码中添加断点
import debugpy
debugpy.listen(5678)
debugpy.wait_for_client()
```

### 前端调试

```bash
# 启用 Next.js 调试
NODE_OPTIONS='--inspect' npm run dev
```

### 容器内调试

```bash
# 进入容器
docker-compose exec cognee bash

# 查看环境变量
docker-compose exec cognee env

# 运行命令
docker-compose exec cognee python -c "import cognee; print(cognee.__version__)"
```

## 测试

### 运行测试

```bash
cd project/cognee

# 运行所有测试
uv run pytest

# 运行特定测试
uv run pytest tests/test_api.py

# 带覆盖率
uv run pytest --cov=cognee tests/
```

### 集成测试

```bash
# 启动测试环境
docker-compose -f docker-compose.test.yml up -d

# 运行集成测试
pytest tests/integration/

# 清理
docker-compose -f docker-compose.test.yml down
```

## 贡献指南

1. Fork 本项目
2. 创建功能分支：`git checkout -b feature/your-feature`
3. 提交更改：`git commit -am 'Add some feature'`
4. 推送到分支：`git push origin feature/your-feature`
5. 提交 Pull Request

## 代码规范

- Python: 遵循 PEP 8
- TypeScript: 使用 ESLint 和 Prettier
- 提交信息: 使用清晰的提交信息

## 常见问题

### CORS 跨域问题

**问题**：本地开发时，前端创建 dataset 失败，出现 CORS 错误，但删除正常。

**原因**：前端（`localhost:3000`）和后端（`localhost:8000`）是不同源，POST 请求会触发 CORS 预检。

**解决**：在 `project/cognee/.env` 中添加 `CORS_ALLOWED_ORIGINS=*`

**详细说明**：请查看 [CORS 跨域问题排查文档](./CORS_LOCAL_DEV.md)

### 依赖安装失败

```bash
# 清理缓存
uv cache clean

# 重新安装
uv sync --reinstall
```

### 端口冲突

修改 `docker-compose.yml` 中的端口映射：

```yaml
ports:
  - "8001:8000"  # 将主机端口改为 8001
```

### 数据库迁移问题

```bash
# 重置数据库（谨慎使用）
docker-compose exec cognee alembic downgrade base
docker-compose exec cognee alembic upgrade head
```

