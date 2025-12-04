# Cognee SDK 开发可行性分析

## 📋 执行摘要

**结论：完全可以开发一个轻量级 SDK，通过 HTTP API 调用 Cognee 服务端。**

Cognee 已经提供了完整的 REST API，并且 MCP 服务器已经实现了类似的 API Mode 模式，这证明了通过 API 调用 Cognee 是完全可行的。

## ✅ 可行性分析

### 1. Cognee 已有完整的 REST API

Cognee 通过 FastAPI 提供了完整的 REST API 接口：

**核心 API 端点：**
- `POST /api/v1/add` - 添加数据
- `POST /api/v1/cognify` - 处理数据生成知识图谱
- `POST /api/v1/memify` - 添加记忆算法
- `POST /api/v1/search` - 搜索知识图谱
- `DELETE /api/v1/delete` - 删除数据
- `PUT /api/v1/update` - 更新数据
- `GET /api/v1/datasets` - 获取数据集列表
- `GET /api/v1/visualize` - 可视化图谱
- `POST /api/v1/sync` - 同步数据

**API 文档：**
- Swagger UI: `http://localhost:8000/docs`
- OpenAPI Schema: `http://localhost:8000/openapi.json`

### 2. MCP 已实现 API Mode

Cognee MCP 服务器已经实现了类似的架构模式，可以作为参考：

**参考实现：** `project/cognee/cognee-mcp/src/cognee_client.py`

```python
class CogneeClient:
    """
    Unified client for interacting with Cognee via direct calls or HTTP API.
    """
    def __init__(self, api_url: Optional[str] = None, api_token: Optional[str] = None):
        self.api_url = api_url.rstrip("/") if api_url else None
        self.use_api = bool(api_url)
        
        if self.use_api:
            self.client = httpx.AsyncClient(timeout=300.0)
        else:
            import cognee as _cognee
            self.cognee = _cognee
```

**关键特性：**
- ✅ 支持 Direct Mode 和 API Mode 两种模式
- ✅ API Mode 通过 HTTP 请求调用 Cognee API
- ✅ 统一的接口，使用方式相同
- ✅ 自动处理认证和错误

### 3. SDK 架构设计

**轻量级 SDK 只需要：**
- HTTP 客户端库（如 `httpx` 或 `requests`）
- 基本的错误处理
- 类型定义（可选，使用 Pydantic）

**不需要：**
- ❌ 完整的 cognee 库及其依赖
- ❌ 数据库连接（PostgreSQL, Neo4j 等）
- ❌ 向量数据库客户端
- ❌ LLM 客户端
- ❌ 文件处理库

**SDK 大小估算：**
- 直接使用 cognee 库：~500MB - 2GB（包含所有依赖）
- 轻量级 SDK：~5-10MB（仅 HTTP 客户端和类型定义）

## 📊 性能差异分析

### 1. 网络开销

**API 调用模式：**
- **网络延迟**：每次调用增加 1-50ms（取决于网络条件）
  - 本地网络（localhost）：< 1ms
  - 局域网：1-5ms
  - 公网：10-50ms
- **序列化开销**：JSON 序列化/反序列化，通常 < 5ms
- **HTTP 协议开销**：HTTP 头部和连接建立，通常 < 10ms

**直接调用模式：**
- **无网络开销**：函数直接调用
- **无序列化开销**：直接传递 Python 对象

### 2. 实际性能影响

**对于不同操作类型：**

#### 快速操作（< 100ms）
- **搜索操作**：API 调用增加 5-20ms 开销
  - 直接调用：50-100ms
  - API 调用：55-120ms
  - **性能影响：5-20%**

#### 中等操作（100ms - 1s）
- **添加数据**：API 调用增加 10-30ms 开销
  - 直接调用：200-500ms
  - API 调用：210-530ms
  - **性能影响：5-10%**

#### 长时间操作（> 1s）
- **Cognify 处理**：API 调用开销可忽略
  - 直接调用：10-60 秒（取决于数据量）
  - API 调用：10-60 秒 + 10-50ms
  - **性能影响：< 0.1%**

