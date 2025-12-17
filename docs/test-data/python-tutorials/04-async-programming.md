# Python 异步编程

异步编程是处理 I/O 密集型任务的高效方式。Python 通过 asyncio 库提供原生异步支持。

## 异步编程概念

### 同步 vs 异步

**同步执行**：代码按顺序执行，每个操作必须等待前一个完成。

```python
import time

def sync_task(name, delay):
    print(f"开始 {name}")
    time.sleep(delay)
    print(f"完成 {name}")

# 同步执行，总耗时 3 秒
sync_task("任务1", 1)
sync_task("任务2", 2)
```

**异步执行**：多个操作可以并发执行，不必等待。

```python
import asyncio

async def async_task(name, delay):
    print(f"开始 {name}")
    await asyncio.sleep(delay)
    print(f"完成 {name}")

async def main():
    # 并发执行，总耗时约 2 秒
    await asyncio.gather(
        async_task("任务1", 1),
        async_task("任务2", 2)
    )

asyncio.run(main())
```

### 核心概念

**协程 (Coroutine)**：使用 `async def` 定义的函数，可以在执行过程中暂停和恢复。

**事件循环 (Event Loop)**：协调和调度所有协程的执行。

**await**：暂停协程执行，等待另一个协程完成。

## async/await 语法

### 定义协程

```python
async def fetch_data(url):
    """异步获取数据"""
    print(f"开始获取: {url}")
    await asyncio.sleep(1)  # 模拟网络请求
    return {"url": url, "data": "some data"}

async def main():
    result = await fetch_data("https://api.example.com")
    print(result)

asyncio.run(main())
```

### await 关键字

await 只能在 async 函数内使用：

```python
async def process():
    # 正确：await 异步函数
    result = await fetch_data("url")
    
    # 正确：await 可等待对象
    await asyncio.sleep(1)
    
    # 错误：不能 await 普通函数
    # result = await regular_function()  # TypeError
```

## 并发执行

### asyncio.gather

同时运行多个协程，返回所有结果：

```python
async def fetch_url(url):
    await asyncio.sleep(1)
    return f"Data from {url}"

async def main():
    urls = [
        "https://api1.example.com",
        "https://api2.example.com",
        "https://api3.example.com"
    ]
    
    # 并发获取所有 URL
    results = await asyncio.gather(*[fetch_url(url) for url in urls])
    
    for result in results:
        print(result)

asyncio.run(main())
```

### asyncio.create_task

创建任务并在后台运行：

```python
async def background_task():
    while True:
        print("后台任务运行中...")
        await asyncio.sleep(2)

async def main():
    # 创建后台任务
    task = asyncio.create_task(background_task())
    
    # 做其他事情
    await asyncio.sleep(5)
    
    # 取消任务
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        print("任务已取消")

asyncio.run(main())
```

### asyncio.wait

更精细的任务控制：

```python
async def main():
    tasks = [
        asyncio.create_task(fetch_url(url))
        for url in urls
    ]
    
    # 等待第一个完成
    done, pending = await asyncio.wait(
        tasks, 
        return_when=asyncio.FIRST_COMPLETED
    )
    
    # 或等待全部完成
    done, pending = await asyncio.wait(
        tasks,
        return_when=asyncio.ALL_COMPLETED
    )
```

## 超时处理

### asyncio.timeout

Python 3.11+ 推荐使用：

```python
async def slow_operation():
    await asyncio.sleep(10)
    return "完成"

async def main():
    try:
        async with asyncio.timeout(5):
            result = await slow_operation()
    except TimeoutError:
        print("操作超时")
```

### asyncio.wait_for

通用的超时包装：

```python
async def main():
    try:
        result = await asyncio.wait_for(
            slow_operation(),
            timeout=5.0
        )
    except asyncio.TimeoutError:
        print("操作超时")
```

## 异步迭代器和生成器

### 异步迭代器

