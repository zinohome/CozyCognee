# Cognee MCP NVIDIA 依赖问题

## 问题

在 Direct Mode 构建 cognee-mcp 镜像时，会安装 NVIDIA/CUDA 相关的包，这是不必要的。

## 原因

Cognee 的基础依赖中包含了以下包，它们会触发 NVIDIA/CUDA 依赖的安装：

1. **onnxruntime<=1.22.1**
   - ONNX Runtime 默认会尝试安装 CUDA 版本
   - 包含 NVIDIA 驱动和 CUDA 库
   - 占用大量空间（数百 MB 到数 GB）

2. **fastembed<=0.6.0**
   - FastEmbed 可能依赖 PyTorch
   - PyTorch 可能包含 CUDA 支持
   - 也会安装 NVIDIA 相关依赖

## 为什么 MCP 服务器不需要这些？

- MCP 服务器主要作为协议转换层
- 实际的 AI 推理由 Cognee API 服务器处理（如果使用 API Mode）
- 或者在 Direct Mode 下，这些依赖也不是必需的（除非使用本地模型推理）
- 大多数部署环境没有 NVIDIA GPU

## 解决方案

### 方案 1：移除依赖（已实现）

在 Dockerfile 中，安装 cognee 之前移除这些依赖：

```dockerfile
# 移除 onnxruntime 和 fastembed（会安装 NVIDIA 包）
RUN sed -i '/onnxruntime/d' /app/cognee-pyproject.toml && \
    sed -i '/fastembed/d' /app/cognee-pyproject.toml
```

**优点**：
- ✅ 大幅减小镜像大小
- ✅ 减少构建时间
- ✅ 避免安装不必要的 NVIDIA 驱动

**缺点**：
- ⚠️ 如果 MCP 服务器需要使用本地模型推理，可能需要这些依赖
- ⚠️ 需要手动维护依赖列表

### 方案 2：使用 API Mode（推荐）

使用 `cognee-mcp:api-latest` 镜像：
- 只安装基础 cognee 包（不包含 onnxruntime, fastembed）
- 所有 AI 推理由 Cognee API 服务器处理
- 不需要本地模型推理能力

### 方案 3：条件安装

根据环境变量决定是否安装 NVIDIA 依赖：

```dockerfile
ARG INSTALL_NVIDIA_DEPS=false
RUN if [ "$INSTALL_NVIDIA_DEPS" = "false" ]; then \
    sed -i '/onnxruntime/d' /app/cognee-pyproject.toml && \
    sed -i '/fastembed/d' /app/cognee-pyproject.toml; \
fi
```

## 影响

### 移除前
- 镜像大小：~8.5GB
- 包含：NVIDIA 驱动、CUDA 库、ONNX Runtime（CUDA 版本）、PyTorch（可能）
- 构建时间：较长（需要下载和安装 NVIDIA 相关包）

### 移除后
- 镜像大小：~1.5-2GB
- 不包含：NVIDIA 相关依赖
- 构建时间：显著减少

## 注意事项

1. **如果确实需要 NVIDIA 支持**：
   - 使用官方 Dockerfile（不修改依赖）
   - 或者手动添加这些依赖

2. **功能影响**：
   - MCP 服务器的核心功能不受影响
   - 只有本地模型推理功能可能受影响（但通常不使用）

3. **API Mode**：
   - API Mode 下完全不需要这些依赖
   - 推荐使用 `cognee-mcp:api-latest` 镜像

## 总结

移除 `onnxruntime` 和 `fastembed` 是合理的优化：
- ✅ MCP 服务器不需要这些依赖
- ✅ 大幅减小镜像大小
- ✅ 减少构建时间
- ✅ 避免安装不必要的 NVIDIA 驱动

如果将来需要这些依赖，可以：
1. 使用官方 Dockerfile
2. 或者通过环境变量控制安装

