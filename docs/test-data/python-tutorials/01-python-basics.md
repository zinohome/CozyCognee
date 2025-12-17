# Python 基础语法

Python 是一种高级、解释型、通用的编程语言。它由 Guido van Rossum 于 1991 年创建，强调代码可读性和简洁性。

## 变量与数据类型

### 基本数据类型

Python 有以下几种基本数据类型：

**整数 (int)**：表示整数值，没有大小限制。

```python
age = 25
count = -100
big_number = 10000000000000000000
```

**浮点数 (float)**：表示小数值，使用 IEEE 754 双精度格式。

```python
price = 19.99
temperature = -3.5
pi = 3.14159265359
```

**字符串 (str)**：表示文本数据，使用单引号或双引号。

```python
name = "Python"
message = 'Hello, World!'
multiline = """这是
多行字符串"""
```

**布尔值 (bool)**：表示真或假。

```python
is_active = True
is_empty = False
```

### 变量命名规则

Python 变量命名需要遵循以下规则：
1. 变量名只能包含字母、数字和下划线
2. 变量名不能以数字开头
3. 变量名区分大小写
4. 不能使用 Python 保留关键字

推荐使用 snake_case 命名风格：

```python
user_name = "Alice"
total_count = 100
is_valid_input = True
```

## 运算符

### 算术运算符

```python
a = 10
b = 3

print(a + b)   # 加法: 13
print(a - b)   # 减法: 7
print(a * b)   # 乘法: 30
print(a / b)   # 除法: 3.333...
print(a // b)  # 整除: 3
print(a % b)   # 取余: 1
print(a ** b)  # 幂运算: 1000
```

### 比较运算符

```python
x = 5
y = 10

print(x == y)  # 等于: False
print(x != y)  # 不等于: True
print(x < y)   # 小于: True
print(x > y)   # 大于: False
print(x <= y)  # 小于等于: True
print(x >= y)  # 大于等于: False
```

### 逻辑运算符

```python
a = True
b = False

print(a and b)  # 与: False
print(a or b)   # 或: True
print(not a)    # 非: False
```

## 控制流语句

### if-elif-else 条件语句

条件语句用于根据条件执行不同的代码块：

```python
score = 85

if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
elif score >= 70:
    grade = "C"
elif score >= 60:
    grade = "D"
else:
    grade = "F"

print(f"成绩等级: {grade}")
```

### for 循环

for 循环用于遍历可迭代对象：

```python
# 遍历列表
fruits = ["apple", "banana", "cherry"]
for fruit in fruits:
    print(fruit)

# 使用 range
for i in range(5):
    print(i)  # 输出 0, 1, 2, 3, 4

# 带索引遍历
for index, fruit in enumerate(fruits):
    print(f"{index}: {fruit}")
```

### while 循环

while 循环在条件为真时持续执行：

```python
count = 0
while count < 5:
    print(count)
    count += 1
```

### 循环控制

使用 break 和 continue 控制循环流程：

```python
# break 终止循环
for i in range(10):
    if i == 5:
        break
    print(i)

# continue 跳过当前迭代
for i in range(10):
    if i % 2 == 0:
        continue
    print(i)  # 只打印奇数
```

## 输入输出

### 输出

使用 print() 函数输出内容：

```python
# 基本输出
print("Hello, World!")

# 格式化输出 - f-string（推荐）
name = "Python"
version = 3.11
print(f"{name} version {version}")

# format 方法
print("{} version {}".format(name, version))

# % 格式化（旧式）
print("%s version %.2f" % (name, version))
```

### 输入

使用 input() 函数获取用户输入：

```python
name = input("请输入您的名字: ")
age = int(input("请输入您的年龄: "))
print(f"你好，{name}！你 {age} 岁了。")
```

## 注释

Python 支持单行注释和多行注释：

```python
# 这是单行注释

"""
这是多行注释
可以跨越多行
通常用于文档字符串
"""

def greet(name):
    """
    向用户问好
    
    Args:
        name: 用户名字
    
    Returns:
        问候字符串
    """
    return f"Hello, {name}!"
```

## 总结

Python 基础语法特点：
- 使用缩进表示代码块，而非花括号
- 动态类型，变量无需声明类型
- 语法简洁清晰，接近自然语言
- 丰富的内置数据类型和运算符
- 强大的控制流语句