```python
class AsyncCounter:
    def __init__(self, limit):
        self.limit = limit
        self.count = 0
    
    def __aiter__(self):
        return self
    
    async def __anext__(self):
        if self.count >= self.limit:
            raise StopAsyncIteration
        self.count += 1
        await asyncio.sleep(0.5)
        return self.count

async def main():
    async for num in AsyncCounter(5):
        print(num)
```

### 异步生成器

```python
async def async_range(start, stop):
    for i in range(start, stop):
        await asyncio.sleep(0.1)
        yield i

async def main():
    async for num in async_range(1, 6):
        print(num)
```

## 异步上下文管理器

```python
class AsyncResource:
    async def __aenter__(self):
        print("获取资源")
        await asyncio.sleep(0.5)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        print("释放资源")
        await asyncio.sleep(0.5)
    
    async def do_something(self):
        print("使用资源")

async def main():
    async with AsyncResource() as resource:
        await resource.do_something()
```

## 异步 HTTP 客户端

使用 httpx 或 aiohttp 进行异步 HTTP 请求：

### 使用 httpx

```python
import httpx

async def fetch_data(url):
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()

async def main():
    urls = [
        "https://api.github.com/users/python",
        "https://api.github.com/users/django",
    ]
    
    async with httpx.AsyncClient() as client:
        tasks = [client.get(url) for url in urls]
        responses = await asyncio.gather(*tasks)
        
    for response in responses:
        print(response.status_code)

asyncio.run(main())
```

## 信号量和锁

### 信号量限制并发

```python
async def fetch_with_limit(semaphore, url):
    async with semaphore:
        print(f"获取 {url}")
        await asyncio.sleep(1)
        return f"数据来自 {url}"

async def main():
    # 限制同时最多 3 个并发请求
    semaphore = asyncio.Semaphore(3)
    
    urls = [f"url_{i}" for i in range(10)]
    tasks = [fetch_with_limit(semaphore, url) for url in urls]
    results = await asyncio.gather(*tasks)
```

### 异步锁

```python
class AsyncCounter:
    def __init__(self):
        self.count = 0
        self.lock = asyncio.Lock()
    
    async def increment(self):
        async with self.lock:
            current = self.count
            await asyncio.sleep(0.01)  # 模拟处理
            self.count = current + 1

async def main():
    counter = AsyncCounter()
    
    # 并发增加 100 次
    await asyncio.gather(*[counter.increment() for _ in range(100)])
    print(counter.count)  # 100（没有竞态条件）
```

## 异步队列

```python
async def producer(queue):
    for i in range(5):
        await asyncio.sleep(0.5)
        await queue.put(f"item_{i}")
        print(f"生产: item_{i}")
    await queue.put(None)  # 结束信号

async def consumer(queue):
    while True:
        item = await queue.get()
        if item is None:
            break
        print(f"消费: {item}")
        queue.task_done()

async def main():
    queue = asyncio.Queue()
    
    await asyncio.gather(
        producer(queue),
        consumer(queue)
    )
```

## 错误处理

### 收集错误

```python
async def might_fail(n):
    if n == 3:
        raise ValueError(f"任务 {n} 失败")
    await asyncio.sleep(0.5)
    return n

async def main():
    tasks = [might_fail(i) for i in range(5)]
    
    # return_exceptions=True 收集异常而不是抛出
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    for result in results:
        if isinstance(result, Exception):
            print(f"错误: {result}")
        else:
            print(f"成功: {result}")
```

## 最佳实践

1. **只对 I/O 操作使用异步**：CPU 密集型任务应使用多进程
2. **避免阻塞调用**：在异步代码中不要使用 `time.sleep()`
3. **使用 asyncio.run()**：这是启动异步程序的推荐方式
4. **适当使用信号量**：限制并发数量，避免资源耗尽
5. **处理取消和超时**：异步任务应正确处理 CancelledError

## 总结

- 异步编程适合 I/O 密集型任务
- async/await 是 Python 异步编程的核心语法
- asyncio 提供了丰富的并发控制工具
- 合理使用锁和信号量避免竞态条件
- 异步 HTTP 客户端大幅提升网络请求效率
