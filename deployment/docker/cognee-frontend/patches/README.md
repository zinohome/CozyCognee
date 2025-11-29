# CozyCognee Frontend 补丁文件

此目录包含对官方 Cognee Frontend 代码的补丁文件，用于在 Docker 镜像构建时替换官方代码。

## 补丁说明

### `next.config.mjs`

**修改内容**: 禁用 Next.js 开发指示器（devIndicators）

**修改原因**: 隐藏左下角的开发工具指示器，提供更清洁的用户界面。

**配置选项**:
- 通过环境变量 `NEXT_DISABLE_DEV_INDICATORS` 控制
- `NEXT_DISABLE_DEV_INDICATORS=true` - 禁用开发指示器（默认）
- `NEXT_DISABLE_DEV_INDICATORS=false` 或不设置 - 启用开发指示器

**使用方法**: 
- 补丁在 Dockerfile 构建时自动应用
- Dockerfile 中默认设置 `NEXT_DISABLE_DEV_INDICATORS=true` 来禁用 devIndicators
- 如需启用，可以在 docker-compose 文件中覆盖此环境变量：
  ```yaml
  environment:
    - NEXT_DISABLE_DEV_INDICATORS=false
  ```

**注意事项**: 
- 此补丁仅在开发模式下有效（生产环境不会显示 devIndicators）
- Next.js 本身不支持通过环境变量控制 devIndicators，此补丁通过读取环境变量实现

## 目录结构

```
patches/
└── next.config.mjs  # Next.js 配置补丁
```

## 应用补丁

补丁文件在 Dockerfile 中自动应用：

```dockerfile
# Apply CozyCognee patches: 使用补丁版本的 next.config.mjs 来禁用 devIndicators
COPY deployment/docker/cognee-frontend/patches/next.config.mjs ./next.config.mjs
```

## 维护说明

当官方代码更新时：
1. 检查补丁文件是否需要更新
2. 如果官方代码已经包含相同功能，可以删除补丁文件
3. 更新此 README 文件

