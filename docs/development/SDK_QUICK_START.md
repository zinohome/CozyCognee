# Cognee SDK 快速使用指南

本文档提供 cognee-sdk 的快速使用指南，包括安装、基本使用、测试和开发流程。

## 📦 安装

### 1. 安装 SDK

```bash
# 基础安装
pip install cognee-sdk

# 包含 WebSocket 支持
pip install cognee-sdk[websocket]
```

### 2. 开发模式安装（用于开发）

```bash
cd cognee_sdk
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e ".[dev]"
```

## 🚀 基本使用

### 初始化客户端

```python
import asyncio
from cognee_sdk import CogneeClient, SearchType

async def main():
    # 创建客户端
    client = CogneeClient(
        api_url="http://localhost:8000",
        api_token="your-token-here"  # 可选
    )
    
    try:
        # 你的代码
        pass
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
```

### 添加数据

```python
# 添加文本数据
result = await client.add(
    data="Cognee turns documents into AI memory.",
    dataset_name="my-dataset"
)
print(f"Added data: {result.data_id}")

# 添加文件
result = await client.add(
    data="/path/to/file.pdf",
    dataset_name="my-dataset"
)

# 批量添加
results = await client.add_batch(
    data_list=["text1", "text2", "text3"],
    dataset_name="my-dataset"
)
```

### 处理数据

```python
# Cognify - 将数据转换为知识图谱
cognify_result = await client.cognify(
    datasets=["my-dataset"],
    run_in_background=False
)
print(f"Status: {cognify_result.status}")

# Memify - 记忆化处理
memify_result = await client.memify(
    dataset_name="my-dataset"
)
```

### 搜索

```python
# 基础搜索
results = await client.search(
    query="What does Cognee do?",
    search_type=SearchType.GRAPH_COMPLETION
)

# 高级搜索
results = await client.search(
    query="What does Cognee do?",
    search_type=SearchType.GRAPH_COMPLETION,
    datasets=["my-dataset"],
    top_k=10,
    system_prompt="You are a helpful assistant."
)
```

### 数据集管理

```python
# 列出所有数据集
datasets = await client.list_datasets()

# 创建数据集
dataset = await client.create_dataset(name="new-dataset")

# 删除数据集
await client.delete_dataset(dataset_id=dataset.id)

# 获取数据集状态
status = await client.get_dataset_status(dataset_ids=[dataset.id])
```

## 🧪 测试

### 运行测试

```bash
cd cognee_sdk
source venv/bin/activate

# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_client.py

# 运行特定测试函数
pytest tests/test_client.py::test_client_initialization

# 显示详细输出
pytest -v

# 查看覆盖率
pytest --cov=cognee_sdk --cov-report=html
open htmlcov/index.html  # 查看 HTML 报告
```

### 代码质量检查

```bash
# 格式化代码
ruff format .

# 检查代码
ruff check .

# 自动修复可修复的问题
ruff check --fix .

# 类型检查
mypy cognee_sdk/
```

## 🔧 开发流程

### 1. 创建虚拟环境

```bash
cd cognee_sdk
python -m venv venv
source venv/bin/activate
```

### 2. 安装依赖

```bash
pip install -e ".[dev]"
```

### 3. 编写代码

在 `cognee_sdk/` 目录下编写或修改代码。

### 4. 运行测试

```bash
pytest
```

### 5. 代码质量检查

```bash
ruff format .
ruff check --fix .
mypy cognee_sdk/
```

### 6. 提交代码

```bash
# 查看更改
git status

# 添加文件
git add .

# 提交
git commit -m "描述你的更改"

# 推送
git push
```

## 📝 Git 配置（首次使用）

如果首次使用 Git，需要配置用户信息：

```bash
# 设置全局用户信息
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# 或者只设置当前仓库
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

## 📚 更多资源

- [完整 API 文档](../cognee_sdk/README.md)
- [测试指南](./SDK_TESTING.md)
- [示例代码](../cognee_sdk/examples/)
- [开发文档](./README.md)

## 💡 常见问题

### Q: 如何查看所有可用的搜索类型？

```python
from cognee_sdk.models import SearchType

# 查看所有搜索类型
for search_type in SearchType:
    print(search_type.name, search_type.value)
```

### Q: 如何处理错误？

```python
from cognee_sdk.exceptions import (
    AuthenticationError,
    NotFoundError,
    ValidationError,
    ServerError
)

try:
    await client.search("query")
except AuthenticationError:
    print("认证失败")
except NotFoundError:
    print("资源未找到")
except ValidationError:
    print("请求参数错误")
except ServerError:
    print("服务器错误")
```

### Q: 如何使用 WebSocket 获取实时进度？

```python
# 需要安装: pip install cognee-sdk[websocket]

async for update in client.subscribe_cognify_progress(pipeline_run_id):
    print(f"Status: {update['status']}, Progress: {update.get('progress', 0)}%")
    if update['status'] == 'completed':
        break
```

### Q: 测试失败怎么办？

1. 确保虚拟环境已激活
2. 确保已安装所有依赖：`pip install -e ".[dev]"`
3. 检查代码格式：`ruff format .`
4. 查看详细错误信息：`pytest -vv`

## 🎯 下一步

- 查看 [示例代码](../cognee_sdk/examples/) 了解更多用法
- 阅读 [API 文档](../cognee_sdk/README.md) 了解完整功能
- 参考 [测试指南](./SDK_TESTING.md) 学习如何编写测试

