# 健康检查配置分析与优化建议

本文档分析所有服务的健康检查配置，评估其效率和合理性。

## 当前健康检查配置总览

### 1. Cognee 主服务 (cognee)

**配置**：
```yaml
test: ["CMD", "curl", "-f", "--max-time", "10", "http://localhost:8000/docs"]
interval: 30s
timeout: 10s
retries: 3
start_period: 90s
```

**分析**：
- ✅ **端点正确**：使用 `/docs` 确保 FastAPI 完全启动
- ⚠️ **效率问题**：
  - `start_period: 90s` 可能过长，FastAPI 通常 30-60 秒内启动
  - `--max-time: 10` 秒可能过长，`/docs` 端点通常 2-5 秒内响应
- ✅ **重试机制合理**：3 次重试足够

**优化建议**：
```yaml
test: ["CMD", "curl", "-f", "--max-time", "5", "http://localhost:8000/docs"]
interval: 30s
timeout: 5s
retries: 3
start_period: 60s  # 减少到 60 秒
```

---

### 2. Cognee MCP API Mode (cognee-mcp-api)

**配置**：
```yaml
test: ["CMD", "curl", "-f", "--max-time", "10", "http://localhost:8000/health"]
interval: 30s
timeout: 10s
retries: 3
start_period: 60s
```

**分析**：
- ✅ **端点正确**：使用 `/health` 端点（MCP 服务器提供）
- ⚠️ **效率问题**：
  - `--max-time: 10` 秒过长，`/health` 端点应该很快（< 1 秒）
  - `start_period: 60s` 合理，MCP API Mode 启动较快
- ✅ **重试机制合理**

**优化建议**：
```yaml
test: ["CMD", "curl", "-f", "--max-time", "3", "http://localhost:8000/health"]
interval: 30s
timeout: 3s
retries: 3
start_period: 45s  # 可以稍微减少
```

---

### 3. Cognee MCP Direct Mode (cognee-mcp-direct)

**当前配置**（❌ **有问题**）：
```yaml
test: ["CMD", "curl", "-f", "--max-time", "10", "http://localhost:8000/docs"]
interval: 30s
timeout: 10s
retries: 3
start_period: 90s
```

**问题**：
- ❌ **端点错误**：MCP Direct Mode 不是 FastAPI，没有 `/docs` 端点
- ❌ **应该使用**：`/health` 端点

**正确配置**：
```yaml
test: ["CMD", "curl", "-f", "--max-time", "3", "http://localhost:8000/health"]
interval: 30s
timeout: 3s
retries: 3
start_period: 60s  # Direct Mode 需要更多初始化时间
```

---

### 4. Nginx 反向代理 (nginx)

**配置**：
```yaml
test: ["CMD-SHELL", "ps | grep -q '[n]ginx' && nginx -t > /dev/null 2>&1"]
interval: 30s
timeout: 10s
retries: 3
start_period: 10s
```

**分析**：
- ✅ **检查方式合理**：检查进程 + 配置文件验证
- ✅ **效率高**：进程检查很快，配置文件验证也很快
- ✅ **启动等待时间合理**：Nginx 启动很快

**优化建议**：
- 可以考虑添加 HTTP 检查，确保 Nginx 真正可以处理请求：
```yaml
test: ["CMD-SHELL", "ps | grep -q '[n]ginx' && nginx -t > /dev/null 2>&1 && wget --quiet --tries=1 --spider http://localhost:80/health || exit 1"]
```
- 但需要确保 `wget` 可用，或者使用更轻量的检查方式

---

### 5. 前端服务 (frontend)

**配置**：
```yaml
test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost:3000"]
interval: 30s
timeout: 10s
retries: 3
```

**分析**：
- ✅ **检查方式合理**：HTTP 请求检查
- ⚠️ **缺少 start_period**：Next.js 启动可能需要时间
- ⚠️ **超时时间**：10 秒可能过长

**优化建议**：
```yaml
test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost:3000"]
interval: 30s
timeout: 5s
retries: 3
start_period: 30s  # Next.js 启动时间
```

---

### 6. PostgreSQL (postgres)

**配置**：
```yaml
test: ["CMD-SHELL", "pg_isready -U cognee_user -d cognee_db"]
interval: 10s
timeout: 5s
retries: 5
```

**分析**：
- ✅ **检查方式高效**：`pg_isready` 是 PostgreSQL 官方工具，非常快
- ✅ **检查频率合理**：10 秒间隔
- ✅ **重试次数充足**：5 次重试
- ✅ **超时时间合理**：5 秒

**评价**：✅ **配置优秀，无需优化**

---

### 7. pgvector (pgvector)

**配置**：
```yaml
test: ["CMD-SHELL", "pg_isready -U cognee_vector_user -d cognee_vector_db"]
interval: 10s
timeout: 5s
retries: 5
```

