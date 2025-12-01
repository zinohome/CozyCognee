# CozyCognee 文件大小限制

本文档说明 CozyCognee 中文件上传和处理的大小限制。

## 📋 限制概览

### 当前配置的限制

| 组件 | 限制 | 配置文件 | 说明 |
|------|------|----------|------|
| **Nginx** | 100 MB | `deployment/nginx/nginx.conf` | `client_max_body_size 100M;` |
| **Caddy** | 100 MB | `deployment/caddy/Caddyfile` | `max_size 100MB` |
| **FastAPI/Uvicorn** | 无硬限制 | - | 受内存限制 |
| **Gunicorn Timeout** | 300 秒（生产） | `deployment/docker/cognee/entrypoint.sh` | 处理超时时间 |
| **Gunicorn Timeout** | 30 秒（开发） | `deployment/docker/cognee/entrypoint.sh` | 处理超时时间 |

## 🔍 详细说明

### 1. 反向代理限制（最重要）

#### Nginx 配置

**文件位置**：`deployment/nginx/nginx.conf`

```nginx
# 客户端请求体大小限制
client_max_body_size 100M;
```

**说明**：
- 这是**最严格的限制**
- 如果文件超过 100MB，Nginx 会直接拒绝请求，返回 `413 Request Entity Too Large` 错误
- 这是**全局限制**，适用于所有通过 Nginx 的请求

#### Caddy 配置

**文件位置**：`deployment/caddy/Caddyfile`

```caddy
request_body {
    max_size 100MB
}
```

**说明**：
- 与 Nginx 相同，限制为 100MB
- 如果文件超过 100MB，Caddy 会拒绝请求

### 2. FastAPI/Uvicorn 限制

**默认行为**：
- FastAPI 和 Uvicorn **没有硬编码的文件大小限制**
- 文件大小受以下因素影响：
  - **可用内存**：文件会被加载到内存中处理
  - **系统资源**：CPU、内存、磁盘 I/O

**实际限制**：
- 理论上可以处理任意大小的文件（受内存限制）
- 但实际使用中，建议：
  - **小文件（< 10MB）**：直接处理
  - **中等文件（10-100MB）**：可以处理，但处理时间可能较长
  - **大文件（> 100MB）**：可能遇到内存问题

### 3. Gunicorn 超时限制

**文件位置**：`deployment/docker/cognee/entrypoint.sh`

#### 生产环境

```bash
gunicorn -w 1 -k uvicorn.workers.UvicornWorker \
    --timeout 300 \  # 5 分钟超时
    --graceful-timeout 30 \
    ...
```

**说明**：
- `--timeout 300`：如果请求处理时间超过 300 秒（5 分钟），worker 会被杀死
- 大文件处理可能需要更长时间，可能需要增加超时时间

#### 开发环境

```bash
gunicorn -w 1 -k uvicorn.workers.UvicornWorker \
    -t 30000 \  # 30 秒超时
    ...
```

**说明**：
- 开发环境超时时间较短（30 秒）
- 不适合处理大文件

### 4. 内存限制

**Docker 容器限制**：
- 默认情况下，Docker 容器没有内存限制
- 但实际可用内存受主机系统限制

**建议**：
- 确保有足够的内存来处理文件
- 大文件处理时，建议监控内存使用情况

## ⚙️ 如何修改限制

### 方法 1：增加 Nginx 文件大小限制

**文件**：`deployment/nginx/nginx.conf`

```nginx
# 修改为 500MB
client_max_body_size 500M;
```

**注意**：
- 修改后需要重启 Nginx 容器
- 确保有足够的内存和磁盘空间

### 方法 2：增加 Caddy 文件大小限制

**文件**：`deployment/caddy/Caddyfile`

```caddy
request_body {
    max_size 500MB
}
```

**注意**：
- 修改后需要重启 Caddy 容器

### 方法 3：增加 Gunicorn 超时时间

**文件**：`deployment/docker/cognee/entrypoint.sh`

