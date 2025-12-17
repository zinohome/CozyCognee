# Python 函数与装饰器

函数是组织代码的基本单元，装饰器是 Python 中强大的元编程工具。

## 函数基础

### 定义函数

```python
def greet(name):
    """向用户问好"""
    return f"Hello, {name}!"

# 调用函数
message = greet("Alice")
print(message)  # Hello, Alice!
```

### 参数类型

**位置参数**：按位置传递的参数。

```python
def power(base, exponent):
    return base ** exponent

result = power(2, 3)  # 8
```

**关键字参数**：按名称传递的参数。

```python
result = power(exponent=3, base=2)  # 8
```

**默认参数**：带默认值的参数。

```python
def greet(name, greeting="Hello"):
    return f"{greeting}, {name}!"

print(greet("Alice"))           # Hello, Alice!
print(greet("Bob", "Hi"))       # Hi, Bob!
```

**可变参数 (*args)**：接收任意数量的位置参数。

```python
def sum_all(*numbers):
    return sum(numbers)

print(sum_all(1, 2, 3, 4, 5))  # 15
```

**关键字可变参数 (**kwargs)**：接收任意数量的关键字参数。

```python
def print_info(**kwargs):
    for key, value in kwargs.items():
        print(f"{key}: {value}")

print_info(name="Alice", age=25, city="Beijing")
```

**参数组合顺序**：位置参数 → *args → 默认参数 → **kwargs

```python
def complex_func(a, b, *args, c=10, **kwargs):
    print(f"a={a}, b={b}, args={args}, c={c}, kwargs={kwargs}")

complex_func(1, 2, 3, 4, c=20, x=100)
```

### 返回值

函数可以返回多个值（实际上是元组）：

```python
def get_stats(numbers):
    return min(numbers), max(numbers), sum(numbers) / len(numbers)

minimum, maximum, average = get_stats([1, 2, 3, 4, 5])
```

## Lambda 表达式

Lambda 是匿名函数，适合简单操作：

```python
# 普通函数
def square(x):
    return x ** 2

# Lambda 等价写法
square = lambda x: x ** 2

# 常用于排序
students = [("Alice", 85), ("Bob", 92), ("Charlie", 78)]
sorted_students = sorted(students, key=lambda x: x[1], reverse=True)

# 用于 map/filter
numbers = [1, 2, 3, 4, 5]
squares = list(map(lambda x: x**2, numbers))
evens = list(filter(lambda x: x % 2 == 0, numbers))
```

## 高阶函数

高阶函数是接收函数作为参数或返回函数的函数。

### 内置高阶函数

```python
# map: 对每个元素应用函数
numbers = [1, 2, 3, 4, 5]
squares = list(map(lambda x: x**2, numbers))

# filter: 过滤元素
evens = list(filter(lambda x: x % 2 == 0, numbers))

# reduce: 累积计算
from functools import reduce
total = reduce(lambda x, y: x + y, numbers)

# sorted: 自定义排序
words = ["apple", "Banana", "cherry"]
sorted_words = sorted(words, key=str.lower)
```

### 自定义高阶函数

```python
def apply_twice(func, value):
    """将函数应用两次"""
    return func(func(value))

result = apply_twice(lambda x: x * 2, 5)  # 20

def make_multiplier(n):
    """返回一个乘法函数"""
    def multiplier(x):
        return x * n
    return multiplier

triple = make_multiplier(3)
print(triple(10))  # 30
```

## 闭包

闭包是引用了外部作用域变量的内部函数：

```python
def counter():
    count = 0
    
    def increment():
        nonlocal count
        count += 1
        return count
    
    return increment

c = counter()
print(c())  # 1
print(c())  # 2
print(c())  # 3
```

闭包常用于：
- 数据隐藏和封装
- 创建工厂函数
- 实现装饰器

## 装饰器

装饰器是修改函数行为的函数，使用 `@` 语法应用。

### 基本装饰器

```python
def my_decorator(func):
    def wrapper(*args, **kwargs):
        print("函数执行前")
        result = func(*args, **kwargs)
        print("函数执行后")
        return result
    return wrapper

@my_decorator
def say_hello(name):
    print(f"Hello, {name}!")

say_hello("Alice")
# 输出:
# 函数执行前
# Hello, Alice!
# 函数执行后
```

### 保留函数元信息

使用 `functools.wraps` 保留原函数的元信息：

```python
from functools import wraps

def my_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        """wrapper docstring"""
        return func(*args, **kwargs)
    return wrapper

@my_decorator
def greet(name):
    """向用户问好"""
    return f"Hello, {name}!"

print(greet.__name__)  # greet（不使用 wraps 会显示 wrapper）
print(greet.__doc__)   # 向用户问好
```

### 带参数的装饰器

```python
def repeat(times):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for _ in range(times):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

@repeat(3)
def greet(name):
    print(f"Hello, {name}!")

greet("Alice")  # 打印 3 次
```

### 类装饰器

```python
class CountCalls:
    def __init__(self, func):
        self.func = func
        self.count = 0
    
    def __call__(self, *args, **kwargs):
        self.count += 1
        print(f"调用次数: {self.count}")
        return self.func(*args, **kwargs)

@CountCalls
def greet(name):
    print(f"Hello, {name}!")

greet("Alice")  # 调用次数: 1
greet("Bob")    # 调用次数: 2
```

### 常用装饰器示例

**计时装饰器**：

```python
import time
from functools import wraps

def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} 执行时间: {end - start:.4f}秒")
        return result
    return wrapper

@timer
def slow_function():
    time.sleep(1)
    return "完成"
```

**缓存装饰器**：

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

print(fibonacci(100))  # 快速计算，因为结果被缓存
```

**重试装饰器**：

```python
def retry(max_attempts=3, delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt < max_attempts - 1:
                        time.sleep(delay)
                    else:
                        raise e
        return wrapper
    return decorator

@retry(max_attempts=3, delay=2)
def unreliable_api_call():
    # 可能失败的 API 调用
    pass
```

### 装饰器堆叠

多个装饰器可以堆叠使用，执行顺序从下到上：

```python
@decorator1
@decorator2
@decorator3
def my_function():
    pass

# 等价于
my_function = decorator1(decorator2(decorator3(my_function)))
```

## 总结

- 函数是代码复用的基本单元
- 灵活使用各种参数类型提高函数通用性
- Lambda 适合简单的匿名函数
- 高阶函数和闭包是函数式编程的核心
- 装饰器是强大的元编程工具，用于扩展函数行为