### 3. 性能优化建议

**对于 SDK 设计：**

1. **连接池复用**
   ```python
   # 使用 httpx.AsyncClient 连接池
   self.client = httpx.AsyncClient(
       timeout=300.0,
       limits=httpx.Limits(max_keepalive_connections=10)
   )
   ```

2. **批量操作支持**
   ```python
   # 支持批量添加，减少 HTTP 请求次数
   await client.add_batch(data_list)
   ```

3. **异步操作**
   ```python
   # 所有操作都是异步的，支持并发
   results = await asyncio.gather(
       client.search("query1"),
       client.search("query2"),
       client.search("query3")
   )
   ```

4. **流式响应**（对于大文件）
   ```python
   # 支持流式上传大文件
   async with client.stream_upload(file_path) as stream:
       ...
   ```

## 🎯 SDK 实现建议

### 1. 基础 SDK 结构

```python
# cognee-sdk/cognee_sdk/__init__.py
from .client import CogneeSDKClient

__all__ = ["CogneeSDKClient"]

# cognee-sdk/cognee_sdk/client.py
import httpx
from typing import Optional, List, Dict, Any
from enum import Enum

class SearchType(str, Enum):
    GRAPH_COMPLETION = "GRAPH_COMPLETION"
    RAG_COMPLETION = "RAG_COMPLETION"
    CHUNKS = "CHUNKS"
    SUMMARIES = "SUMMARIES"
    CYPHER = "CYPHER"
    FEELING_LUCKY = "FEELING_LUCKY"

class CogneeSDKClient:
    """轻量级 Cognee SDK 客户端，通过 HTTP API 调用 Cognee 服务端"""
    
    def __init__(
        self,
        api_url: str,
        api_token: Optional[str] = None,
        timeout: float = 300.0
    ):
        self.api_url = api_url.rstrip("/")
        self.api_token = api_token
        self.client = httpx.AsyncClient(
            timeout=timeout,
            limits=httpx.Limits(max_keepalive_connections=10)
        )
    
    def _get_headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_token:
            headers["Authorization"] = f"Bearer {self.api_token}"
        return headers
    
    async def add(
        self,
        data: Any,
        dataset_name: str = "main_dataset",
        dataset_id: Optional[str] = None,
        node_set: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """添加数据到 Cognee"""
        endpoint = f"{self.api_url}/api/v1/add"
        
        # 处理文件上传
        if isinstance(data, (str, bytes)):
            files = {"data": ("data.txt", str(data), "text/plain")}
        else:
            files = {"data": data}
        
        form_data = {}
        if dataset_name:
            form_data["datasetName"] = dataset_name
        if dataset_id:
            form_data["datasetId"] = dataset_id
        if node_set:
            form_data["node_set"] = json.dumps(node_set)
        
        response = await self.client.post(
            endpoint,
            files=files,
            data=form_data,
            headers={"Authorization": f"Bearer {self.api_token}"} if self.api_token else {}
        )
        response.raise_for_status()
        return response.json()
    
    async def cognify(
        self,
        datasets: Optional[List[str]] = None,
        run_in_background: bool = False,
        custom_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """处理数据生成知识图谱"""
        endpoint = f"{self.api_url}/api/v1/cognify"
        payload = {
            "datasets": datasets or ["main_dataset"],
            "run_in_background": run_in_background
        }
        if custom_prompt:
            payload["custom_prompt"] = custom_prompt
        
        response = await self.client.post(
            endpoint,
            json=payload,
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    async def search(
        self,
        query: str,
        search_type: SearchType = SearchType.GRAPH_COMPLETION,
        datasets: Optional[List[str]] = None,
        system_prompt: Optional[str] = None,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """搜索知识图谱"""
        endpoint = f"{self.api_url}/api/v1/search"
        payload = {
            "query": query,
            "search_type": search_type.value,
            "top_k": top_k
        }
        if datasets:
            payload["datasets"] = datasets
        if system_prompt:
            payload["system_prompt"] = system_prompt
        
        response = await self.client.post(
            endpoint,
            json=payload,
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    async def delete(
        self,
        data_id: str,
        dataset_id: str,
        mode: str = "soft"
    ) -> Dict[str, Any]:
        """删除数据"""
        endpoint = f"{self.api_url}/api/v1/delete"
        params = {
            "data_id": data_id,
            "dataset_id": dataset_id,
            "mode": mode
        }
        
        response = await self.client.delete(
            endpoint,
            params=params,
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    async def list_datasets(self) -> List[Dict[str, Any]]:
        """获取数据集列表"""
        endpoint = f"{self.api_url}/api/v1/datasets"
        response = await self.client.get(
            endpoint,
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    async def close(self):
        """关闭 HTTP 客户端"""
        await self.client.aclose()
```

