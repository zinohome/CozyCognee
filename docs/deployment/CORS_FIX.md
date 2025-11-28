# CORS 问题排查和修复指南

## 问题现象

访问 `http://192.168.66.11:8000/health/detailed` 时出现 CORS 错误：
```
Failed to fetch.
Possible Reasons:
CORS
Network Failure
URL scheme must be "http" or "https" for CORS request.
```

## 根本原因

1. **镜像未重新构建**：补丁代码没有应用到运行中的容器
2. **环境变量未生效**：容器未重启，环境变量没有加载
3. **CORS 配置限制**：官方代码不支持 `*` 通配符，需要明确列出所有来源

## 快速解决方案

### 方案 1: 重新构建镜像并重启（推荐）

```bash
# 1. 重新构建镜像（应用补丁）
cd /data/build/CozyCognee/deployment/scripts
./build-image.sh cognee latest

# 2. 重启容器
docker-compose -f /data/build/CozyCognee/deployment/docker-compose.1panel.yml restart cognee

# 或者如果使用 1Panel，在 1Panel 中重启容器
```

### 方案 2: 使用具体的 URL 列表（无需补丁）

如果不想重新构建镜像，可以直接使用具体的 URL 列表：

在 `docker-compose.1panel.yml` 中修改：

```yaml
- CORS_ALLOWED_ORIGINS=http://192.168.66.11:8000,http://192.168.66.11:3000,http://localhost:3000,http://localhost:8000,http://127.0.0.1:8000,http://127.0.0.1:3000
```

然后重启容器：

```bash
docker-compose -f docker-compose.1panel.yml restart cognee
```

### 方案 3: 检查运行中的容器

进入容器检查配置：

```bash
# 进入容器
docker exec -it cognee bash

# 检查环境变量
echo $CORS_ALLOWED_ORIGINS

# 检查代码是否已打补丁
grep -A 5 "CozyCognee Patch" /app/cognee/api/client.py

# 或者运行检查脚本
python3 /tmp/check_cors.py /app/cognee/api/client.py
```

## 验证修复

### 1. 检查 CORS 响应头

```bash
curl -v -H "Origin: http://192.168.66.11:8000" \
  http://192.168.66.11:8000/health \
  2>&1 | grep -i "access-control"
```

应该看到：
```
< Access-Control-Allow-Origin: http://192.168.66.11:8000
< Access-Control-Allow-Credentials: true
< Access-Control-Allow-Methods: OPTIONS, GET, PUT, POST, DELETE
```

### 2. 使用浏览器测试

在浏览器控制台运行：

```javascript
fetch('http://192.168.66.11:8000/health', {
  method: 'GET',
  headers: {
    'Accept': 'application/json'
  }
})
.then(r => r.json())
.then(console.log)
.catch(console.error)
```

## 常见问题

### Q: 为什么使用 `*` 还是不行？

A: 使用 `*` 时，`allow_credentials` 必须为 `False`。如果代码没有打补丁，`allow_credentials=True` 和 `allow_origins=["*"]` 会冲突。

### Q: 补丁脚本没有执行？

A: 检查 Dockerfile 中的补丁步骤是否在正确的阶段执行，确保在复制代码之后、安装依赖之前执行。

### Q: 环境变量设置了但没生效？

A: 确保：
1. 环境变量在 `docker-compose.1panel.yml` 中正确设置
2. 容器已重启以加载新环境变量
3. 检查容器内的环境变量：`docker exec cognee env | grep CORS`

## 推荐配置

### 开发环境

```yaml
- CORS_ALLOWED_ORIGINS=*
```

需要重新构建镜像应用补丁。

### 生产环境

```yaml
- CORS_ALLOWED_ORIGINS=http://yourdomain.com,https://yourdomain.com
```

不需要补丁，直接使用官方代码即可。

