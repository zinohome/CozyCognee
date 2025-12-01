# 使用文档

本文档介绍 CozyCognee 的使用方法和最佳实践。

## 目录

- [快速开始](#快速开始)
- [支持的文件格式](./SUPPORTED_FILE_FORMATS.md)
- [API 使用](#api-使用)
- [前端使用](#前端使用)
- [MCP 集成](#mcp-集成)
- [最佳实践](#最佳实践)
- [常见用例](#常见用例)

## 快速开始

### 启动服务

```bash
cd deployment
docker-compose up -d cognee
```

### 验证安装

```bash
# 检查服务状态
curl http://localhost:8000/health

# 查看 API 文档
open http://localhost:8000/docs
```

## 支持的文件格式

Cognee 支持多种文件格式，包括文本、PDF、Office 文档、图片、音频等。

**详细说明**：
- [CozyCognee 实际支持的文件格式](./SUPPORTED_FILE_FORMATS_COZYCOGNEE.md) - **推荐查看**（基于我们当前的 Docker 配置）
- [完整支持的文件格式列表](./SUPPORTED_FILE_FORMATS.md) - 包含所有可能的文件格式（需要完整安装）
- [文件大小限制](./FILE_SIZE_LIMITS.md) - 文件上传和处理的大小限制说明

**快速参考**：
- ✅ **文本文件**：`.txt`, `.md`, `.csv`, `.json`, `.xml`, `.yaml`, `.log`
- ✅ **PDF 文件**：`.pdf`
- ✅ **Office 文档**：`.docx`, `.doc`, `.xlsx`, `.xls`, `.pptx`, `.ppt`, `.rtf`
- ✅ **图片文件**：`.png`, `.jpg`, `.jpeg`, `.gif`, `.webp`, `.tif`, `.bmp` 等
- ✅ **音频文件**：`.mp3`, `.wav`, `.m4a`, `.ogg`, `.flac` 等
- ✅ **HTML 文件**：`.html`, `.htm`
- ✅ **代码文件**：`.py`, `.js`, `.ts`, `.java`, `.cpp` 等（作为文本处理）

**重要**：所有能够成功通过 `add()` 上传的文件，都可以正常进行 `cognify` 和 `memify` 操作。

## API 使用

### Python SDK

```python
import cognee

# 初始化
await cognee.prune()

# 添加数据
await cognee.add(
    data="Your text data here",
    data_id="unique-id",
    dataset_id="my-dataset"
)

# 处理数据
await cognee.cognify(datasets=["my-dataset"])

# 搜索
results = await cognee.search(
    "your query",
    query_type=cognee.SearchType.GRAPH_COMPLETION
)
```

### REST API

```bash
# 添加数据
curl -X POST http://localhost:8000/api/v1/add \
  -H "Content-Type: application/json" \
  -d '{
    "data": "Your text data",
    "data_id": "unique-id",
    "dataset_id": "my-dataset"
  }'

# 搜索
curl -X POST http://localhost:8000/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "your query",
    "query_type": "GRAPH_COMPLETION"
  }'
```

## 前端使用

### 启动前端

```bash
docker-compose --profile ui up -d frontend
```

访问：http://localhost:3000

### 功能说明

- **数据管理**: 添加和管理数据集
- **知识图谱可视化**: 查看知识图谱结构
- **搜索**: 执行语义搜索
- **配置**: 管理系统配置

## MCP 集成

### 启动 MCP 服务

```bash
docker-compose --profile mcp up -d cognee-mcp
```

### 配置 Cursor/Claude Desktop

在 Cursor 或 Claude Desktop 中配置 MCP 服务器：

```json
{
  "mcpServers": {
    "cognee": {
      "command": "curl",
      "args": [
        "http://localhost:8001"
      ],
      "transport": "sse"
    }
  }
}
```

### MCP 工具

- `cognee_add`: 添加数据到 Cognee
- `cognee_search`: 搜索知识图谱
- `cognee_cognify`: 处理数据生成知识图谱
- `cognee_visualize`: 可视化知识图谱

## 最佳实践

### 数据组织

1. **使用数据集**: 将相关数据组织到数据集中
2. **唯一标识**: 为每个数据项使用唯一的 `data_id`
3. **批量处理**: 对于大量数据，使用批量添加

```python
# 批量添加数据
data_list = [
    {"data": "text1", "data_id": "id1"},
    {"data": "text2", "data_id": "id2"},
]

for item in data_list:
    await cognee.add(
        data=item["data"],
        data_id=item["data_id"],
        dataset_id="my-dataset"
    )
```

### 性能优化

1. **异步处理**: 使用 `run_in_background=True` 处理大型数据集

```python
await cognee.cognify(
    datasets=["large-dataset"],
    run_in_background=True
)
```

2. **增量加载**: 启用增量加载避免重复处理

```python
await cognee.cognify(
    datasets=["my-dataset"],
    incremental_loading=True
)
```

3. **资源限制**: 根据数据量调整批处理大小

```python
await cognee.cognify(
    datasets=["my-dataset"],
    chunks_per_batch=10,
    data_per_batch=20
)
```

### 数据库选择

- **SQLite**: 适合开发和测试，无需额外配置
- **PostgreSQL**: 适合生产环境，支持并发访问
- **Neo4j**: 适合复杂图查询和分析
- **ChromaDB**: 轻量级向量数据库，适合小到中型项目

## 常见用例

### 用例 1: 文档知识库

```python
import cognee

# 添加文档
await cognee.add(
    data=open("document.pdf", "rb").read(),
    data_id="doc-1",
    dataset_id="documents"
)

# 处理文档
await cognee.cognify(datasets=["documents"])

# 查询文档
results = await cognee.search(
    "What is the main topic?",
    query_type=cognee.SearchType.GRAPH_COMPLETION
)
```

### 用例 2: 代码库分析

```python
# 添加代码库
await cognee.add(
    data=codebase_text,
    data_id="codebase-1",
    dataset_id="code"
)

# 使用代码特定的图模型
from cognee.modules.graph.models import CodeGraph

await cognee.cognify(
    datasets=["code"],
    graph_model=CodeGraph
)
```

### 用例 3: 对话记忆

```python
# 添加对话历史
await cognee.add(
    data=conversation_history,
    data_id="conv-1",
    dataset_id="conversations"
)

# 处理对话
await cognee.memify(datasets=["conversations"])

# 检索相关对话
results = await cognee.search(
    "previous discussion about X",
    query_type=cognee.SearchType.CHUNKS
)
```

## 配置建议

### 开发环境

```env
DEBUG=true
ENVIRONMENT=local
LOG_LEVEL=DEBUG
DB_PROVIDER=sqlite
```

### 生产环境

```env
DEBUG=false
ENVIRONMENT=production
LOG_LEVEL=ERROR
DB_PROVIDER=postgres
VECTOR_DB_PROVIDER=chroma
GRAPH_DATABASE_PROVIDER=neo4j
```

## 监控和维护

### 健康检查

```bash
# API 健康检查
curl http://localhost:8000/health

# 检查服务状态
docker-compose ps
```

### 日志查看

```bash
# 查看实时日志
docker-compose logs -f cognee

# 查看错误日志
docker-compose logs cognee | grep ERROR
```

### 数据备份

定期备份重要数据：

```bash
# 备份数据库
docker-compose exec postgres pg_dump -U cognee cognee_db > backup.sql

# 备份向量数据库数据
docker cp chromadb:/chroma/chroma ./backup/chromadb
```

## 故障排查

### API 无响应

1. 检查服务是否运行：`docker-compose ps`
2. 查看日志：`docker-compose logs cognee`
3. 检查端口占用：`netstat -tulpn | grep 8000`

### 搜索无结果

1. 确认数据已添加：检查数据集
2. 确认已执行 cognify：处理数据生成知识图谱
3. 检查向量数据库连接

### 性能问题

1. 调整批处理大小
2. 使用后台处理模式
3. 优化数据库配置
4. 增加资源限制

## 更多资源

- [Cognee 官方文档](https://docs.cognee.ai)
- [API 参考](http://localhost:8000/docs)
- [示例代码](../project/cognee/examples/)