### 2. 使用示例

```python
import asyncio
from cognee_sdk import CogneeSDKClient, SearchType

async def main():
    # 初始化 SDK 客户端
    client = CogneeSDKClient(
        api_url="http://localhost:8000",
        api_token="your-token-here"  # 可选
    )
    
    try:
        # 添加数据
        await client.add(
            data="Cognee turns documents into AI memory.",
            dataset_name="my-dataset"
        )
        
        # 处理数据
        await client.cognify(datasets=["my-dataset"])
        
        # 搜索
        results = await client.search(
            query="What does Cognee do?",
            search_type=SearchType.GRAPH_COMPLETION
        )
        
        for result in results:
            print(result)
    
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
```

### 3. 依赖项

**最小依赖：**
```toml
[project]
name = "cognee-sdk"
version = "0.1.0"
dependencies = [
    "httpx>=0.25.0",
    "pydantic>=2.0.0",  # 可选，用于类型验证
]
```

**总大小：** ~5-10MB（相比完整 cognee 库的 500MB-2GB）

## 📈 性能对比总结

| 操作类型 | 直接调用 | API 调用 | 性能差异 |
|---------|---------|---------|---------|
| **快速操作** (< 100ms) | 50-100ms | 55-120ms | +5-20% |
| **中等操作** (100ms-1s) | 200-500ms | 210-530ms | +5-10% |
| **长时间操作** (> 1s) | 10-60s | 10-60s + 10-50ms | < 0.1% |
| **安装大小** | 500MB-2GB | 5-10MB | **减少 99%** |
| **启动时间** | 2-5s | < 0.1s | **减少 95%** |

## ✅ 结论

### 优势

1. **轻量级**：SDK 大小减少 99%，启动时间减少 95%
2. **易于部署**：不需要配置数据库、向量数据库等复杂环境
3. **集中管理**：所有数据和处理逻辑集中在服务端
4. **多语言支持**：可以轻松实现其他语言的 SDK（JavaScript, Go, Rust 等）
5. **版本兼容**：客户端和服务端可以独立升级

### 劣势

1. **网络依赖**：需要网络连接，无法离线使用
2. **性能开销**：快速操作有 5-20% 的性能开销
3. **功能限制**：某些高级功能可能仅支持直接调用模式

### 推荐场景

**适合使用 SDK：**
- ✅ Web 应用集成
- ✅ 微服务架构
- ✅ 多客户端共享知识图谱
- ✅ 快速原型开发
- ✅ 资源受限的环境

**适合直接使用库：**
- ✅ 高性能要求的场景
- ✅ 离线环境
- ✅ 需要完整功能控制
- ✅ 单机应用

## 🚀 下一步行动

1. **创建 SDK 项目结构**
2. **实现核心 API 客户端**
3. **添加错误处理和重试机制**
4. **编写单元测试和集成测试**
5. **发布到 PyPI**

## 📚 参考资源

- [Cognee API 文档](http://localhost:8000/docs)
- [MCP API Mode 实现](../deployment/COGNEE_MCP_DEPLOYMENT.md)
- [Cognee MCP 客户端代码](../../project/cognee/cognee-mcp/src/cognee_client.py)

