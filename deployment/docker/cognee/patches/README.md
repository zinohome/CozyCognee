# CozyCognee 补丁文件

此目录包含对官方 Cognee 代码的补丁文件，用于在 Docker 镜像构建时替换官方代码。

## 补丁说明

### `cognee/api/client.py`

**修改内容**: 增强 CORS 配置，支持 `CORS_ALLOWED_ORIGINS=*` 来允许所有来源。

**修改原因**: 官方代码不支持 `*` 通配符，需要明确列出所有允许的来源。此补丁允许使用 `*` 来允许所有来源（适用于开发/测试环境）。

**使用方法**: 
- 在 `docker-compose.1panel.yml` 中设置 `CORS_ALLOWED_ORIGINS=*`
- 或使用具体的 URL 列表：`CORS_ALLOWED_ORIGINS=http://example.com,http://another.com`

**注意事项**: 
- 使用 `*` 时，`allow_credentials` 会自动设置为 `False`（浏览器安全限制）
- 生产环境建议使用具体的 URL 列表而不是 `*`

## 目录结构

```
patches/
└── cognee/
    └── api/
        └── client.py  # CORS 配置补丁
```

## 应用补丁

补丁文件在 Dockerfile 中自动应用：

```dockerfile
# Apply CozyCognee patches (CORS configuration)
COPY deployment/docker/cognee/patches/cognee/api/client.py /app/cognee/api/client.py
```

## 维护说明

当官方代码更新时：
1. 检查补丁文件是否需要更新
2. 如果官方代码已经包含相同功能，可以删除补丁文件
3. 更新此 README 文件

