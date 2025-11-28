# Cognee MCP Dockerfile 对比分析

## 问题：官方 Dockerfile 为什么没有显式安装 cognee？

## 答案：官方 Dockerfile **确实安装了 cognee**，只是通过 `uv sync` 自动安装的

## 详细分析

### 官方 Dockerfile 的工作流程

```dockerfile
# 1. 复制 pyproject.toml 和 uv.lock
COPY ./cognee-mcp/pyproject.toml ./cognee-mcp/uv.lock ./cognee-mcp/entrypoint.sh ./

# 2. 运行 uv sync（关键步骤）
RUN uv sync --frozen --no-install-project --no-dev --no-editable
```

**关键点**：
- `uv sync` 会根据 `pyproject.toml` 中的 `dependencies` 自动安装所有依赖
- `pyproject.toml` 第 12 行声明了：`"cognee[postgres,docs,neo4j]==0.3.7"`
- 所以 `uv sync` **会自动安装 cognee 及其所有 extras**

### pyproject.toml 中的依赖声明

```toml
dependencies = [
    "cognee[postgres,docs,neo4j]==0.3.7",  # ← 这里声明了 cognee
    "fastmcp>=2.10.0,<3.0.0",
    "mcp>=1.12.0,<2.0.0",
    "uv>=0.6.3,<1.0.0",
    "httpx>=0.27.0,<1.0.0",
]
```

### 为什么看起来"没有安装"？

1. **没有显式的 `pip install cognee` 或 `uv pip install cognee`**
2. **依赖是通过 `uv sync` 自动解析和安装的**
3. **这是 uv 的标准工作方式**：读取 `pyproject.toml` → 解析依赖 → 安装所有依赖

### 官方 Dockerfile 的完整流程

```
1. 复制 pyproject.toml + uv.lock
   ↓
2. uv sync --frozen --no-install-project
   → 读取 pyproject.toml
   → 解析依赖（包括 cognee[postgres,docs,neo4j]）
   → 安装所有依赖到虚拟环境
   ↓
3. 复制源代码
   ↓
4. uv sync --frozen --no-dev --no-editable
   → 安装项目本身（cognee-mcp）
   → 依赖已经在步骤 2 中安装好了
```

## 我们的 Dockerfile.api 的问题

### 当前实现

```dockerfile
# 手动安装依赖
RUN uv pip install --system --no-cache \
    "cognee==0.3.7" \
    "fastmcp>=2.10.0,<3.0.0" \
    "mcp>=1.12.0,<2.0.0" \
    "httpx>=0.27.0,<1.0.0"
```

### 问题

1. **没有使用 pyproject.toml**：失去了依赖管理的优势
2. **手动管理依赖**：容易出错，需要手动维护版本
3. **没有使用 uv.lock**：无法保证依赖版本的一致性

## 改进方案

### 方案 1：创建轻量级 pyproject.toml（推荐）

创建一个专门用于 API Mode 的 `pyproject.toml.api`：

```toml
[project]
name = "cognee-mcp-api"
version = "0.4.0"
requires-python = ">=3.10"
dependencies = [
    # 只安装基础 cognee 包，不安装 extras
    "cognee==0.3.7",  # 不包含 [postgres,docs,neo4j]
    "fastmcp>=2.10.0,<3.0.0",
    "mcp>=1.12.0,<2.0.0",
    "httpx>=0.27.0,<1.0.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project.scripts]
cognee-mcp = "src:main_mcp"
```

然后在 Dockerfile 中使用：

```dockerfile
# 复制轻量级 pyproject.toml
COPY project/cognee/cognee-mcp/pyproject.toml.api ./pyproject.toml

# 使用 uv sync 安装依赖（自动处理依赖解析）
RUN uv sync --frozen --no-install-project --no-dev --no-editable
```

### 方案 2：使用构建参数

```dockerfile
ARG MCP_MODE=full
# MCP_MODE=api 时只安装基础依赖
# MCP_MODE=full 时安装完整依赖

# 根据模式选择不同的 pyproject.toml
COPY project/cognee/cognee-mcp/pyproject.toml${MCP_MODE:+.${MCP_MODE}} ./pyproject.toml
```

## 对比总结

| 特性 | 官方 Dockerfile | 我们的 Dockerfile.api |
|------|----------------|----------------------|
| 依赖管理 | ✅ 使用 pyproject.toml + uv sync | ❌ 手动 pip install |
| 版本锁定 | ✅ 使用 uv.lock | ❌ 无版本锁定 |
| 依赖解析 | ✅ 自动解析依赖树 | ❌ 手动管理 |
| 镜像大小 | ❌ ~8.5GB（完整依赖） | ✅ ~2-3GB（最小依赖） |
| 维护性 | ✅ 高（标准方式） | ⚠️ 低（需要手动维护） |

## 推荐方案

**最佳实践**：创建 `pyproject.toml.api`，使用 `uv sync` 安装依赖

**优点**：
- ✅ 遵循官方标准做法
- ✅ 自动依赖解析
- ✅ 版本锁定支持
- ✅ 易于维护
- ✅ 镜像体积小

**实现步骤**：
1. 创建 `project/cognee/cognee-mcp/pyproject.toml.api`
2. 修改 `Dockerfile.api` 使用 `uv sync` 而不是手动 `pip install`
3. 保持与官方 Dockerfile 相同的构建流程

