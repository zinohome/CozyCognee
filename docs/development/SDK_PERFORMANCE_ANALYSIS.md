# SDK 性能分析与优化方案

## 📊 问题分析

### 当前性能差异

**SDK方式（HTTP API）** vs **直接安装cognee包方式（本地调用）**

性能差异的主要原因：

1. **网络延迟** - 每次请求都需要网络往返
2. **HTTP协议开销** - 请求头、响应头、状态码等
3. **序列化/反序列化** - JSON编码/解码、multipart编码
4. **连接建立** - TCP握手、TLS握手（如果使用HTTPS）
5. **数据重复传输** - 客户端准备数据，服务器接收数据

### 性能瓶颈分析

#### 1. 网络层开销

```
直接调用: 函数调用 → 内存操作 → 返回结果
         [0-1ms]

SDK调用:  函数调用 → 序列化 → 网络传输 → 服务器处理 → 网络传输 → 反序列化 → 返回结果
         [10-100ms+]
```

**典型延迟**：
- 本地网络：1-5ms
- 局域网：5-20ms
- 互联网：50-200ms+

#### 2. HTTP协议开销

每个请求包含：
- 请求头：~200-500 bytes
- 响应头：~200-500 bytes
- HTTP状态码、方法等元数据

#### 3. 序列化开销

- JSON编码/解码：小数据（<1KB）约0.1-1ms，大数据（>1MB）约10-100ms
- Multipart编码：文件上传需要额外的编码开销

#### 4. 连接管理

- 每次请求可能需要建立新连接（如果没有连接池）
- TLS握手：首次连接需要额外的100-500ms

## 🎯 优化方案

### 方案1: 连接池优化（已实现，可进一步优化）

**当前实现**：
```python
self.client = httpx.AsyncClient(
    timeout=httpx.Timeout(timeout, connect=10.0),
    limits=httpx.Limits(
        max_keepalive_connections=10,
        max_connections=20
    ),
    follow_redirects=True
)
```

**优化建议**：

1. **增加连接池大小**
   ```python
   limits=httpx.Limits(
       max_keepalive_connections=50,  # 从10增加到50
       max_connections=100,            # 从20增加到100
   )
   ```

2. **HTTP/2支持**
   ```python
   http2=True,  # 启用HTTP/2，支持多路复用
   ```

3. **连接复用策略**
   - 使用单例客户端（全局共享）
   - 实现连接预热
   - 智能连接管理

### 方案2: 批量操作优化（已实现，可进一步优化）

**当前实现**：
- `add_batch()` 支持批量操作
- 使用 `asyncio.Semaphore` 控制并发

**优化建议**：

1. **智能批处理**
   ```python
   async def add_batch_optimized(
       self,
       data_list: list[...],
       batch_size: int = 100,  # 自动分批
       max_concurrent: int = 20
   ):
       # 自动将大数据集分批处理
       # 每批内部并发，批次之间顺序执行
   ```

2. **服务器端批量API**
   - 实现服务器端批量处理端点
   - 减少HTTP请求次数
   - 服务器端可以优化处理流程

### 方案3: 数据压缩

**实现**：
```python
import gzip
import json

# 请求压缩
headers = {
    "Content-Encoding": "gzip",
    "Accept-Encoding": "gzip"
}

# 压缩请求体
if len(json_data) > 1024:  # 大于1KB才压缩
    compressed = gzip.compress(json.dumps(data).encode())
    # 发送压缩数据
```

**收益**：
- 减少网络传输时间（特别是大数据）
- 减少带宽使用
- 对于文本数据，压缩率通常可达70-90%

### 方案4: 流式传输优化（已部分实现）

**当前实现**：
- 大文件（>10MB）使用流式上传

**优化建议**：

1. **更激进的流式策略**
   ```python
   STREAMING_THRESHOLD = 1 * 1024 * 1024  # 从10MB降低到1MB
   ```

2. **分块上传**
   - 大文件分块上传
   - 支持断点续传
   - 并行上传多个块

3. **服务器端流式处理**
   - 服务器端边接收边处理
   - 减少服务器内存使用
   - 提高响应速度

### 方案5: 本地缓存

**实现**：
```python
from functools import lru_cache
import hashlib

class CachedCogneeClient(CogneeClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cache = {}
        self._cache_ttl = 300  # 5分钟
    
    async def search(self, query: str, **kwargs):
        # 生成缓存键
        cache_key = hashlib.md5(
            f"{query}:{kwargs}".encode()
        ).hexdigest()
        
        # 检查缓存
        if cache_key in self._cache:
            cached_result, timestamp = self._cache[cache_key]
            if time.time() - timestamp < self._cache_ttl:
                return cached_result
        
        # 调用API
        result = await super().search(query, **kwargs)
        
        # 更新缓存
        self._cache[cache_key] = (result, time.time())
        return result
```

**适用场景**：
- 搜索查询（相同查询可能返回相同结果）
- 数据集列表（不经常变化）
- 健康检查（频繁调用但结果相同）

### 方案6: 请求合并

**实现**：
```python
class RequestBatcher:
    """将多个请求合并为单个请求"""
    
    async def batch_requests(self, requests: list[Request]):
        # 将多个请求合并为单个批量请求
        # 服务器端并行处理
        # 返回合并结果
        pass
```

**示例**：
```python
# 之前：3个独立请求
await client.add("data1", dataset_name="test")
await client.add("data2", dataset_name="test")
await client.add("data3", dataset_name="test")

# 优化后：1个批量请求
await client.add_batch(["data1", "data2", "data3"], dataset_name="test")
```

