# Cognee MCP 镜像大小优化指南

## 问题说明

默认的 `cognee-mcp:latest` 镜像包含完整的 cognee 库及其所有依赖（postgres、docs、neo4j 等），导致镜像大小约为 **8.5GB**。

## 解决方案

对于 **API Mode**，我们提供了轻量级镜像 `cognee-mcp:api-latest`，只安装必要的依赖，镜像大小约为 **2-3GB**，可以大幅减小镜像体积（减少约 60-70%）。

## 镜像对比

| 镜像 | 大小 | 用途 | 包含内容 |
|------|------|------|----------|
| `cognee-mcp:latest` | ~8.5GB | Direct Mode | 完整的 cognee 库 + 所有 extras (postgres, docs, neo4j 等) |
| `cognee-mcp:api-latest` | ~2-3GB | API Mode | 基础 cognee 包 + MCP 依赖 (fastmcp, mcp, httpx) |

## 构建轻量级镜像

### 方法 1：使用构建脚本（推荐）

```bash
cd deployment
./scripts/build-image.sh cognee-mcp-api
```

这会构建 `cognee-mcp:api-latest` 镜像。

### 方法 2：直接使用 Docker

```bash
# 从项目根目录执行
docker build -f deployment/docker/cognee-mcp/Dockerfile.api -t cognee-mcp:api-latest .
```

### 工作原理

改进后的 Dockerfile.api 使用标准方式：

1. **使用 `pyproject.toml.api`**：专门为 API Mode 设计的轻量级依赖配置
   - 只包含 `cognee==0.3.7`（基础包，不包含 extras）
   - 包含 MCP 必需的依赖（fastmcp, mcp, httpx）

2. **使用 `uv sync`**：与官方 Dockerfile 保持一致的标准方式
   - 自动解析依赖树
   - 支持版本锁定（如果提供 uv.lock）
   - 更好的依赖管理

3. **多阶段构建**：与官方 Dockerfile 相同的构建流程
   - 构建阶段：安装依赖
   - 运行阶段：最小化镜像

## 使用轻量级镜像

### 在 docker-compose.1panel.yml 中

```yaml
cognee-mcp:
  image: cognee-mcp:api-latest  # 使用轻量级镜像
  container_name: cognee-mcp
  restart: unless-stopped
  profiles:
    - mcp
  ports:
    - "8001:8000"
  environment:
    - TRANSPORT_MODE=sse
    - MCP_LOG_LEVEL=INFO
    - API_URL=http://cognee:8000  # API Mode 配置
  depends_on:
    cognee:
      condition: service_healthy
  networks:
    - 1panel-network
```

### 直接使用 Docker

```bash
docker run \
  -e TRANSPORT_MODE=sse \
  -e API_URL=http://cognee:8000 \
  -p 8001:8000 \
  --rm -it cognee-mcp:api-latest
```

## 为什么可以减小镜像？

### Direct Mode 需要的依赖

- 完整的 `cognee[postgres,docs,neo4j]` 包
- PostgreSQL 客户端库
- Neo4j 驱动
- 文档处理库
- 其他数据库适配器
- 等等...

### API Mode 需要的依赖

- 基础 `cognee` 包（仅用于 logging_utils）
- `fastmcp`（MCP 服务器框架）
- `mcp`（MCP 协议库）
- `httpx`（HTTP 客户端，用于 API 请求）

API Mode 下，所有实际的数据处理、LLM 调用、数据库操作都由 Cognee API 服务器处理，MCP 服务器只需要：
1. 接收 MCP 客户端请求
2. 转发到 Cognee API 服务器
3. 返回结果给 MCP 客户端

因此不需要安装完整的 cognee 依赖。

## 验证镜像大小

构建完成后，可以查看镜像大小：

```bash
docker images | grep cognee-mcp
```

输出示例：
```
cognee-mcp    api-latest     abc123def456   2 minutes ago    2.8GB
cognee-mcp    latest         def456abc123   5 minutes ago    8.5GB
```

## 注意事项

1. **API Mode 限制**：某些功能在 API Mode 下不可用（如 codify、prune 等），详见 [COGNEE_MCP_DEPLOYMENT.md](./COGNEE_MCP_DEPLOYMENT.md)

2. **确保 API 服务器运行**：使用 API Mode 时，必须确保 Cognee API 服务器已启动并可访问

3. **网络配置**：在 Docker Compose 中，确保 cognee-mcp 和 cognee 服务在同一网络中

4. **切换模式**：如果需要从 API Mode 切换到 Direct Mode，只需：
   - 将 `image: cognee-mcp:api-latest` 改为 `image: cognee-mcp:latest`
   - 添加所有必需的环境变量（LLM、数据库等）
   - 移除 `API_URL` 配置

## 性能影响

使用轻量级镜像不会影响性能，因为：
- API Mode 下的所有实际处理都在 Cognee API 服务器上完成
- MCP 服务器只负责协议转换和请求转发
- 镜像大小不影响运行时性能

## 总结

- ✅ **推荐使用 API Mode + 轻量级镜像**：镜像小、配置简单、性能无影响
- ⚠️ **Direct Mode + 完整镜像**：仅在需要完整功能时使用（codify、prune 等）

