# 反向代理配置指南

使用 Nginx 或 Caddy 作为反向代理统一后端服务，避免 CORS 问题。

## 为什么需要反向代理？

1. **避免 CORS 问题**：所有 API 请求都来自同一个源（nginx/caddy），浏览器不会触发 CORS 检查
2. **统一入口**：前端只需要配置一个 API URL，由反向代理路由到对应的后端服务
3. **简化配置**：不需要在每个服务中配置 CORS 允许的来源列表
4. **更好的安全性**：可以统一处理认证、限流等

## 架构说明

```
前端 (3000)
    ↓
Nginx/Caddy (8080) ← 统一入口
    ├─ /api/* → cognee:8000
    ├─ /mcp-api/* → cognee-mcp-api:8000
    └─ /mcp-direct/* → cognee-mcp-direct:8000
```

## 使用 Nginx（推荐）

### 1. 启动服务

```bash
# 启动所有服务（包括反向代理）
docker-compose -f deployment/docker-compose.1panel.yml --profile mcp --profile proxy up -d
```

### 2. 前端配置

前端环境变量：
```yaml
- NEXT_PUBLIC_BACKEND_API_URL=http://192.168.66.11:8080/api
- NEXT_PUBLIC_MCP_API_URL=http://192.168.66.11:8080/mcp-api
```

### 3. API 端点

- **Cognee API**: `http://192.168.66.11:8080/api/*`
- **MCP API Mode**: `http://192.168.66.11:8080/mcp-api/*`
- **MCP Direct Mode**: `http://192.168.66.11:8080/mcp-direct/*`
- **健康检查**: 
  - `http://192.168.66.11:8080/health` (Cognee)
  - `http://192.168.66.11:8080/mcp-api/health` (MCP API)
  - `http://192.168.66.11:8080/mcp-direct/health` (MCP Direct)

### 4. 配置文件位置

- Nginx 配置: `deployment/nginx/nginx.conf`
- 日志目录: `/data/cognee/nginx/logs`

## 使用 Caddy（更简单）

### 1. 启用 Caddy

在 `docker-compose.1panel.yml` 中：
1. 注释掉 `nginx` 服务
2. 取消注释 `caddy` 服务

### 2. 启动服务

```bash
docker-compose -f deployment/docker-compose.1panel.yml --profile mcp --profile proxy up -d
```

### 3. 前端配置

与 Nginx 相同：
```yaml
- NEXT_PUBLIC_BACKEND_API_URL=http://192.168.66.11:8080/api
- NEXT_PUBLIC_MCP_API_URL=http://192.168.66.11:8080/mcp-api
```

### 4. 配置文件位置

- Caddy 配置: `deployment/caddy/Caddyfile`
- 数据目录: `/data/cognee/caddy/data`
- 配置目录: `/data/cognee/caddy/config`

## 优势对比

### Nginx
- ✅ 更成熟，使用广泛
- ✅ 性能优秀
- ✅ 配置灵活
- ❌ 需要手动配置 CORS（虽然我们通过同源避免了）

### Caddy
- ✅ 自动 HTTPS（如果有域名）
- ✅ 自动处理 CORS
- ✅ 配置更简单
- ✅ 自动证书管理
- ❌ 资源占用略高

## 注意事项

1. **端口映射**：
   - 反向代理监听 `8080` 端口
   - 后端服务不再直接暴露端口（已注释掉）

2. **健康检查**：
   - 所有服务的健康检查仍然有效
   - 可以通过反向代理访问健康检查端点

3. **SSE 支持**：
   - Nginx 和 Caddy 都配置了 SSE（Server-Sent Events）支持
   - 用于 MCP 的实时通信

4. **WebSocket 支持**：
   - Nginx 配置了 WebSocket 支持
   - 用于 Cognee API 的 WebSocket 连接

5. **日志**：
   - Nginx 日志: `/data/cognee/nginx/logs`
   - Caddy 日志: 在容器内，可以通过 `docker logs` 查看

## 故障排查

### 1. 检查反向代理是否运行

```bash
# 检查容器状态
docker ps | grep nginx
# 或
docker ps | grep caddy

# 检查健康状态
curl http://192.168.66.11:8080/
```

### 2. 检查后端服务

```bash
# 检查 Cognee API
curl http://192.168.66.11:8080/health

# 检查 MCP API
curl http://192.168.66.11:8080/mcp-api/health

# 检查 MCP Direct
curl http://192.168.66.11:8080/mcp-direct/health
```

### 3. 查看日志

```bash
# Nginx 日志
docker logs cognee_nginx

# Caddy 日志
docker logs cognee_caddy

# 后端服务日志
docker logs cognee
docker logs cognee-mcp-api
docker logs cognee-mcp-direct
```

### 4. 测试路由

```bash
# 测试 API 路由
curl http://192.168.66.11:8080/api/v1/health

# 测试 MCP API 路由
curl http://192.168.66.11:8080/mcp-api/health
```

## 自定义配置

### 修改 Nginx 配置

编辑 `deployment/nginx/nginx.conf`，然后重启服务：

```bash
docker-compose -f deployment/docker-compose.1panel.yml restart nginx
```

### 修改 Caddy 配置

编辑 `deployment/caddy/Caddyfile`，然后重启服务：

```bash
docker-compose -f deployment/docker-compose.1panel.yml restart caddy
```

## 生产环境建议

1. **使用域名**：
   - 配置域名解析
   - Caddy 可以自动申请 SSL 证书
   - Nginx 需要手动配置 SSL

2. **安全加固**：
   - 添加访问限制
   - 配置防火墙规则
   - 启用日志审计

3. **性能优化**：
   - 配置缓存策略
   - 启用压缩
   - 调整连接池大小

