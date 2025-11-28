# Cognee MCP CORS 配置修复

## 问题描述

### 问题 1：CORS 错误

前端（`http://192.168.66.11:3000`）访问 MCP 服务器（`http://192.168.66.11:8001/health`）时被 CORS 策略阻止：

```
Access to fetch at 'http://192.168.66.11:8001/health' from origin 'http://192.168.66.11:3000' 
has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

### 问题 2：400 Bad Request

前端尝试连接 cloud 服务时返回 400 错误：

```
POST http://192.168.66.11:8000/api/v1/checks/connection 400 (Bad Request)
Failed to connect to the cloud service. Please add… key to local instance. [CloudApiKeyMissingError]
```

## 原因分析

### CORS 问题

MCP 服务器的 CORS 配置是硬编码的，只允许 `http://localhost:3000`：

```python
# 修复前（硬编码）
allow_origins=["http://localhost:3000"]
```

没有读取 `CORS_ALLOWED_ORIGINS` 环境变量，导致前端无法从其他地址访问。

### 400 错误问题

1. **配置错误**：`NEXT_PUBLIC_CLOUD_API_URL` 被设置为 MCP 服务器地址（`http://192.168.66.11:8001`）
2. **端点不存在**：`/api/v1/checks/connection` 是 cognee API 服务器的端点，不是 MCP 服务器的端点
3. **本地部署**：本地部署不需要 cloud API，应该禁用或指向正确的服务

## 解决方案

### 1. 修复 MCP 服务器的 CORS 配置

修改 `project/cognee/cognee-mcp/src/server.py`，使其从环境变量读取 CORS 配置：

```python
# 修复后（从环境变量读取）
CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS")
if CORS_ALLOWED_ORIGINS:
    if CORS_ALLOWED_ORIGINS.strip() == "*":
        allowed_origins = ["*"]
        allow_credentials = False
    else:
        allowed_origins = [
            origin.strip() for origin in CORS_ALLOWED_ORIGINS.split(",") if origin.strip()
        ]
        allow_credentials = True
else:
    allowed_origins = [os.getenv("UI_APP_URL", "http://localhost:3000")]
    allow_credentials = True
```

**修改位置**：
- `run_sse_with_cors()` 函数
- `run_http_with_cors()` 函数

### 2. 更新 docker-compose 配置

#### 2.1 添加 MCP 服务器的 CORS 配置

在 `cognee-mcp` 服务中添加 `CORS_ALLOWED_ORIGINS` 环境变量：

```yaml
cognee-mcp:
  environment:
    # ==================== CORS 配置 ====================
    # 注意：必须包含前端访问的地址，否则会出现 CORS 错误
    - CORS_ALLOWED_ORIGINS=http://192.168.99.100:3000,http://192.168.66.11:3000,http://localhost:3000,http://127.0.0.1:3000,http://192.168.66.11:8000,http://localhost:8000,http://127.0.0.1:8000,http://192.168.66.11:8001
```

#### 2.2 修复前端 cloud API 配置

对于本地部署，应该注释掉或清空 `NEXT_PUBLIC_CLOUD_API_URL`：

```yaml
frontend:
  environment:
    - NEXT_PUBLIC_BACKEND_API_URL=http://192.168.66.11:8000
    # NEXT_PUBLIC_CLOUD_API_URL: 本地部署不需要 cloud API，留空或注释掉
    # 如果设置为 MCP 服务器地址，会导致 400 错误（MCP 服务器没有 /api/v1/checks/connection 端点）
    # - NEXT_PUBLIC_CLOUD_API_URL=http://192.168.66.11:8001
    - NEXT_PUBLIC_MCP_API_URL=http://192.168.66.11:8001
```

## 配置说明

### CORS_ALLOWED_ORIGINS 格式

- **多个来源**：逗号分隔的 URL 列表
  ```
  CORS_ALLOWED_ORIGINS=http://192.168.66.11:3000,http://localhost:3000
  ```

- **允许所有来源**：使用 `*`（不推荐用于生产环境）
  ```
  CORS_ALLOWED_ORIGINS=*
  ```
  注意：使用 `*` 时，`allow_credentials` 会自动设置为 `False`

### 前端环境变量说明

| 变量 | 说明 | 本地部署推荐值 |
|------|------|---------------|
| `NEXT_PUBLIC_BACKEND_API_URL` | Cognee API 服务器地址 | `http://192.168.66.11:8000` |
| `NEXT_PUBLIC_CLOUD_API_URL` | Cloud Cognee 服务地址 | 留空或注释（本地部署不需要） |
| `NEXT_PUBLIC_MCP_API_URL` | MCP 服务器地址 | `http://192.168.66.11:8001` |
| `NEXT_PUBLIC_COGWIT_API_KEY` | Cloud API 密钥 | 留空（本地部署不需要） |
| `NEXT_PUBLIC_IS_CLOUD_ENVIRONMENT` | 是否为 cloud 环境 | `false` |

## 验证修复

### 1. 重新构建 MCP 镜像

```bash
# 重新构建包含 CORS 修复的镜像
docker build -f deployment/docker/cognee-mcp/Dockerfile.api -t cognee-mcp:api-0.4.1 .
```

### 2. 重启服务

```bash
docker-compose -f deployment/docker-compose-test.1panel.yml --profile mcp up -d cognee-mcp
```

### 3. 检查 CORS 响应头

```bash
# 检查 MCP 服务器的 CORS 响应头
curl -H "Origin: http://192.168.66.11:3000" \
     -H "Access-Control-Request-Method: GET" \
     -X OPTIONS \
     http://192.168.66.11:8001/health -v
```

应该看到：
```
Access-Control-Allow-Origin: http://192.168.66.11:3000
```

### 4. 检查前端

打开浏览器控制台，应该不再看到 CORS 错误。

## 注意事项

1. **MCP 服务器 CORS 配置**：必须包含前端访问的所有地址
2. **Cloud API 配置**：本地部署时应该禁用或指向正确的服务
3. **环境变量同步**：确保 `cognee` 和 `cognee-mcp` 服务的 `CORS_ALLOWED_ORIGINS` 配置一致

## 相关文件

- `project/cognee/cognee-mcp/src/server.py` - MCP 服务器 CORS 配置
- `deployment/docker-compose-test.1panel.yml` - Docker Compose 配置
- `project/cognee/cognee/api/client.py` - Cognee API 服务器 CORS 配置（参考）

