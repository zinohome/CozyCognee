# Cognee Python SDK API 文档

## CogneeClient

主客户端类，用于与 Cognee API 服务器交互。

### 初始化

```python
client = CogneeClient(
    api_url="http://localhost:8000",
    api_token="your-token",  # 可选
    timeout=300.0,           # 请求超时（秒）
    max_retries=3,           # 最大重试次数
    retry_delay=1.0          # 初始重试延迟（秒）
)
```

### 核心方法

#### add()

添加数据到 Cognee。

```python
result = await client.add(
    data="文本内容",
    dataset_name="数据集名称",
    dataset_id=None,  # 可选
    node_set=None     # 可选
)
```

**支持的数据类型：**
- 字符串
- 字节数据
- 文件路径（Path 对象或字符串）
- 文件对象（BinaryIO）
- 上述类型的列表

#### delete()

删除数据。

```python
result = await client.delete(
    data_id=UUID("..."),
    dataset_id=UUID("..."),
    mode="soft"  # 或 "hard"
)
```

#### cognify()

处理数据生成知识图谱。

```python
result = await client.cognify(
    datasets=["dataset1"],
    dataset_ids=None,  # 可选
    run_in_background=False,
    custom_prompt=None  # 可选
)
```

#### search()

搜索知识图谱。

```python
results = await client.search(
    query="搜索查询",
    search_type=SearchType.GRAPH_COMPLETION,
    datasets=None,  # 可选
    dataset_ids=None,  # 可选
    system_prompt=None,  # 可选
    node_name=None,  # 可选
    top_k=10,
    only_context=False,
    use_combined_context=False
)
```

#### list_datasets()

获取数据集列表。

```python
datasets = await client.list_datasets()
```

#### create_dataset()

创建数据集。

```python
dataset = await client.create_dataset("数据集名称")
```

### 数据集管理方法

#### update()

更新数据。

#### delete_dataset()

删除数据集。

#### get_dataset_data()

获取数据集中的数据项。

#### get_dataset_graph()

获取知识图谱数据。

#### get_dataset_status()

获取数据集处理状态。

#### download_raw_data()

下载原始数据文件。

### 认证方法

#### login()

用户登录。

```python
token = await client.login("user@example.com", "password")
```

#### register()

用户注册。

```python
user = await client.register("user@example.com", "password")
```

#### get_current_user()

获取当前用户信息。

### 其他方法

#### memify()

添加记忆算法。

#### get_search_history()

获取搜索历史。

#### visualize()

生成 HTML 可视化。

#### sync_to_cloud()

同步到云端。

#### get_sync_status()

获取同步状态。

#### subscribe_cognify_progress()

订阅 Cognify 处理进度（WebSocket）。

#### add_batch()

批量添加数据。

## 异常类型

- `CogneeSDKError` - 基础异常
- `CogneeAPIError` - API 调用错误
- `AuthenticationError` - 认证错误（401）
- `NotFoundError` - 资源未找到（404）
- `ValidationError` - 请求验证错误（400）
- `ServerError` - 服务器错误（5xx）
- `TimeoutError` - 请求超时

## 数据模型

所有数据模型定义在 `cognee_sdk.models` 模块中，使用 Pydantic BaseModel。

主要模型：
- `User` - 用户模型
- `Dataset` - 数据集模型
- `DataItem` - 数据项模型
- `AddResult` - 添加结果
- `CognifyResult` - Cognify 结果
- `SearchResult` - 搜索结果
- `GraphData` - 图谱数据

