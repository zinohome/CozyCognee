# Cognee vs Cognee-MCP 镜像大小差异分析

## 问题

- **cognee 镜像**：只有 1.27GB
- **cognee-mcp 镜像**：8.5GB

为什么 cognee-mcp 镜像比 cognee 镜像大这么多？

## 根本原因

### 1. Cognee 镜像的构建方式

```dockerfile
# 1. 只安装依赖，不安装 cognee 包本身
RUN uv sync --frozen --no-install-project --no-dev --no-editable

# 2. 直接复制源代码
COPY project/cognee/cognee /app/cognee
COPY project/cognee/distributed /app/distributed

# 3. 安装 cognee 作为本地包（editable install）
RUN uv sync --frozen --no-dev --no-editable
```

**关键点**：
- ✅ cognee 是**源代码**，直接复制到镜像中
- ✅ 只安装**运行时依赖**（通过 `--extra` 指定）
- ✅ 不包含 PyPI 包的元数据、文档等额外内容
- ✅ 不包含未使用的依赖

### 2. Cognee-MCP 镜像的构建方式

```dockerfile
# 1. 复制 pyproject.toml（包含依赖声明）
COPY project/cognee/cognee-mcp/pyproject.toml ...

# 2. uv sync 会自动从 PyPI 下载并安装 cognee 包
RUN uv sync --frozen --no-install-project --no-dev --no-editable
```

**pyproject.toml 中的声明**：
```toml
dependencies = [
    "cognee[postgres,docs,neo4j]==0.3.7",  # ← 这里！
    ...
]
```

**关键点**：
- ❌ cognee 是**从 PyPI 下载的完整包**
- ❌ 包含所有 extras 的依赖：`postgres`, `docs`, `neo4j`
- ❌ 包含 PyPI 包的元数据、文档等
- ❌ 可能包含重复的依赖

## 详细对比

### Cognee 镜像（1.27GB）

**安装的内容**：
1. Python 基础镜像
2. cognee 源代码（直接复制）
3. 指定的 extras 依赖：
   - `postgres` (psycopg2, pgvector, asyncpg)
   - `neo4j` (neo4j 驱动)
   - `scraping` (playwright, beautifulsoup4, 等)
   - 其他指定的 extras

**不包含**：
- PyPI 包的元数据
- 未使用的依赖
- 重复的依赖

### Cognee-MCP 镜像（8.5GB）

**安装的内容**：
1. Python 基础镜像
2. **从 PyPI 下载的完整 cognee 包**（包含所有 extras）
3. `cognee[postgres,docs,neo4j]` 的所有依赖：
   - `postgres` extras: psycopg2, pgvector, asyncpg
   - `docs` extras: **unstructured 及其所有子依赖**（非常大！）
   - `neo4j` extras: neo4j 驱动
4. cognee-mcp 包本身
5. PyPI 包的元数据、文档等

**额外开销**：
- `docs` extra 中的 `unstructured` 包非常大，包含：
  - 文档处理库
  - PDF 处理库
  - Office 文档处理库
  - 图像处理库
  - 等等...

## 为什么 docs extra 这么大？

查看 `project/cognee/pyproject.toml`：

```toml
docs = [
    "lxml<6.0.0", 
    "unstructured[csv, doc, docx, epub, md, odt, org, ppt, pptx, rst, rtf, tsv, xlsx, pdf]>=0.18.1,<19"
]
```

`unstructured` 包包含：
- 多种文档格式支持（PDF, DOCX, PPTX, XLSX, 等）
- 图像处理库
- OCR 库
- 各种解析器
- 所有这些的依赖

**估计大小**：`unstructured` 及其依赖可能占用 **3-5GB**！

## 解决方案

### 方案 1：使用 API Mode（推荐）

使用轻量级 `cognee-mcp:api-latest` 镜像（~2-3GB）：
- 只安装基础 cognee 包（不包含 extras）
- 通过 HTTP 请求到 Cognee API 服务器
- 不需要本地处理文档、数据库等

### 方案 2：优化 Direct Mode 镜像

修改 `cognee-mcp` 的 Dockerfile，使用源代码而不是 PyPI 包：

```dockerfile
# 1. 只安装依赖，不安装 cognee 包
RUN uv sync --frozen --no-install-project --no-dev --no-editable

# 2. 复制 cognee 源代码（而不是从 PyPI 安装）
COPY project/cognee/cognee /app/cognee
COPY project/cognee/distributed /app/distributed

# 3. 安装 cognee-mcp 和 cognee（作为本地包）
RUN uv sync --frozen --no-dev --no-editable
```

**优点**：
- 镜像大小接近 cognee 镜像（~1.5-2GB）
- 不包含未使用的依赖
- 与 cognee 镜像构建方式一致

**缺点**：
- 需要访问 cognee 源代码（构建时）
- 需要确保 cognee 版本匹配

### 方案 3：移除不必要的 extras

如果不需要 `docs` extra，可以修改 `pyproject.toml`：

```toml
dependencies = [
    "cognee[postgres,neo4j]==0.3.7",  # 移除 docs
    ...
]
```

**估计减少**：3-5GB（移除 unstructured 相关依赖）

## 镜像大小估算

| 组件 | Cognee 镜像 | Cognee-MCP 镜像 |
|------|------------|----------------|
| Python 基础镜像 | ~200MB | ~200MB |
| cognee 源代码 | ~50MB | - |
| cognee PyPI 包 | - | ~100MB |
| 基础依赖 | ~300MB | ~300MB |
| postgres extras | ~50MB | ~50MB |
| neo4j extras | ~20MB | ~20MB |
| **docs extras** | **~0MB** | **~4-5GB** |
| 其他 extras | ~100MB | ~100MB |
| 重复依赖/元数据 | ~0MB | ~1-2GB |
| **总计** | **~1.27GB** | **~8.5GB** |

## 总结

**为什么 cognee-mcp 镜像这么大？**

1. **从 PyPI 安装完整包**：包含所有 extras 和元数据
2. **docs extra 非常大**：`unstructured` 包及其依赖占用 3-5GB
3. **重复依赖**：可能安装了一些重复的依赖
4. **PyPI 包开销**：包含元数据、文档等额外内容

**推荐解决方案**：
- ✅ **API Mode**：使用 `cognee-mcp:api-latest`（~2-3GB）
- ✅ **Direct Mode**：修改 Dockerfile 使用源代码而不是 PyPI 包

