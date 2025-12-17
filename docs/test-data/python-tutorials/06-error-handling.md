# Python 错误处理

错误处理是编写健壮程序的关键。Python 使用异常机制来处理错误情况。

## 异常基础

### 异常类型

Python 内置了丰富的异常类型：

```python
# 语法错误（无法捕获）
# if True print("hello")  # SyntaxError

# 常见运行时异常
x = 1 / 0           # ZeroDivisionError
int("abc")          # ValueError
name                # NameError（未定义变量）
[1, 2, 3][10]       # IndexError
{"a": 1}["b"]       # KeyError
open("不存在.txt")   # FileNotFoundError
1 + "string"        # TypeError
```

### 异常层次结构

```
BaseException
├── SystemExit
├── KeyboardInterrupt
├── GeneratorExit
└── Exception
    ├── StopIteration
    ├── ArithmeticError
    │   ├── ZeroDivisionError
    │   ├── OverflowError
    │   └── FloatingPointError
    ├── LookupError
    │   ├── IndexError
    │   └── KeyError
    ├── OSError
    │   ├── FileNotFoundError
    │   ├── PermissionError
    │   └── TimeoutError
    ├── ValueError
    ├── TypeError
    └── ...
```

## try-except 语句

### 基本用法

```python
try:
    result = 10 / 0
except ZeroDivisionError:
    print("不能除以零！")
```

### 捕获多种异常

```python
try:
    value = int(input("请输入数字: "))
    result = 10 / value
except ValueError:
    print("输入的不是有效数字")
except ZeroDivisionError:
    print("不能输入零")

# 或者合并捕获
try:
    value = int(input("请输入数字: "))
    result = 10 / value
except (ValueError, ZeroDivisionError) as e:
    print(f"发生错误: {e}")
```

### 获取异常信息

```python
try:
    result = risky_operation()
except Exception as e:
    print(f"异常类型: {type(e).__name__}")
    print(f"异常信息: {e}")
    print(f"异常参数: {e.args}")
```

### else 子句

没有发生异常时执行：

```python
try:
    result = 10 / 2
except ZeroDivisionError:
    print("除零错误")
else:
    print(f"结果是: {result}")  # 只有成功时才执行
```

### finally 子句

无论是否发生异常都会执行：

```python
try:
    file = open("data.txt", "r")
    data = file.read()
except FileNotFoundError:
    print("文件不存在")
finally:
    # 清理资源
    if 'file' in locals():
        file.close()
```

### 完整语法

```python
try:
    # 可能引发异常的代码
    result = risky_operation()
except SpecificError as e:
    # 处理特定异常
    handle_specific_error(e)
except Exception as e:
    # 处理其他所有异常
    handle_general_error(e)
else:
    # 没有异常时执行
    process_result(result)
finally:
    # 总是执行（清理资源）
    cleanup()
```

## 抛出异常

### raise 语句

```python
def divide(a, b):
    if b == 0:
        raise ValueError("除数不能为零")
    return a / b

def validate_age(age):
    if not isinstance(age, int):
        raise TypeError("年龄必须是整数")
    if age < 0 or age > 150:
        raise ValueError("年龄必须在 0-150 之间")
    return age
```

### 重新抛出异常

```python
try:
    result = risky_operation()
except Exception as e:
    # 记录日志后重新抛出
    logging.error(f"操作失败: {e}")
    raise  # 重新抛出当前异常

# 或者抛出新异常，保留原因链
try:
    result = risky_operation()
except SomeError as e:
    raise RuntimeError("操作失败") from e
```

## 自定义异常

### 基本自定义异常

```python
class ValidationError(Exception):
    """验证错误"""
    pass

class DatabaseError(Exception):
    """数据库错误"""
    pass

def validate_email(email):
    if "@" not in email:
        raise ValidationError(f"无效的邮箱地址: {email}")
```

### 带额外信息的异常

```python
class APIError(Exception):
    """API 调用错误"""
    
    def __init__(self, message, status_code, response=None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response = response
    
    def __str__(self):
        return f"[{self.status_code}] {self.message}"

# 使用
try:
    response = call_api()
    if response.status_code != 200:
        raise APIError(
            "API 调用失败",
            status_code=response.status_code,
            response=response.json()
        )
except APIError as e:
    print(f"错误: {e}")
    print(f"状态码: {e.status_code}")
    print(f"响应: {e.response}")
```

### 异常层次结构

