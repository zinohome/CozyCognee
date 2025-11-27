# Deployment 目录说明

本目录包含 CozyCognee 的所有部署相关文件。

## 📁 目录结构

```
deployment/
├── docker/                    # Docker 镜像构建文件
│   ├── cognee/               # Cognee 后端服务
│   │   ├── Dockerfile
│   │   └── entrypoint.sh
│   ├── cognee-frontend/      # Cognee 前端服务
│   │   └── Dockerfile
│   └── cognee-mcp/           # Cognee MCP 服务
│       ├── Dockerfile
│       └── entrypoint.sh
├── scripts/                   # 部署脚本
│   ├── start.sh              # 启动脚本
│   ├── stop.sh               # 停止脚本
│   └── restart.sh            # 重启脚本
├── docker-compose.yml         # 标准 Docker Compose 配置
├── docker-compose.1panel.yml  # 1Panel 编排配置
├── env.example               # 环境变量配置示例
└── README.md                 # 本文件
```

## 🚀 快速开始

### 1. 配置环境变量

```bash
cp env.example .env
# 编辑 .env 文件，配置您的 LLM API 密钥等
```

### 2. 启动服务

使用启动脚本（推荐）：
```bash
./scripts/start.sh
```

或使用 Docker Compose：
```bash
docker-compose up -d cognee
```

### 3. 访问服务

- Cognee API: http://localhost:8000
- API 文档: http://localhost:8000/docs
- 前端: http://localhost:3000 (需要启动前端服务)

## 📝 文件说明

### Docker Compose 文件

- **docker-compose.yml**: 标准 Docker Compose 配置，适用于本地开发和测试
- **docker-compose.1panel.yml**: 1Panel 编排配置
  - 使用外部网络 `1panel-network`
  - 所有数据存储在 `/data/cognee` 目录
  - 不包含 build 配置，镜像需单独构建
  - 包含 PostgreSQL、Redis、Qdrant、MinIO 等依赖服务

### 镜像构建

**重要**: `docker-compose.1panel.yml` 不包含 build 配置，需要先构建镜像：

```bash
# 构建所有镜像
./scripts/build-images.sh [version]

# 或构建单个镜像
./scripts/build-image.sh <service> [version]
```

详细说明请参考 [scripts/README.md](scripts/README.md)

### Docker 文件

每个服务的 Dockerfile 位于 `docker/<service-name>/` 目录中：
- `cognee/`: 核心后端服务
- `cognee-frontend/`: 前端服务
- `cognee-mcp/`: MCP 服务

### 脚本文件

- `start.sh`: 启动所有服务，包含交互式配置检查
- `stop.sh`: 停止所有服务
- `restart.sh`: 重启所有服务

## 🔧 配置说明

详细配置说明请参考 [部署文档](../docs/deployment/README.md)。

## 📚 更多信息

- [部署文档](../docs/deployment/README.md)
- [开发文档](../docs/development/README.md)
- [使用文档](../docs/usage/README.md)

