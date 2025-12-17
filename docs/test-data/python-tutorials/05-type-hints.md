# Python 类型提示

类型提示（Type Hints）是 Python 3.5+ 引入的特性，用于声明变量、参数和返回值的类型。

## 基础类型提示

### 变量类型提示

```python
# 基本类型
name: str = "Alice"
age: int = 25
price: float = 19.99
is_active: bool = True

# 类型可以不赋值（仅声明）
email: str  # 稍后赋值
```

### 函数参数和返回值

```python
def greet(name: str) -> str:
    return f"Hello, {name}!"

def add(a: int, b: int) -> int:
    return a + b

def process_data(data: bytes) -> None:
    # 无返回值用 None
    print(data)
```

## typing 模块

Python 的 typing 模块提供了丰富的类型工具。

### 容器类型

```python
from typing import List, Dict, Set, Tuple

# 列表
names: List[str] = ["Alice", "Bob", "Charlie"]

# 字典
scores: Dict[str, int] = {"Alice": 95, "Bob": 87}

# 集合
unique_ids: Set[int] = {1, 2, 3}

# 元组（固定长度）
point: Tuple[int, int] = (10, 20)

# 元组（可变长度同类型）
values: Tuple[int, ...] = (1, 2, 3, 4, 5)
```

### Python 3.9+ 简化语法

从 Python 3.9 开始，可以直接使用内置类型：

```python
# Python 3.9+
names: list[str] = ["Alice", "Bob"]
scores: dict[str, int] = {"Alice": 95}
point: tuple[int, int] = (10, 20)
```

### Optional 类型

表示值可能是 None：

```python
from typing import Optional

def find_user(user_id: int) -> Optional[str]:
    """返回用户名，找不到返回 None"""
    users = {1: "Alice", 2: "Bob"}
    return users.get(user_id)

# 等价于 Union[str, None]
def get_name(user_id: int) -> str | None:  # Python 3.10+
    pass
```

### Union 类型

表示多种可能的类型：

```python
from typing import Union

def process(data: Union[str, bytes]) -> str:
    if isinstance(data, bytes):
        return data.decode()
    return data

# Python 3.10+ 可用 | 语法
def process(data: str | bytes) -> str:
    pass
```

### Any 类型

表示任意类型（应谨慎使用）：

```python
from typing import Any

def log(message: Any) -> None:
    print(str(message))
```

## 高级类型

### Callable

表示可调用对象（函数）：

```python
from typing import Callable

def apply_func(
    func: Callable[[int, int], int],
    a: int,
    b: int
) -> int:
    return func(a, b)

# 使用示例
result = apply_func(lambda x, y: x + y, 1, 2)
```

### TypeVar 泛型

创建泛型类型变量：

```python
from typing import TypeVar, List

T = TypeVar('T')

def first(items: List[T]) -> T:
    return items[0]

# 自动推断类型
name = first(["Alice", "Bob"])  # str
number = first([1, 2, 3])       # int

# 限制类型范围
Number = TypeVar('Number', int, float)

def double(x: Number) -> Number:
    return x * 2
```

### Generic 泛型类

```python
from typing import Generic, TypeVar

T = TypeVar('T')

class Stack(Generic[T]):
    def __init__(self) -> None:
        self._items: List[T] = []
    
    def push(self, item: T) -> None:
        self._items.append(item)
    
    def pop(self) -> T:
        return self._items.pop()

# 使用泛型类
int_stack: Stack[int] = Stack()
int_stack.push(1)
int_stack.push(2)

str_stack: Stack[str] = Stack()
str_stack.push("hello")
```

### Literal

限制为特定字面值：

```python
from typing import Literal

def set_mode(mode: Literal["read", "write", "append"]) -> None:
    print(f"Mode set to: {mode}")

set_mode("read")    # 正确
# set_mode("delete")  # 类型错误
```

### TypedDict

定义具有特定键的字典类型：

```python
from typing import TypedDict

class UserDict(TypedDict):
    name: str
    age: int
    email: str

def create_user(data: UserDict) -> None:
    print(f"Creating user: {data['name']}")

user: UserDict = {
    "name": "Alice",
    "age": 25,
    "email": "alice@example.com"
}
```