```python
class AppError(Exception):
    """应用基础异常"""
    pass

class DatabaseError(AppError):
    """数据库相关错误"""
    pass

class ConnectionError(DatabaseError):
    """数据库连接错误"""
    pass

class QueryError(DatabaseError):
    """查询错误"""
    pass

class ValidationError(AppError):
    """数据验证错误"""
    pass

class AuthError(AppError):
    """认证错误"""
    pass
```

## 上下文管理器

### with 语句

自动管理资源，确保清理：

```python
# 文件操作
with open("data.txt", "r") as file:
    content = file.read()
# 文件自动关闭

# 数据库连接
with get_db_connection() as conn:
    cursor = conn.execute("SELECT * FROM users")
# 连接自动关闭
```

### 自定义上下文管理器

使用类实现：

```python
class Timer:
    def __enter__(self):
        self.start = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end = time.time()
        print(f"耗时: {self.end - self.start:.2f}秒")
        return False  # 不抑制异常

with Timer():
    time.sleep(1)
```

使用 contextmanager 装饰器：

```python
from contextlib import contextmanager

@contextmanager
def timer():
    start = time.time()
    try:
        yield
    finally:
        end = time.time()
        print(f"耗时: {end - start:.2f}秒")

with timer():
    time.sleep(1)
```

### 异常处理上下文管理器

```python
@contextmanager
def handle_errors():
    try:
        yield
    except ValueError as e:
        print(f"值错误: {e}")
    except TypeError as e:
        print(f"类型错误: {e}")
    except Exception as e:
        print(f"未知错误: {e}")
        raise

with handle_errors():
    risky_operation()
```

## 日志记录

### 基本日志

```python
import logging

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='app.log'
)

logger = logging.getLogger(__name__)

try:
    result = risky_operation()
except Exception as e:
    logger.error(f"操作失败: {e}", exc_info=True)
```

### 日志级别

```python
logger.debug("调试信息")
logger.info("一般信息")
logger.warning("警告信息")
logger.error("错误信息")
logger.critical("严重错误")

# 记录异常堆栈
try:
    risky_operation()
except Exception:
    logger.exception("发生异常")  # 自动包含堆栈信息
```

## 断言

### assert 语句

用于调试和开发阶段的检查：

```python
def calculate_average(numbers):
    assert len(numbers) > 0, "列表不能为空"
    return sum(numbers) / len(numbers)

# 注意：可以用 -O 参数禁用断言
# python -O script.py
```

### 断言 vs 异常

```python
# 断言：检查不应该发生的情况（编程错误）
def get_item(items, index):
    assert 0 <= index < len(items), "索引超出范围"
    return items[index]

# 异常：处理可能发生的错误情况（运行时错误）
def get_item_safe(items, index):
    if not 0 <= index < len(items):
        raise IndexError(f"索引 {index} 超出范围")
    return items[index]
```

## 错误处理模式

### 提前返回

```python
def process_user(user_data):
    if not user_data:
        return None
    
    if "name" not in user_data:
        raise ValueError("缺少 name 字段")
    
    if "age" not in user_data:
        raise ValueError("缺少 age 字段")
    
    # 正常处理
    return create_user(user_data)
```

### 错误码 vs 异常

```python
# 使用异常（推荐）
def divide(a, b):
    if b == 0:
        raise ValueError("除数不能为零")
    return a / b

# 使用错误码（不推荐）
def divide_with_code(a, b):
    if b == 0:
        return None, "除数不能为零"
    return a / b, None
```

### 重试模式

```python
import time
from functools import wraps

def retry(max_attempts=3, delay=1, exceptions=(Exception,)):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        time.sleep(delay * (2 ** attempt))  # 指数退避
            raise last_exception
        return wrapper
    return decorator

@retry(max_attempts=3, delay=1, exceptions=(ConnectionError,))
def fetch_data(url):
    # 可能失败的网络请求
    pass
```

## 最佳实践

1. **捕获具体异常**：避免裸露的 `except:`
   
   ```python
   # 不推荐
   try:
       risky_operation()
   except:
       pass
   
   # 推荐
   try:
       risky_operation()
   except SpecificError as e:
       handle_error(e)
   ```

2. **不要忽略异常**：至少记录日志
   
   ```python
   try:
       operation()
   except Exception as e:
       logger.error(f"操作失败: {e}")
       # 决定是否需要重新抛出
   ```

3. **使用上下文管理器管理资源**

4. **自定义异常提供更多上下文**

5. **在适当的层级处理异常**

## 总结

- try-except 是 Python 异常处理的核心
- 使用 finally 确保资源清理
- 自定义异常类提供更好的错误信息
- 上下文管理器简化资源管理
- 日志记录是调试的重要工具
- 选择合适的错误处理策略