### 方案7: 异步并发优化

**当前实现**：
- 使用 `asyncio.gather()` 进行并发

**优化建议**：

1. **智能并发控制**
   ```python
   async def add_batch_smart(
       self,
       data_list: list[...],
       adaptive_concurrency: bool = True
   ):
       if adaptive_concurrency:
           # 根据数据大小和网络延迟动态调整并发数
           if avg_data_size > 1MB:
               max_concurrent = 5  # 大文件降低并发
           else:
               max_concurrent = 20  # 小文件提高并发
   ```

2. **优先级队列**
   - 重要请求优先处理
   - 后台任务降低优先级

### 方案8: 协议优化

#### HTTP/2 多路复用

```python
self.client = httpx.AsyncClient(
    http2=True,  # 启用HTTP/2
    limits=httpx.Limits(
        max_keepalive_connections=100,
        max_connections=200
    )
)
```

**收益**：
- 单个连接可以处理多个请求
- 减少连接建立开销
- 服务器推送（如果支持）

#### WebSocket 长连接

对于频繁的交互操作，使用WebSocket：

```python
async def cognify_with_websocket(self, ...):
    # 使用WebSocket进行实时通信
    # 减少HTTP开销
    # 支持服务器推送进度更新
    pass
```

### 方案9: 本地混合模式（高级）

**实现本地+远程混合模式**：

```python
class HybridCogneeClient:
    """混合模式：本地处理 + 远程API"""
    
    def __init__(self, local_cognee=None, remote_client=None):
        self.local = local_cognee  # 直接安装的cognee包
        self.remote = remote_client  # SDK客户端
    
    async def add(self, data, **kwargs):
        # 判断是否应该本地处理
        if self._should_use_local(data):
            return await self.local.add(data, **kwargs)
        else:
            return await self.remote.add(data, **kwargs)
    
    def _should_use_local(self, data):
        # 判断条件：
        # 1. 数据大小（小数据本地处理）
        # 2. 网络延迟（高延迟时本地处理）
        # 3. 操作类型（某些操作必须远程）
        pass
```

**适用场景**：
- 开发环境：使用本地模式
- 生产环境：使用远程API
- 混合：根据条件自动选择

### 方案10: 预取和预加载

**实现**：
```python
class PrefetchClient(CogneeClient):
    """预取客户端"""
    
    async def search_with_prefetch(self, query: str, **kwargs):
        # 执行搜索
        results = await self.search(query, **kwargs)
        
        # 预取相关数据
        if results:
            # 后台预取相关数据集
            asyncio.create_task(
                self._prefetch_related_data(results)
            )
        
        return results
```

## 📈 性能优化优先级

### 高优先级（立即实施）

1. ✅ **连接池优化** - 增加连接数，启用HTTP/2
2. ✅ **批量操作** - 已实现，可进一步优化
3. ⚠️ **数据压缩** - 实现请求/响应压缩
4. ⚠️ **流式传输** - 降低流式阈值，优化大文件处理

### 中优先级（短期实施）

5. ⚠️ **本地缓存** - 实现智能缓存策略
6. ⚠️ **请求合并** - 实现请求批处理
7. ⚠️ **异步并发优化** - 智能并发控制

### 低优先级（长期规划）

8. ⚠️ **WebSocket长连接** - 对于频繁交互
9. ⚠️ **混合模式** - 本地+远程混合
10. ⚠️ **预取和预加载** - 智能预取策略

## 🔧 实施建议

### 阶段1: 快速优化（1-2天）

1. 增加连接池大小
2. 启用HTTP/2
3. 实现数据压缩
4. 优化流式传输阈值

**预期收益**：性能提升 20-40%

### 阶段2: 中期优化（1周）

1. 实现本地缓存
2. 优化批量操作
3. 智能并发控制

**预期收益**：性能提升 40-60%

### 阶段3: 长期优化（1个月）

1. 实现混合模式
2. WebSocket支持
3. 预取和预加载

**预期收益**：性能提升 60-80%

## 📊 性能基准测试

### 测试场景

1. **小数据添加**（<1KB）
   - 直接调用：~1ms
   - SDK当前：~10-50ms
   - SDK优化后目标：~5-20ms

2. **中等数据添加**（1MB）
   - 直接调用：~10ms
   - SDK当前：~100-200ms
   - SDK优化后目标：~50-100ms

3. **大数据添加**（100MB）
   - 直接调用：~500ms
   - SDK当前：~5-10s
   - SDK优化后目标：~2-5s

4. **批量操作**（100条数据）
   - 直接调用：~100ms
   - SDK当前：~5-10s
   - SDK优化后目标：~1-2s

## 🎯 目标

**最终目标**：SDK方式性能达到直接调用的 **50-80%**

- 小数据操作：达到直接调用的 80%
- 中等数据操作：达到直接调用的 70%
- 大数据操作：达到直接调用的 60%
- 批量操作：达到直接调用的 70%

## 📝 注意事项

1. **网络延迟是硬限制**：无法完全消除
2. **序列化开销**：对于大数据，这是主要瓶颈
3. **服务器性能**：优化客户端的同时，也要优化服务器
4. **权衡**：某些优化可能增加代码复杂度

## 🔍 监控和测量

实现性能监控：

```python
class PerformanceMonitor:
    """性能监控"""
    
    def track_request(self, method, endpoint, duration):
        # 记录请求性能
        pass
    
    def get_performance_report(self):
        # 生成性能报告
        pass
```

---

**文档版本**: 1.0
**创建时间**: 2025-12-08
**最后更新**: 2025-12-08