```bash
# 生产环境：增加到 10 分钟
gunicorn -w 1 -k uvicorn.workers.UvicornWorker \
    --timeout 600 \  # 10 分钟
    ...
```

**注意**：
- 需要重新构建镜像或修改 entrypoint.sh
- 超时时间过长可能导致资源占用问题

### 方法 4：直接访问后端（绕过反向代理）

如果文件超过反向代理限制，可以：

1. **直接访问后端 API**：
   ```bash
   curl -X POST http://cognee:8000/api/v1/add \
     -F "data=@large_file.pdf"
   ```

2. **使用内部网络**：
   - 在 Docker 网络内部访问，绕过反向代理限制

**注意**：
- 这需要从容器内部或同一网络访问
- 不适用于外部用户

## 📊 不同文件类型的实际限制

### 文本文件（.txt, .md, .csv, .json）

- **推荐大小**：< 50MB
- **最大大小**：100MB（受反向代理限制）
- **处理时间**：取决于文件大小和内容复杂度

### PDF 文件（.pdf）

- **推荐大小**：< 50MB
- **最大大小**：100MB（受反向代理限制）
- **处理时间**：
  - 小文件（< 10MB）：几秒到几十秒
  - 中等文件（10-50MB）：几分钟
  - 大文件（50-100MB）：可能需要 5-10 分钟

### 图片文件（.png, .jpg, .jpeg）

- **推荐大小**：< 20MB
- **最大大小**：100MB（受反向代理限制）
- **处理时间**：
  - 取决于图片分辨率和 LLM 处理速度
  - 通常需要 10-60 秒

### 音频文件（.mp3, .wav）

- **推荐大小**：< 50MB
- **最大大小**：100MB（受反向代理限制）
- **处理时间**：
  - 取决于音频长度和 LLM 转录速度
  - 通常需要几分钟到十几分钟

### HTML 文件（.html）

- **推荐大小**：< 10MB
- **最大大小**：100MB（受反向代理限制）
- **处理时间**：取决于 HTML 复杂度和内容量

## ⚠️ 注意事项

### 1. 内存使用

- 大文件会占用大量内存
- 建议监控内存使用情况
- 如果内存不足，可能导致处理失败或系统不稳定

### 2. 处理时间

- 大文件处理时间可能很长
- 建议使用后台处理模式（`run_in_background=True`）
- 监控处理进度

### 3. 网络传输

- 大文件上传需要稳定的网络连接
- 建议使用断点续传或分块上传（如果支持）

### 4. 存储空间

- 确保有足够的磁盘空间存储文件
- 文件会被存储在 `data_root_directory` 配置的目录中

## 🔧 最佳实践

### 1. 文件大小建议

- **小文件（< 10MB）**：直接上传和处理
- **中等文件（10-50MB）**：可以处理，但建议使用后台模式
- **大文件（50-100MB）**：需要增加超时时间，使用后台模式
- **超大文件（> 100MB）**：需要修改配置或分块处理

### 2. 处理大文件的建议

```python
# 使用后台处理模式
await cognee.add(
    data="large_file.pdf",
    dataset_name="my_dataset"
)

# 使用后台模式处理
await cognee.cognify(
    datasets=["my_dataset"],
    run_in_background=True  # 后台处理，避免超时
)
```

### 3. 监控和日志

- 监控内存使用情况
- 查看处理日志
- 检查错误信息

### 4. 错误处理

如果遇到文件大小限制错误：

1. **413 Request Entity Too Large**：
   - 文件超过反向代理限制（100MB）
   - 需要修改 Nginx/Caddy 配置

2. **504 Gateway Timeout**：
   - 处理时间超过超时限制
   - 需要增加 Gunicorn 超时时间或使用后台模式

3. **内存不足错误**：
   - 文件太大，内存不足
   - 需要增加容器内存限制或使用分块处理

## 📚 相关文档

- [支持的文件格式](./SUPPORTED_FILE_FORMATS_COZYCOGNEE.md)
- [API 使用指南](./README.md)
- [部署文档](../deployment/README.md)

