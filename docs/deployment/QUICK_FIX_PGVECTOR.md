# pgvector 扩展问题快速修复指南

## 🚨 问题描述

上传文件时出现错误：
```
Error: Conflict
extension "vector" is not available
Could not open extension control file "/usr/local/share/postgresql/extension/vector.control"
```

## ✅ 解决方案

### 步骤 1：备份数据（如果已有重要数据）

```bash
# 备份数据库
docker-compose -f deployment/docker-compose.1panel.yml exec postgres pg_dump -U cognee_user cognee_db > backup_$(date +%Y%m%d_%H%M%S).sql
```

### 步骤 2：停止服务

```bash
cd /path/to/CozyCognee
docker-compose -f deployment/docker-compose.1panel.yml down
```

### 步骤 3：修改配置（已完成）

`deployment/docker-compose.1panel.yml` 中的 `postgres` 服务已修改为：
```yaml
postgres:
  image: pgvector/pgvector:pg15  # 已改为带 pgvector 的镜像
```

### 步骤 4：启动 postgres 服务

```bash
docker-compose -f deployment/docker-compose.1panel.yml up -d postgres
```

### 步骤 5：等待数据库启动（约 10-30 秒）

```bash
# 检查数据库是否启动
docker-compose -f deployment/docker-compose.1panel.yml logs postgres | tail -20
```

### 步骤 6：验证 pgvector 扩展

```bash
# 连接到数据库并检查扩展
docker-compose -f deployment/docker-compose.1panel.yml exec postgres psql -U cognee_user -d cognee_db -c "\dx"
```

如果看到 `vector` 扩展，说明安装成功。

### 步骤 7：重启 cognee 服务

```bash
docker-compose -f deployment/docker-compose.1panel.yml restart cognee
```

### 步骤 8：验证修复

```bash
# 查看 cognee 日志，确认没有 pgvector 错误
docker-compose -f deployment/docker-compose.1panel.yml logs cognee | grep -i vector

# 测试上传文件
curl -X 'POST' \
  'http://192.168.66.11:8000/api/v1/add' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'data=@README.txt;type=text/plain' \
  -F 'datasetName=test' \
  -F 'node_set='
```

## 📝 注意事项

1. **数据迁移**：如果之前使用的是 `postgres:15-alpine`，切换到 `pgvector/pgvector:pg15` 后，数据会自动迁移，但建议先备份。

2. **版本兼容性**：
   - 原镜像：`postgres:15-alpine` (PostgreSQL 15)
   - 新镜像：`pgvector/pgvector:pg15` (PostgreSQL 15 + pgvector)
   - 版本兼容，数据可以直接使用

3. **如果遇到问题**：
   - 检查日志：`docker-compose -f deployment/docker-compose.1panel.yml logs postgres`
   - 检查 cognee 日志：`docker-compose -f deployment/docker-compose.1panel.yml logs cognee`

## 🔄 回滚方案

如果修复后出现问题，可以回滚：

```bash
# 停止服务
docker-compose -f deployment/docker-compose.1panel.yml down

# 恢复 docker-compose.1panel.yml 中的 postgres 镜像为 postgres:15-alpine

# 恢复数据（如果有备份）
docker-compose -f deployment/docker-compose.1panel.yml up -d postgres
# 然后恢复备份的 SQL 文件
```

## 📚 相关文档

- [详细日志分析](./LOG_ANALYSIS_AND_FIXES.md)
- [pgvector 配置指南](./PGVECTOR_SETUP.md)

