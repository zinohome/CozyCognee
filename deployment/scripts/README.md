# 部署脚本说明

本目录包含 CozyCognee 项目的部署和管理脚本。

## 脚本列表

### 服务管理脚本

- **start.sh**: 启动所有服务
- **stop.sh**: 停止所有服务
- **restart.sh**: 重启所有服务

### 镜像构建脚本

- **build-images.sh**: 构建所有 Docker 镜像
- **build-image.sh**: 构建单个 Docker 镜像

### 项目初始化脚本

- **init-project.sh**: 初始化 project/cognee 目录（位于项目根目录）

## 使用方法

### 构建镜像

#### 构建所有镜像

```bash
cd deployment
./scripts/build-images.sh [version]
```

示例：
```bash
# 使用默认版本 latest
./scripts/build-images.sh

# 指定版本
./scripts/build-images.sh v1.0.0
```

#### 构建单个镜像

```bash
cd deployment
./scripts/build-image.sh <service> [version]
```

示例：
```bash
# 构建 cognee 后端镜像
./scripts/build-image.sh cognee

# 构建前端镜像，指定版本
./scripts/build-image.sh cognee-frontend v1.0.0

# 构建 MCP 镜像
./scripts/build-image.sh cognee-mcp
```

支持的服务名称：
- `cognee` - Cognee 后端服务
- `cognee-frontend` 或 `frontend` - 前端服务
- `cognee-mcp` 或 `mcp` - MCP 服务

### 启动服务

```bash
cd deployment
./scripts/start.sh
```

### 停止服务

```bash
cd deployment
./scripts/stop.sh
```

### 重启服务

```bash
cd deployment
./scripts/restart.sh
```

## 镜像版本管理

### 版本命名规范

- `latest`: 最新构建的镜像（默认）
- `v1.0.0`: 语义化版本号
- `20241127`: 日期版本（YYYYMMDD）

### 镜像标签

构建的镜像会自动打上以下标签：
- `{image-name}:{version}` - 指定版本
- `{image-name}:latest` - 最新版本

### 镜像元数据

每个镜像包含以下标签（labels）：
- `org.opencontainers.image.created`: 构建时间
- `org.opencontainers.image.version`: 版本号
- `org.opencontainers.image.revision`: Git 提交哈希

## 1Panel 部署

在 1Panel 中使用时：

1. **构建镜像**（在本地或 CI/CD 环境）：
   ```bash
   ./scripts/build-images.sh v1.0.0
   ```

2. **推送到镜像仓库**（可选）：
   ```bash
   docker tag cognee:v1.0.0 your-registry/cognee:v1.0.0
   docker push your-registry/cognee:v1.0.0
   ```

3. **在 1Panel 中使用**：
   - 使用 `docker-compose.1panel.yml` 文件
   - 确保镜像已构建或从仓库拉取
   - 所有数据存储在 `/data/cognee` 目录

## 注意事项

1. **构建前准备**：
   - 确保已运行 `./scripts/init-project.sh` 初始化项目目录
   - 确保 Docker 已安装并运行

2. **镜像大小**：
   - Cognee 后端镜像较大（包含 Python 环境和依赖）
   - 前端镜像包含 Node.js 和构建产物
   - 建议定期清理未使用的镜像

3. **版本管理**：
   - 生产环境建议使用具体版本号而非 `latest`
   - 定期更新镜像以获取安全补丁

4. **数据持久化**：
   - 1Panel 部署时，所有数据存储在 `/data/cognee` 目录
   - 确保该目录有足够的磁盘空间
   - 定期备份重要数据

## 故障排查

### 构建失败

1. 检查 `project/cognee` 目录是否存在
2. 检查 Docker 是否运行：`docker ps`
3. 查看构建日志中的错误信息

### 镜像找不到

1. 确认镜像已构建：`docker images | grep cognee`
2. 检查镜像名称和版本是否正确
3. 如果使用远程仓库，确认已正确推送

### 服务启动失败

1. 检查镜像是否存在
2. 检查 `/data/cognee` 目录权限
3. 查看容器日志：`docker logs cognee`

