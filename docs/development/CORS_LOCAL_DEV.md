# 本地开发 CORS 跨域问题排查

## 问题说明

在本地开发环境中，如果前端和后端运行在不同的端口（例如前端 `localhost:3000`，后端 `localhost:8000`），浏览器会将其视为**不同的源**，从而触发 CORS（跨域资源共享）检查。

### 为什么删除正常，创建失败？

- **DELETE 请求**：可能不会触发 CORS 预检请求（简单请求），或者即使触发了也成功通过
- **POST 请求**：会触发 CORS 预检请求（因为设置了 `Content-Type: application/json`），如果后端没有正确配置 CORS，预检请求会失败

## 解决方案

### 方案一：配置后端 CORS（推荐）

在 `project/cognee/.env` 文件中添加：

```bash
# 允许所有来源（最简单，适合本地开发）
CORS_ALLOWED_ORIGINS=*
```

或者指定具体的前端地址：

```bash
# 指定具体地址（更安全）
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

**重要**：
- 使用 `*` 时，后端会禁用 `allow_credentials`（浏览器安全限制）
- 使用具体地址列表时，可以启用 `allow_credentials`

### 方案二：使用 Nginx 反向代理（生产环境）

在生产环境（Docker Compose）中，使用 Nginx 反向代理可以避免 CORS 问题：

```
前端 (localhost:3000)
    ↓
Nginx (localhost:8080) ← 统一入口
    ↓
后端 (localhost:8000)
```

所有请求都通过同一个源（Nginx），浏览器不会触发 CORS 检查。

## 验证 CORS 配置

### 1. 检查后端环境变量

```bash
cd project/cognee
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('CORS_ALLOWED_ORIGINS:', os.getenv('CORS_ALLOWED_ORIGINS'))"
```

### 2. 测试 OPTIONS 预检请求

```bash
curl -X OPTIONS http://localhost:8000/api/v1/datasets \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type" \
  -v
```

应该看到响应头包含：
```
Access-Control-Allow-Origin: http://localhost:3000
Access-Control-Allow-Methods: POST
Access-Control-Allow-Headers: Content-Type
```

### 3. 测试实际 POST 请求

```bash
curl -X POST http://localhost:8000/api/v1/datasets \
  -H "Origin: http://localhost:3000" \
  -H "Content-Type: application/json" \
  -d '{"name": "test-dataset"}' \
  -v
```

## 常见错误

### 错误 1: `Access-Control-Allow-Origin` header is missing

**原因**：后端没有配置 CORS 或配置不正确

**解决**：在 `.env` 文件中添加 `CORS_ALLOWED_ORIGINS=*`

### 错误 2: Credentials mode is 'include' but 'Access-Control-Allow-Origin' is '*'

**原因**：使用 `*` 通配符时，不能同时使用 `credentials: "include"`

**解决**：
- 方案 A：使用具体地址列表而不是 `*`
- 方案 B：前端请求中移除 `credentials: "include"`（如果不需要）

### 错误 3: Preflight request doesn't pass access control check

**原因**：OPTIONS 预检请求失败

**解决**：
1. 确认后端已配置 CORS
2. 确认后端允许 `OPTIONS` 方法
3. 检查后端日志，查看预检请求是否到达

## 后端 CORS 配置说明

后端使用 FastAPI 的 `CORSMiddleware`，配置逻辑如下：

```python
# 从环境变量读取
CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS")

if CORS_ALLOWED_ORIGINS:
    if CORS_ALLOWED_ORIGINS.strip() == "*":
        allowed_origins = ["*"]
        allow_credentials = False  # 使用 * 时禁用 credentials
    else:
        allowed_origins = [origin.strip() for origin in CORS_ALLOWED_ORIGINS.split(",")]
        allow_credentials = True
else:
    # 默认只允许 http://localhost:3000
    allowed_origins = [os.getenv("UI_APP_URL", "http://localhost:3000")]
    allow_credentials = True
```

## 为什么 Docker/Nginx 环境不需要配置 CORS？

在 Docker Compose 环境中：

1. **Nginx 作为反向代理**：所有请求都通过 Nginx（`localhost:8080`）
2. **统一源**：前端和后端都通过同一个源（Nginx）访问
3. **浏览器不触发 CORS**：因为请求来自同一个源
4. **Nginx 处理 CORS 头**：Nginx 配置文件中已经设置了 CORS 响应头

因此，Docker/Nginx 环境不需要在后端配置 CORS，Nginx 已经处理了跨域问题。

## 相关文档

- [本地开发配置指南](./LOCAL_DEV_SETUP.md)
- [反向代理配置指南](../deployment/REVERSE_PROXY_SETUP.md)
- [CORS 修复说明](../deployment/CORS_FIX.md)

