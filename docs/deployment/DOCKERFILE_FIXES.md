# Dockerfile 修复说明

## 修复内容

### 1. Dockerfile.api（API Mode 轻量级镜像）

**修复的问题**：
- 移除了 `--frozen` 标志，因为 `pyproject.toml.api` 没有对应的 `uv.lock` 文件
- 确保路径正确：`pyproject.toml.api` 放在 `deployment/docker/cognee-mcp/` 目录下（不在官方代码目录）

**构建命令**：
```bash
# 从项目根目录执行
docker build -f deployment/docker/cognee-mcp/Dockerfile.api -t cognee-mcp:api-latest .
```

**预期镜像大小**：~2-3GB（不包含 docs extra）

### 2. Dockerfile（Direct Mode 优化镜像）

**优化内容**：
- 使用本地 cognee 源代码而不是从 PyPI 安装
- 移除 docs extra（unstructured 包占用 3-5GB）
- **移除 NVIDIA 相关依赖**（onnxruntime, fastembed）- 这些包会安装 CUDA/NVIDIA 驱动，但 MCP 服务器不需要
- 只安装必要的 extras（postgres, neo4j）

**关键优化**：
```dockerfile
# 1. 先复制 cognee 源代码
COPY project/cognee/cognee /app/cognee
COPY project/cognee/distributed /app/distributed
COPY project/cognee/pyproject.toml /app/cognee-pyproject.toml

# 2. 移除不必要的依赖（onnxruntime, fastembed 会安装 NVIDIA 包）
RUN sed -i '/onnxruntime/d' /app/cognee-pyproject.toml && \
    sed -i '/fastembed/d' /app/cognee-pyproject.toml

# 3. 修改 pyproject.toml 使用本地路径，移除 docs extra
RUN sed -i 's|"cognee\[postgres,docs,neo4j\]==0.3.7"|"cognee[postgres,neo4j] @ file:///app"|' pyproject.toml
```

**为什么移除 onnxruntime 和 fastembed？**
- `onnxruntime`：ONNX Runtime 默认会尝试安装 CUDA 版本，包含 NVIDIA 驱动
- `fastembed`：FastEmbed 可能依赖 PyTorch，而 PyTorch 可能包含 CUDA 支持
- MCP 服务器在 Direct Mode 下不需要这些依赖，它们会：
  - 大幅增加镜像大小（NVIDIA 驱动和相关库）
  - 增加构建时间
  - 在非 NVIDIA GPU 环境中完全无用

**预期镜像大小**：~1.5-2GB（从 8.5GB 减少，且不包含 NVIDIA 相关包）

## 构建说明

### 构建 API Mode 镜像

```bash
cd /Users/zhangjun/CursorProjects/CozyCognee
docker build -f deployment/docker/cognee-mcp/Dockerfile.api -t cognee-mcp:api-latest .
```

### 构建 Direct Mode 镜像

```bash
cd /Users/zhangjun/CursorProjects/CozyCognee
docker build -f deployment/docker/cognee-mcp/Dockerfile -t cognee-mcp:latest .
```

### 使用构建脚本

```bash
cd deployment
./scripts/build-image.sh cognee-mcp-api  # API Mode
./scripts/build-image.sh cognee-mcp      # Direct Mode
```

## 注意事项

1. **构建上下文**：必须从项目根目录执行构建命令（最后的 `.` 表示当前目录）
2. **文件路径**：Dockerfile 中的路径是相对于构建上下文的
3. **uv.lock**：API Mode 不使用 lock 文件，Direct Mode 使用原始的 uv.lock

## 镜像大小对比

| 镜像 | 大小 | 说明 |
|------|------|------|
| cognee-mcp:latest (优化前) | ~8.5GB | 从 PyPI 安装，包含 docs extra |
| cognee-mcp:latest (优化后) | ~1.5-2GB | 使用源代码，移除 docs extra |
| cognee-mcp:api-latest | ~2-3GB | 只安装基础包，不包含 extras |