**分析**：
- ✅ **与 PostgreSQL 相同，配置优秀**

**评价**：✅ **配置优秀，无需优化**

---

### 8. Redis (redis)

**配置**：
```yaml
test: ["CMD", "redis-cli", "-a", "cognee_redis_password", "ping"]
interval: 10s
timeout: 3s
retries: 5
```

**分析**：
- ✅ **检查方式高效**：`redis-cli ping` 非常快
- ✅ **检查频率合理**：10 秒间隔
- ✅ **超时时间合理**：3 秒足够
- ✅ **重试次数充足**：5 次重试

**评价**：✅ **配置优秀，无需优化**

---

### 9. MinIO (minio)

**当前配置**：
```yaml
# 没有健康检查，使用 service_started
```

**分析**：
- ⚠️ **缺少健康检查**：无法确保 MinIO 真正可用

**优化建议**：
```yaml
healthcheck:
  test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost:9000/minio/health/live"]
  interval: 30s
  timeout: 5s
  retries: 3
  start_period: 30s
```

或者使用 MinIO 客户端：
```yaml
healthcheck:
  test: ["CMD", "mc", "ready", "local"]
  interval: 30s
  timeout: 5s
  retries: 3
  start_period: 30s
```

---

### 10. Neo4j (neo4j)

**配置**：
```yaml
test: ["CMD", "cypher-shell", "-u", "neo4j", "-p", "pleaseletmein", "RETURN 1"]
interval: 30s
timeout: 10s
retries: 3
```

**分析**：
- ✅ **检查方式合理**：执行简单查询验证数据库可用
- ⚠️ **效率问题**：
  - `cypher-shell` 启动和执行可能需要 2-5 秒
  - `timeout: 10s` 合理
  - `interval: 30s` 合理（Neo4j 是重量级服务）

**优化建议**：
- 可以考虑使用 HTTP 端点（如果可用）：
```yaml
test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost:7474"]
```
- 或者保持当前配置，但减少超时时间：
```yaml
test: ["CMD", "cypher-shell", "-u", "neo4j", "-p", "pleaseletmein", "RETURN 1"]
interval: 30s
timeout: 8s
retries: 3
start_period: 60s  # Neo4j 启动较慢
```

---

### 11. Redis Insight (redisinsight)

**配置**：
```yaml
test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost:5540"]
interval: 30s
timeout: 10s
retries: 3
```

**分析**：
- ✅ **检查方式合理**：HTTP 请求检查
- ⚠️ **缺少 start_period**：Redis Insight 启动可能需要时间

**优化建议**：
```yaml
test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost:5540"]
interval: 30s
timeout: 5s
retries: 3
start_period: 30s
```

---

## 总结与优化建议

### 需要立即修复的问题

1. ❌ **cognee-mcp-direct 使用错误的端点**：应使用 `/health` 而不是 `/docs`

### 效率优化建议

| 服务 | 当前问题 | 优化建议 |
|------|---------|---------|
| cognee | `start_period: 90s` 过长，`--max-time: 10` 过长 | 减少到 60s 和 5s |
| cognee-mcp-api | `--max-time: 10` 过长 | 减少到 3s |
| cognee-mcp-direct | ❌ 使用错误端点 | 改为 `/health`，`--max-time: 3s` |
| frontend | 缺少 `start_period`，`timeout: 10s` 过长 | 添加 `start_period: 30s`，减少到 5s |
| minio | ❌ 缺少健康检查 | 添加健康检查 |
| neo4j | 缺少 `start_period` | 添加 `start_period: 60s` |
| redisinsight | 缺少 `start_period`，`timeout: 10s` 过长 | 添加 `start_period: 30s`，减少到 5s |

### 配置优秀的服务

- ✅ PostgreSQL (postgres)
- ✅ pgvector
- ✅ Redis (redis)
- ✅ Nginx (nginx) - 可以进一步优化

---

## 健康检查最佳实践

1. **端点选择**：
   - FastAPI 服务：使用 `/docs` 确保完全启动
   - MCP 服务：使用 `/health` 端点
   - 数据库服务：使用专用工具（`pg_isready`, `redis-cli ping`）
   - Web 服务：使用 HTTP 请求

2. **超时时间**：
   - 轻量级服务（Redis, PostgreSQL）：3-5 秒
   - 中等服务（FastAPI, MCP）：5-8 秒
   - 重量级服务（Neo4j）：8-10 秒

3. **检查间隔**：
   - 关键服务（数据库）：10 秒
   - 应用服务：30 秒
   - 管理工具：30-60 秒

4. **启动等待时间**：
   - 快速启动服务（Nginx, Redis）：10-30 秒
   - 中等启动服务（FastAPI, MCP）：45-60 秒
   - 慢速启动服务（Neo4j, 大型应用）：60-90 秒

5. **重试次数**：
   - 关键服务：5 次
   - 一般服务：3 次

