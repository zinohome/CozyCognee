# Cognee SDK 测试指南

本文档介绍如何运行和编写 cognee-sdk 的测试。

## 📋 目录

- [环境准备](#环境准备)
- [运行测试](#运行测试)
- [测试覆盖率](#测试覆盖率)
- [测试结构](#测试结构)
- [编写测试](#编写测试)
- [代码质量检查](#代码质量检查)

## 环境准备

### 1. 安装开发依赖

首先需要安装开发依赖，包括 pytest、pytest-asyncio、pytest-cov 等：

```bash
cd cognee_sdk
pip install -e ".[dev]"
```

这会安装以下开发工具：
- `pytest>=7.0.0` - 测试框架
- `pytest-asyncio>=0.21.0` - 异步测试支持
- `pytest-cov>=4.0.0` - 测试覆盖率
- `black>=23.0.0` - 代码格式化
- `ruff>=0.1.0` - 代码检查和格式化
- `mypy>=1.0.0` - 类型检查

### 2. 验证安装

确认 pytest 已正确安装：

```bash
pytest --version
```

## 运行测试

### 运行所有测试

```bash
# 在 cognee_sdk 目录下运行
pytest
```

### 运行特定测试文件

```bash
# 运行客户端测试
pytest tests/test_client.py

# 运行认证测试
pytest tests/test_auth.py

# 运行搜索测试
pytest tests/test_search_comprehensive.py
```

### 运行特定测试函数

```bash
# 运行特定的测试函数
pytest tests/test_client.py::test_client_initialization

# 运行匹配模式的测试
pytest -k "test_add"
```

### 详细输出

```bash
# 显示详细输出
pytest -v

# 显示最详细的输出（包括 print 语句）
pytest -vv -s
```

### 并行运行测试

```bash
# 安装 pytest-xdist（如果未安装）
pip install pytest-xdist

# 并行运行测试（使用 4 个进程）
pytest -n 4
```

## 测试覆盖率

### 查看覆盖率报告

项目配置要求测试覆盖率 ≥ 80%。运行测试时会自动生成覆盖率报告：

```bash
# 运行测试并生成覆盖率报告
pytest --cov=cognee_sdk --cov-report=html

# 查看终端覆盖率报告
pytest --cov=cognee_sdk --cov-report=term-missing
```

### 查看 HTML 覆盖率报告

运行 `pytest --cov=cognee_sdk --cov-report=html` 后，会在 `htmlcov/` 目录生成 HTML 报告：

```bash
# 在浏览器中打开覆盖率报告
open htmlcov/index.html  # macOS
# 或
xdg-open htmlcov/index.html  # Linux
```

### 覆盖率配置

覆盖率配置在 `pyproject.toml` 中：

```toml
[tool.coverage.run]
source = ["cognee_sdk"]
omit = [
    "*/tests/*",
    "*/examples/*",
    "*/__pycache__/*",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
]
```

## 测试结构

### 测试文件组织

测试文件位于 `tests/` 目录，按功能模块组织：

```
tests/
├── __init__.py
├── test_client.py              # 客户端核心功能测试
├── test_auth.py                # 认证相关测试
├── test_datasets.py            # 数据集操作测试
├── test_search_comprehensive.py # 搜索功能测试
├── test_cognify_comprehensive.py # Cognify 功能测试
├── test_delete_comprehensive.py  # 删除功能测试
├── test_file_upload.py         # 文件上传测试
├── test_websocket.py           # WebSocket 功能测试
├── test_exceptions.py          # 异常处理测试
├── test_models.py              # 数据模型测试
├── test_concurrency.py         # 并发操作测试
├── test_integration_scenarios.py # 集成场景测试
└── ...
```

### 测试命名规范

- 测试文件：`test_*.py`
- 测试类：`Test*`
- 测试函数：`test_*`

### 测试配置

pytest 配置在 `pyproject.toml` 中：

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
asyncio_mode = "auto"  # 自动检测异步测试
addopts = [
    "--strict-markers",
    "--cov=cognee_sdk",
    "--cov-report=term-missing",
    "--cov-report=html",
    "--cov-fail-under=80",  # 覆盖率要求 ≥ 80%
]
```

## 编写测试

### 基本测试结构

所有测试使用 pytest 和 pytest-asyncio。示例：

```python
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from cognee_sdk import CogneeClient

@pytest.fixture
def client():
    """创建测试客户端实例"""
    return CogneeClient(api_url="http://localhost:8000", api_token="test-token")

@pytest.mark.asyncio
async def test_client_initialization(client):
    """测试客户端初始化"""
    assert client.api_url == "http://localhost:8000"
    assert client.api_token == "test-token"
```

### 异步测试

所有 API 调用都是异步的，测试必须使用 `@pytest.mark.asyncio` 装饰器：

```python
@pytest.mark.asyncio
async def test_search(client):
    """测试搜索功能"""
    # 使用 mock 模拟 HTTP 请求
    with patch.object(client.client, 'post', new_callable=AsyncMock) as mock_post:
        mock_post.return_value.json.return_value = [
            {"id": "1", "text": "result 1"}
        ]
        mock_post.return_value.status_code = 200
        
        results = await client.search("test query")
        assert len(results) == 1
```

### Mock HTTP 请求

使用 `unittest.mock` 模拟 HTTP 请求，避免实际网络调用：

```python
from unittest.mock import AsyncMock, MagicMock, patch

@pytest.fixture
def mock_response():
    """创建模拟 HTTP 响应"""
    response = MagicMock()
    response.status_code = 200
    response.json = MagicMock(return_value={})
    response.text = ""
    return response

@pytest.mark.asyncio
async def test_add_data(client, mock_response):
    """测试添加数据"""
    mock_response.json.return_value = {
        "status": "success",
        "data_id": "123",
    }
    
    with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
        mock_request.return_value = mock_response
        result = await client.add(data="test", dataset_name="test-dataset")
        assert result.status == "success"
```

### 测试异常处理

测试应该验证异常是否正确抛出：

```python
from cognee_sdk.exceptions import AuthenticationError, NotFoundError

@pytest.mark.asyncio
async def test_authentication_error(client):
    """测试认证错误"""
    with patch.object(client.client, 'post') as mock_post:
        mock_post.return_value.status_code = 401
        mock_post.return_value.json.return_value = {"error": "Unauthorized"}
        
        with pytest.raises(AuthenticationError):
            await client.search("test query")
```

### 使用 Fixtures

pytest fixtures 用于共享测试数据和设置：

```python
@pytest.fixture
def client():
    """创建测试客户端"""
    return CogneeClient(api_url="http://localhost:8000")

@pytest.fixture
def sample_dataset():
    """创建示例数据集"""
    return {
        "id": "dataset-123",
        "name": "test-dataset",
    }

@pytest.mark.asyncio
async def test_with_fixtures(client, sample_dataset):
    """使用 fixtures 的测试"""
    # 使用 client 和 sample_dataset
    pass
```

### 测试最佳实践

1. **每个测试应该独立**：不依赖其他测试的执行顺序
2. **使用描述性的测试名称**：清楚说明测试的目的
3. **测试正常情况和异常情况**：包括成功和失败场景
4. **使用 mock 避免外部依赖**：不依赖实际的 API 服务器
5. **保持测试简单**：每个测试只验证一个功能点
6. **添加文档字符串**：说明测试的目的和场景

## 代码质量检查

### 运行代码格式化

```bash
# 使用 ruff 格式化代码
ruff format .

# 检查代码格式（不修改）
ruff format --check .
```

### 运行代码检查

```bash
# 使用 ruff 检查代码
ruff check .

# 检查特定文件
ruff check cognee_sdk/client.py
```

### 运行类型检查

```bash
# 使用 mypy 进行类型检查
mypy cognee_sdk/

# 显示详细错误信息
mypy cognee_sdk/ --show-error-codes
```

### 完整的代码质量检查流程

在提交代码前，运行完整的检查：

```bash
# 1. 格式化代码
ruff format .

# 2. 检查代码
ruff check .

# 3. 类型检查
mypy cognee_sdk/

# 4. 运行测试
pytest

# 5. 检查覆盖率
pytest --cov=cognee_sdk --cov-report=term-missing
```

## 常见问题

### 1. 测试失败：找不到模块

确保在 `cognee_sdk` 目录下运行测试，或者使用开发模式安装：

```bash
pip install -e ".[dev]"
```

### 2. 异步测试不运行

确保安装了 `pytest-asyncio` 并且配置了 `asyncio_mode = "auto"`。

### 3. 覆盖率低于 80%

检查哪些代码没有被测试覆盖：

```bash
pytest --cov=cognee_sdk --cov-report=term-missing
```

然后为未覆盖的代码添加测试。

### 4. Mock 不工作

确保使用 `AsyncMock` 来模拟异步函数：

```python
from unittest.mock import AsyncMock

with patch.object(client.client, 'post', new_callable=AsyncMock) as mock_post:
    # ...
```

## 参考资源

- [pytest 文档](https://docs.pytest.org/)
- [pytest-asyncio 文档](https://pytest-asyncio.readthedocs.io/)
- [unittest.mock 文档](https://docs.python.org/3/library/unittest.mock.html)
- [项目 README](../cognee_sdk/README.md)
- [贡献指南](../cognee_sdk/CONTRIBUTING.md)

