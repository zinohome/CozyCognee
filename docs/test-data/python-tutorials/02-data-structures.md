# Python 数据结构

Python 提供了多种内置数据结构，用于存储和组织数据。本文介绍列表、元组、字典和集合这四种核心数据结构。

## 列表 (List)

列表是 Python 中最常用的数据结构，是一个有序、可变的元素集合。

### 创建列表

```python
# 空列表
empty_list = []
empty_list = list()

# 带初始值的列表
numbers = [1, 2, 3, 4, 5]
mixed = [1, "hello", 3.14, True]

# 列表推导式
squares = [x**2 for x in range(10)]
```

### 列表操作

```python
fruits = ["apple", "banana", "cherry"]

# 访问元素
print(fruits[0])   # apple
print(fruits[-1])  # cherry（最后一个）

# 切片
print(fruits[0:2])  # ['apple', 'banana']
print(fruits[::2])  # 每隔一个取一个

# 添加元素
fruits.append("orange")      # 末尾添加
fruits.insert(1, "grape")    # 指定位置插入
fruits.extend(["mango", "kiwi"])  # 扩展列表

# 删除元素
fruits.remove("banana")  # 按值删除
del fruits[0]            # 按索引删除
popped = fruits.pop()    # 弹出最后一个

# 查找
index = fruits.index("cherry")  # 查找索引
count = fruits.count("apple")   # 统计出现次数

# 排序
fruits.sort()                # 原地排序
sorted_fruits = sorted(fruits)  # 返回新列表
fruits.reverse()             # 反转
```

### 列表推导式

列表推导式是创建列表的简洁方式：

```python
# 基本列表推导式
squares = [x**2 for x in range(10)]

# 带条件的列表推导式
even_squares = [x**2 for x in range(10) if x % 2 == 0]

# 嵌套列表推导式
matrix = [[i*j for j in range(3)] for i in range(3)]

# 多条件
filtered = [x for x in range(100) if x % 2 == 0 if x % 3 == 0]
```

## 元组 (Tuple)

元组是有序、不可变的元素集合。一旦创建就不能修改。

### 创建元组

```python
# 空元组
empty_tuple = ()
empty_tuple = tuple()

# 带初始值的元组
coordinates = (10, 20)
single = (42,)  # 单元素元组需要逗号

# 不带括号
point = 10, 20, 30
```

### 元组操作

```python
person = ("Alice", 25, "Engineer")

# 访问元素
name = person[0]
age = person[1]

# 解包
name, age, job = person

# 部分解包
first, *rest = (1, 2, 3, 4, 5)  # first=1, rest=[2,3,4,5]

# 元组方法
count = person.count("Alice")
index = person.index(25)

# 元组不可变，以下会报错
# person[0] = "Bob"  # TypeError
```

### 命名元组

使用 namedtuple 创建具名元组，提高可读性：

```python
from collections import namedtuple

Point = namedtuple('Point', ['x', 'y'])
p = Point(10, 20)

print(p.x)  # 10
print(p.y)  # 20
print(p[0]) # 10
```

## 字典 (Dict)

字典是键值对的集合，键必须是不可变类型且唯一。

### 创建字典

```python
# 空字典
empty_dict = {}
empty_dict = dict()

# 带初始值的字典
person = {
    "name": "Alice",
    "age": 25,
    "city": "Beijing"
}

# 从键值对创建
pairs = [("a", 1), ("b", 2)]
d = dict(pairs)

# 字典推导式
squares = {x: x**2 for x in range(5)}
```

### 字典操作

```python
person = {"name": "Alice", "age": 25}

# 访问值
name = person["name"]
age = person.get("age")
city = person.get("city", "Unknown")  # 带默认值

# 添加/修改
person["email"] = "alice@example.com"
person["age"] = 26

# 删除
del person["email"]
age = person.pop("age")
item = person.popitem()  # 删除最后一个

# 遍历
for key in person:
    print(key)

for key, value in person.items():
    print(f"{key}: {value}")

for value in person.values():
    print(value)

# 合并字典（Python 3.9+）
dict1 = {"a": 1, "b": 2}
dict2 = {"c": 3, "d": 4}
merged = dict1 | dict2
```

### defaultdict

defaultdict 自动为不存在的键创建默认值：

```python
from collections import defaultdict

# 计数器
counter = defaultdict(int)
for char in "hello":
    counter[char] += 1

# 分组
groups = defaultdict(list)
data = [("a", 1), ("b", 2), ("a", 3)]
for key, value in data:
    groups[key].append(value)
```

## 集合 (Set)

集合是无序、不重复元素的集合。

### 创建集合

```python
# 空集合
empty_set = set()  # 注意：{} 创建的是空字典

# 带初始值的集合
numbers = {1, 2, 3, 4, 5}
unique = set([1, 1, 2, 2, 3])  # {1, 2, 3}

# 集合推导式
even = {x for x in range(10) if x % 2 == 0}
```

### 集合操作

```python
a = {1, 2, 3, 4}
b = {3, 4, 5, 6}

# 添加/删除
a.add(5)
a.remove(1)      # 不存在会报错
a.discard(10)    # 不存在不报错
popped = a.pop() # 随机删除一个

# 集合运算
union = a | b         # 并集: {1, 2, 3, 4, 5, 6}
intersection = a & b  # 交集: {3, 4}
difference = a - b    # 差集: {1, 2}
sym_diff = a ^ b      # 对称差集: {1, 2, 5, 6}

# 关系判断
a.issubset(b)      # 子集判断
a.issuperset(b)    # 超集判断
a.isdisjoint(b)    # 是否无交集
```

### frozenset

frozenset 是不可变的集合，可以作为字典的键：

```python
frozen = frozenset([1, 2, 3])
# frozen.add(4)  # 报错，不可修改

# 作为字典键
cache = {frozen: "cached_value"}
```

## 数据结构选择指南

| 场景 | 推荐数据结构 |
|------|-------------|
| 有序集合，需要修改 | list |
| 有序集合，不需要修改 | tuple |
| 键值映射 | dict |
| 去重 | set |
| 计数 | collections.Counter |
| 队列 | collections.deque |
| 有序字典 | dict (Python 3.7+) |

## 性能对比

| 操作 | list | dict | set |
|------|------|------|-----|
| 查找 | O(n) | O(1) | O(1) |
| 插入 | O(n) | O(1) | O(1) |
| 删除 | O(n) | O(1) | O(1) |
| 索引访问 | O(1) | O(1) | N/A |

选择合适的数据结构对程序性能至关重要。
