# Python 面向对象与设计模式

面向对象编程（OOP）是 Python 的核心范式之一。本文介绍 Python 的 OOP 特性和常用设计模式。

## 类与对象基础

### 定义类

```python
class Dog:
    # 类属性（所有实例共享）
    species = "Canis familiaris"
    
    # 初始化方法
    def __init__(self, name, age):
        # 实例属性
        self.name = name
        self.age = age
    
    # 实例方法
    def bark(self):
        return f"{self.name} says woof!"
    
    # 类方法
    @classmethod
    def create_puppy(cls, name):
        return cls(name, 0)
    
    # 静态方法
    @staticmethod
    def is_valid_age(age):
        return 0 <= age <= 30

# 创建实例
dog = Dog("Buddy", 3)
print(dog.bark())  # Buddy says woof!
```

### 特殊方法（魔术方法）

```python
class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __repr__(self):
        return f"Vector({self.x}, {self.y})"
    
    def __str__(self):
        return f"({self.x}, {self.y})"
    
    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)
    
    def __mul__(self, scalar):
        return Vector(self.x * scalar, self.y * scalar)
    
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    
    def __len__(self):
        return int((self.x**2 + self.y**2)**0.5)
    
    def __iter__(self):
        yield self.x
        yield self.y

v1 = Vector(1, 2)
v2 = Vector(3, 4)
print(v1 + v2)  # (4, 6)
print(v1 * 3)   # (3, 6)
```

## 封装

### 属性访问控制

```python
class BankAccount:
    def __init__(self, owner, balance=0):
        self.owner = owner          # 公开属性
        self._balance = balance     # 受保护属性（约定）
        self.__pin = "1234"         # 私有属性（名称改写）
    
    @property
    def balance(self):
        """只读属性"""
        return self._balance
    
    @property
    def pin(self):
        return "****"  # 隐藏真实值
    
    def deposit(self, amount):
        if amount > 0:
            self._balance += amount
    
    def withdraw(self, amount):
        if 0 < amount <= self._balance:
            self._balance -= amount
            return amount
        raise ValueError("无效的取款金额")

account = BankAccount("Alice", 1000)
print(account.balance)  # 1000
# account.balance = 500  # AttributeError
```

### property 装饰器

```python
class Temperature:
    def __init__(self, celsius=0):
        self._celsius = celsius
    
    @property
    def celsius(self):
        return self._celsius
    
    @celsius.setter
    def celsius(self, value):
        if value < -273.15:
            raise ValueError("温度不能低于绝对零度")
        self._celsius = value
    
    @property
    def fahrenheit(self):
        return self._celsius * 9/5 + 32
    
    @fahrenheit.setter
    def fahrenheit(self, value):
        self.celsius = (value - 32) * 5/9

temp = Temperature(25)
print(temp.fahrenheit)  # 77.0
temp.fahrenheit = 100
print(temp.celsius)     # 37.78
```

## 继承

### 单继承

```python
class Animal:
    def __init__(self, name):
        self.name = name
    
    def speak(self):
        raise NotImplementedError

class Dog(Animal):
    def speak(self):
        return f"{self.name} says woof!"

class Cat(Animal):
    def speak(self):
        return f"{self.name} says meow!"

# 使用
dog = Dog("Buddy")
cat = Cat("Whiskers")
print(dog.speak())  # Buddy says woof!
print(cat.speak())  # Whiskers says meow!
```

### 多继承

```python
class Flyable:
    def fly(self):
        return "I can fly!"

class Swimmable:
    def swim(self):
        return "I can swim!"

class Duck(Animal, Flyable, Swimmable):
    def speak(self):
        return f"{self.name} says quack!"

duck = Duck("Donald")
print(duck.speak())  # Donald says quack!
print(duck.fly())    # I can fly!
print(duck.swim())   # I can swim!
```

### super() 函数

```python
class Base:
    def __init__(self, x):
        self.x = x
        print(f"Base.__init__({x})")

class Child(Base):
    def __init__(self, x, y):
        super().__init__(x)  # 调用父类初始化
        self.y = y
        print(f"Child.__init__({x}, {y})")

child = Child(1, 2)
```

### 方法解析顺序 (MRO)

```python
class A:
    def method(self):
        print("A")

class B(A):
    def method(self):
        print("B")
        super().method()

class C(A):
    def method(self):
        print("C")
        super().method()

class D(B, C):
    def method(self):
        print("D")
        super().method()

print(D.__mro__)  # 查看方法解析顺序
d = D()
d.method()  # D -> B -> C -> A
```

## 多态

### 鸭子类型

```python
def make_sound(animal):
    """只要有 speak 方法就能用"""
    print(animal.speak())

class Robot:
    def speak(self):
        return "Beep boop!"

# Robot 不继承 Animal，但有 speak 方法
make_sound(Dog("Buddy"))    # Buddy says woof!
make_sound(Robot())         # Beep boop!
```

### 抽象基类

```python
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self):
        pass
    
    @abstractmethod
    def perimeter(self):
        pass

class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height
    
    def area(self):
        return self.width * self.height
    
    def perimeter(self):
        return 2 * (self.width + self.height)

# shape = Shape()  # TypeError: 不能实例化抽象类
rect = Rectangle(5, 3)
print(rect.area())  # 15
```

## 常用设计模式

### 单例模式

确保类只有一个实例：

```python
class Singleton:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

# 使用装饰器实现
def singleton(cls):
    instances = {}
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return get_instance

@singleton
class Database:
    def __init__(self):
        self.connection = "Connected"

db1 = Database()
db2 = Database()
print(db1 is db2)  # True
```

