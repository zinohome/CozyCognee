# CozyCognee 项目结构

本文档详细说明 CozyCognee 项目的目录结构和文件组织。

## 📁 项目根目录结构

```
CozyCognee/
├── .gitignore              # Git 忽略文件配置
├── .cursorrules            # Cursor 编辑器规则配置
├── README.md               # 项目主文档
│
├── deployment/             # 部署相关文件
│   ├── docker/             # Docker 镜像构建文件
│   │   ├── cognee/         # Cognee 后端服务
│   │   │   ├── Dockerfile
│   │   │   └── entrypoint.sh
│   │   ├── cognee-frontend/ # Cognee 前端服务
│   │   │   └── Dockerfile
│   │   └── cognee-mcp/      # Cognee MCP 服务
│   │       ├── Dockerfile
│   │       └── entrypoint.sh
│   ├── scripts/             # 部署脚本
│   │   ├── start.sh         # 启动脚本
│   │   ├── stop.sh          # 停止脚本
│   │   └── restart.sh       # 重启脚本
│   ├── docker-compose.yml   # 标准 Docker Compose 配置
│   ├── docker-compose.1panel.yml  # 1Panel 编排配置
│   ├── env.example          # 环境变量配置示例
│   └── README.md            # 部署目录说明
│
├── docs/                    # 项目文档（所有文档必须在此目录下）
│   ├── README.md            # 文档索引
│   ├── PROJECT_STRUCTURE.md # 项目结构说明（本文件）
│   ├── deployment/          # 部署文档
│   │   └── README.md        # 详细部署指南
│   ├── development/         # 开发文档
│   │   └── README.md        # 开发环境配置和开发指南
│   └── usage/               # 使用文档
│       └── README.md        # 使用方法和最佳实践
│
└── project/                 # Cognee 官方项目副本（Git 忽略）
    ├── .gitkeep            # 保持目录结构
    └── cognee/              # 与官方同步的 Cognee 源码（需初始化）
        ├── cognee/          # 核心库
        ├── cognee-frontend/ # 前端代码
        ├── cognee-mcp/      # MCP 服务代码
        └── ...              # 其他官方文件
```

## 📂 目录详细说明

### deployment/ - 部署目录

包含所有部署相关的配置和脚本。

#### docker/ - Docker 构建文件

每个服务都有独立的 Docker 目录：

- **cognee/**: Cognee 后端服务的 Dockerfile 和启动脚本
- **cognee-frontend/**: 前端服务的 Dockerfile
- **cognee-mcp/**: MCP 服务的 Dockerfile 和启动脚本

#### scripts/ - 部署脚本

便捷的部署管理脚本：

- `start.sh`: 启动服务，包含环境检查
- `stop.sh`: 停止所有服务
- `restart.sh`: 重启服务

#### Docker Compose 文件

- `docker-compose.yml`: 标准配置，适用于本地开发
- `docker-compose.1panel.yml`: 1Panel 专用配置，包含健康检查

### docs/ - 文档目录

完整的项目文档：

- **deployment/**: 部署相关文档
  - 标准部署步骤
  - 1Panel 部署指南
  - 环境配置说明
  - 故障排查

- **development/**: 开发相关文档
  - 开发环境设置
  - 本地开发指南
  - Docker 开发
  - 代码同步方法

- **usage/**: 使用相关文档
  - API 使用示例
  - 前端使用指南
  - MCP 集成
  - 最佳实践

### project/ - 项目源码

维护 Cognee 官方项目的副本，用于：

- 与官方代码同步
- 本地开发和测试
- Docker 镜像构建

**注意**: 
- `project/` 目录在 `.gitignore` 中被忽略，不会提交到 Git 仓库
- 每个开发者需要使用 `scripts/init-project.sh` 脚本初始化此目录
- 这样可以避免将大量第三方代码提交到仓库，也避免潜在的许可证问题

## 🔄 文件关系

### Docker 构建流程

```
deployment/docker-compose.yml
  └── build context: deployment/
      └── dockerfile: docker/cognee/Dockerfile
          └── COPY: ../../project/cognee/...
```

### 文档组织

```
README.md (根目录)
  ├── 快速开始
  └── 链接到 docs/
      ├── deployment/README.md
      ├── development/README.md
      └── usage/README.md
```

## 📝 重要文件说明

### .gitignore

配置了以下忽略规则：
- Python 相关（`__pycache__`, `.venv`, `*.pyc` 等）
- Node.js 相关（`node_modules/`, `.next/` 等）
- 环境变量文件（`.env`）
- 日志文件（`*.log`, `logs/`）
- 数据库文件（`*.db`, `*.sqlite`）
- Docker 相关（`.dockerignore`）
- IDE 配置（`.vscode/`, `.idea/`）

### env.example

环境变量配置模板，包含：
- 基础配置（DEBUG, ENVIRONMENT, LOG_LEVEL）
- LLM 配置（API_KEY, PROVIDER, MODEL）
- 数据库配置（DB_PROVIDER, DB_HOST 等）
- 向量数据库配置
- 图数据库配置
- MCP 配置

## 🚀 使用流程

### 首次部署

1. 克隆项目
2. 配置环境变量：`cp deployment/env.example deployment/.env`
3. 编辑 `.env` 文件
4. 运行启动脚本：`./deployment/scripts/start.sh`

### 日常开发

1. 在 `project/cognee/` 中修改代码
2. 使用 Docker Compose 测试：`cd deployment && docker-compose up -d`
3. 查看日志：`docker-compose logs -f`

### 代码同步

1. 进入 `project/cognee/`
2. 同步官方代码：`git fetch upstream && git merge upstream/main`

## 📊 项目规模

- **部署文件**: ~10 个 Docker 相关文件
- **文档文件**: ~5 个 Markdown 文档
- **脚本文件**: 3 个 Shell 脚本
- **配置文件**: 2 个 Docker Compose 文件 + 1 个环境变量示例

## 🔗 相关链接

- [项目 README](../README.md)
- [文档索引](./README.md)
- [部署文档](./deployment/README.md)
- [开发文档](./development/README.md)
- [使用文档](./usage/README.md)

