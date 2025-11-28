# CozyCognee

CozyCognee 是 Cognee 项目的本地化 Docker Compose 部署优化版本。本项目提供了完整的 Docker 化部署方案，包括标准 Docker Compose 和 1Panel 编排版本。

## 📁 项目结构

```
CozyCognee/
├── deployment/              # 部署相关文件
│   ├── docker/              # Docker 镜像构建文件
│   │   ├── cognee/          # Cognee 后端服务
│   │   ├── cognee-frontend/ # Cognee 前端服务
│   │   └── cognee-mcp/      # Cognee MCP 服务
│   ├── docker-compose.yml   # 标准 Docker Compose 配置
│   ├── docker-compose.1panel.yml  # 1Panel 编排配置
│   └── env.example          # 环境变量配置示例
├── docs/                    # 项目文档
│   ├── deployment/          # 部署文档
│   ├── development/         # 开发文档
│   └── usage/               # 使用文档
├── project/                 # Cognee 官方项目副本
│   └── cognee/              # 与官方同步的 Cognee 源码
└── README.md                # 本文件
```

## 🚀 快速开始

### 前置要求

- Docker 和 Docker Compose
- Git
- 至少 8GB 可用内存

### 本地开发部署

1. **克隆项目**
   ```bash
   git clone <your-repo-url>
   cd CozyCognee
   ```

2. **初始化项目目录**
   ```bash
   # project/ 目录包含 Cognee 官方代码，需要单独初始化
   ./scripts/init-project.sh
   ```

3. **配置环境变量**
   ```bash
   cd deployment
   cp env.example .env
   # 编辑 .env 文件，配置您的 LLM API 密钥等
   ```

3. **启动服务**
   ```bash
   # 启动核心服务
   docker-compose up -d cognee
   
   # 启动前端（可选）
   docker-compose --profile ui up -d frontend
   
   # 启动数据库服务（根据需要选择）
   docker-compose --profile postgres up -d postgres
   docker-compose --profile neo4j up -d neo4j
   docker-compose --profile chromadb up -d chromadb
   ```

4. **访问服务**
   - Cognee API: http://localhost:8000
   - Frontend: http://localhost:3000
   - Neo4j Browser: http://localhost:7474
   - ChromaDB: http://localhost:3002

### 1Panel 部署

1. **在 1Panel 中创建应用**
   - 使用 `docker-compose.1panel.yml` 文件
   - 配置环境变量
   - 设置数据卷挂载路径

2. **启动服务**
   - 通过 1Panel 界面启动服务
   - 或使用命令行：`docker-compose -f docker-compose.1panel.yml up -d`

## 📚 文档

详细文档请参考 [docs](./docs/) 目录：

- [文档索引](./docs/README.md) - 文档导航和索引
- [项目结构](./docs/PROJECT_STRUCTURE.md) - 项目目录结构说明
- [部署文档](./docs/deployment/) - 详细的部署指南
- [开发文档](./docs/development/) - 开发环境配置和开发指南
- [使用文档](./docs/usage/) - 使用说明和最佳实践

**注意**: 所有项目文档必须放在 `docs/` 目录下并按子目录整理，详见 [.cursorrules](.cursorrules) 中的文档组织规则。

## 🔧 配置说明

### 环境变量

主要环境变量配置（完整列表见 `deployment/env.example`）：

- `LLM_API_KEY`: LLM API 密钥（必需）
- `LLM_PROVIDER`: LLM 提供商（openai, anthropic, groq 等）
- `DB_PROVIDER`: 数据库类型（sqlite, postgres）
- `VECTOR_DB_PROVIDER`: 向量数据库类型（pgvector, chroma, qdrant 等）
- `GRAPH_DATABASE_PROVIDER`: 图数据库类型（kuzu, neo4j）

### 服务配置

- **cognee**: 核心后端服务，端口 8000
- **cognee-frontend**: 前端服务，端口 3000
- **cognee-mcp**: MCP 服务，端口 8001
- **postgres**: PostgreSQL 关系数据库，端口 5432
- **pgvector**: pgvector 向量数据库（独立的 PostgreSQL 实例），端口 5433
- **neo4j**: Neo4j 图数据库，端口 7474/7687
- **redis**: Redis 缓存，端口 6379

## 🛠️ 开发

### 本地开发模式

在本地开发时，建议直接运行项目代码而不是使用 Docker：

```bash
cd project/cognee
# 按照官方文档配置和运行
```

### 同步官方代码

`project/cognee` 目录用于维护 Cognee 官方项目的副本，可以通过以下方式同步：

```bash
cd project/cognee
git remote add upstream <official-repo-url>
git fetch upstream
git merge upstream/main
```

## 📝 注意事项

1. **镜像构建**: 当前配置为本地开发模式，Dockerfile 使用项目源码构建。生产环境建议先构建镜像再部署。

2. **数据持久化**: 确保重要数据目录已正确挂载到宿主机。

3. **环境变量**: 生产环境请务必修改默认密码和密钥。

4. **资源限制**: 根据实际需求调整 `docker-compose.yml` 中的资源限制。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

本项目遵循 Cognee 项目的许可证。

## 🔗 相关链接

- [Cognee 官方文档](https://docs.cognee.ai)
- [Cognee GitHub](https://github.com/topoteretes/cognee)