### 工厂模式

创建对象而不暴露创建逻辑：

```python
class Animal:
    def speak(self):
        raise NotImplementedError

class Dog(Animal):
    def speak(self):
        return "Woof!"

class Cat(Animal):
    def speak(self):
        return "Meow!"

class AnimalFactory:
    @staticmethod
    def create(animal_type):
        animals = {
            "dog": Dog,
            "cat": Cat
        }
        if animal_type not in animals:
            raise ValueError(f"Unknown animal type: {animal_type}")
        return animals[animal_type]()

# 使用
dog = AnimalFactory.create("dog")
cat = AnimalFactory.create("cat")
```

### 策略模式

定义一系列算法，使它们可以互换：

```python
from abc import ABC, abstractmethod

class PaymentStrategy(ABC):
    @abstractmethod
    def pay(self, amount):
        pass

class CreditCardPayment(PaymentStrategy):
    def __init__(self, card_number):
        self.card_number = card_number
    
    def pay(self, amount):
        return f"Paid {amount} using Credit Card {self.card_number[-4:]}"

class PayPalPayment(PaymentStrategy):
    def __init__(self, email):
        self.email = email
    
    def pay(self, amount):
        return f"Paid {amount} using PayPal ({self.email})"

class ShoppingCart:
    def __init__(self):
        self.items = []
        self.payment_strategy = None
    
    def set_payment_strategy(self, strategy):
        self.payment_strategy = strategy
    
    def checkout(self, amount):
        if self.payment_strategy:
            return self.payment_strategy.pay(amount)
        raise ValueError("No payment strategy set")

# 使用
cart = ShoppingCart()
cart.set_payment_strategy(CreditCardPayment("1234-5678-9012-3456"))
print(cart.checkout(100))  # Paid 100 using Credit Card 3456
```

### 观察者模式

当对象状态改变时通知依赖对象：

```python
class Subject:
    def __init__(self):
        self._observers = []
        self._state = None
    
    def attach(self, observer):
        self._observers.append(observer)
    
    def detach(self, observer):
        self._observers.remove(observer)
    
    def notify(self):
        for observer in self._observers:
            observer.update(self)
    
    @property
    def state(self):
        return self._state
    
    @state.setter
    def state(self, value):
        self._state = value
        self.notify()

class Observer:
    def update(self, subject):
        raise NotImplementedError

class EmailNotifier(Observer):
    def update(self, subject):
        print(f"Email: State changed to {subject.state}")

class SMSNotifier(Observer):
    def update(self, subject):
        print(f"SMS: State changed to {subject.state}")

# 使用
subject = Subject()
subject.attach(EmailNotifier())
subject.attach(SMSNotifier())
subject.state = "Active"
# Email: State changed to Active
# SMS: State changed to Active
```

### 装饰器模式

动态添加功能：

```python
class Coffee:
    def cost(self):
        return 5
    
    def description(self):
        return "Coffee"

class CoffeeDecorator(Coffee):
    def __init__(self, coffee):
        self._coffee = coffee
    
    def cost(self):
        return self._coffee.cost()
    
    def description(self):
        return self._coffee.description()

class MilkDecorator(CoffeeDecorator):
    def cost(self):
        return self._coffee.cost() + 2
    
    def description(self):
        return self._coffee.description() + " + Milk"

class SugarDecorator(CoffeeDecorator):
    def cost(self):
        return self._coffee.cost() + 1
    
    def description(self):
        return self._coffee.description() + " + Sugar"

# 使用
coffee = Coffee()
coffee = MilkDecorator(coffee)
coffee = SugarDecorator(coffee)
print(coffee.description())  # Coffee + Milk + Sugar
print(coffee.cost())         # 8
```

### 依赖注入

降低组件之间的耦合：

```python
class EmailService:
    def send(self, to, message):
        print(f"Sending email to {to}: {message}")

class SMSService:
    def send(self, to, message):
        print(f"Sending SMS to {to}: {message}")

class NotificationManager:
    def __init__(self, notification_service):
        # 依赖通过构造函数注入
        self.service = notification_service
    
    def notify(self, user, message):
        self.service.send(user, message)

# 使用不同的服务
email_manager = NotificationManager(EmailService())
email_manager.notify("alice@example.com", "Hello!")

sms_manager = NotificationManager(SMSService())
sms_manager.notify("123-456-7890", "Hello!")
```

## dataclass

简化数据类的创建：

```python
from dataclasses import dataclass, field
from typing import List

@dataclass
class Product:
    name: str
    price: float
    quantity: int = 0
    tags: List[str] = field(default_factory=list)
    
    def total_value(self):
        return self.price * self.quantity

@dataclass(frozen=True)  # 不可变
class Point:
    x: float
    y: float

# 自动生成 __init__, __repr__, __eq__ 等
product = Product("Apple", 1.5, 10)
print(product)  # Product(name='Apple', price=1.5, quantity=10, tags=[])
```

## 元类

元类是创建类的类：

```python
class SingletonMeta(type):
    _instances = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class Database(metaclass=SingletonMeta):
    def __init__(self):
        self.connection = "Connected"

db1 = Database()
db2 = Database()
print(db1 is db2)  # True
```

## 总结

- OOP 的三大特性：封装、继承、多态
- 使用 property 实现属性访问控制
- 抽象基类定义接口规范
- 设计模式提供经过验证的解决方案
- dataclass 简化数据类的创建
- 选择合适的设计模式解决特定问题