### Protocol

定义结构化子类型（鸭子类型）：

```python
from typing import Protocol

class Drawable(Protocol):
    def draw(self) -> None: ...

class Circle:
    def draw(self) -> None:
        print("Drawing circle")

class Square:
    def draw(self) -> None:
        print("Drawing square")

def render(shape: Drawable) -> None:
    shape.draw()

# Circle 和 Square 不需要继承 Drawable
# 只需要有 draw 方法即可
render(Circle())
render(Square())
```

## 类型别名

### 简单别名

```python
from typing import List, Dict, Tuple

# 类型别名
Vector = List[float]
Matrix = List[Vector]
Point = Tuple[float, float]
Headers = Dict[str, str]

def dot_product(v1: Vector, v2: Vector) -> float:
    return sum(a * b for a, b in zip(v1, v2))
```

### TypeAlias (Python 3.10+)

```python
from typing import TypeAlias

Vector: TypeAlias = list[float]
Matrix: TypeAlias = list[Vector]
```

## 类中的类型提示

### 类属性

```python
class User:
    name: str
    age: int
    email: str | None
    
    def __init__(self, name: str, age: int) -> None:
        self.name = name
        self.age = age
        self.email = None

# 类变量 vs 实例变量
from typing import ClassVar

class Counter:
    count: ClassVar[int] = 0  # 类变量
    value: int                 # 实例变量
```

### 自引用类型

```python
from __future__ import annotations

class Node:
    def __init__(self, value: int, next: Node | None = None) -> None:
        self.value = value
        self.next = next
    
    def append(self, node: Node) -> None:
        current = self
        while current.next:
            current = current.next
        current.next = node
```

## 使用 dataclass

dataclass 与类型提示完美配合：

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class User:
    name: str
    age: int
    email: Optional[str] = None
    
    def greet(self) -> str:
        return f"Hello, I'm {self.name}!"

# 自动生成 __init__, __repr__, __eq__ 等
user = User(name="Alice", age=25)
```

## Pydantic 数据验证

Pydantic 结合类型提示进行运行时验证：

```python
from pydantic import BaseModel, EmailStr
from typing import Optional

class User(BaseModel):
    name: str
    age: int
    email: EmailStr
    is_active: bool = True
    
# 自动验证类型
user = User(
    name="Alice",
    age=25,
    email="alice@example.com"
)

# 类型错误会抛出异常
# User(name="Alice", age="not a number", email="invalid")
```

## 类型检查工具

### mypy

静态类型检查器：

```bash
# 安装
pip install mypy

# 检查单个文件
mypy script.py

# 检查整个项目
mypy --config-file mypy.ini .
```

**mypy 配置示例** (mypy.ini):

```ini
[mypy]
python_version = 3.11
strict = True
warn_return_any = True
warn_unused_ignores = True
```

### pyright

Microsoft 开发的类型检查器，速度更快：

```bash
pip install pyright
pyright .
```

## 最佳实践

1. **逐步添加类型提示**：从核心模块开始
2. **使用 Optional 明确表示可能为 None**
3. **避免过度使用 Any**：它会削弱类型检查
4. **使用 TypedDict 代替普通 dict**：当字典结构固定时
5. **利用 Protocol 实现鸭子类型**：更灵活的接口定义
6. **配置 CI 进行类型检查**：确保代码质量

## 常见模式

### 返回 self

```python
from typing import TypeVar

T = TypeVar('T', bound='Builder')

class Builder:
    def set_name(self: T, name: str) -> T:
        self.name = name
        return self
    
    def set_age(self: T, age: int) -> T:
        self.age = age
        return self
```

### 工厂模式

```python
from typing import Type, TypeVar

T = TypeVar('T', bound='Animal')

class Animal:
    @classmethod
    def create(cls: Type[T]) -> T:
        return cls()

class Dog(Animal):
    pass

dog = Dog.create()  # 类型推断为 Dog
```

## 总结

- 类型提示提高代码可读性和可维护性
- typing 模块提供丰富的类型工具
- 配合 mypy/pyright 进行静态类型检查
- Pydantic 实现运行时类型验证
- 类型提示是可选的，不影响运行时行为
