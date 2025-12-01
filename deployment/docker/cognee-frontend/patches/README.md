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

### `InstanceDatasetsAccordion.tsx`

**修改内容**: 禁用自动检测 cloud 连接

**修改原因**: 在本地部署时，前端会自动检测 cloud 连接，导致出现 `CloudApiKeyMissingError` 错误。通过补丁禁用自动检测，避免不必要的错误。

**配置选项**:
- 通过环境变量 `NEXT_PUBLIC_DISABLE_CLOUD_CHECK` 控制
- `NEXT_PUBLIC_DISABLE_CLOUD_CHECK=true` - 禁用自动检测（默认）
- `NEXT_PUBLIC_DISABLE_CLOUD_CHECK=false` 或不设置 - 启用自动检测

**使用方法**: 
- 补丁在 Dockerfile 构建时自动应用
- Dockerfile 中默认设置 `NEXT_PUBLIC_DISABLE_CLOUD_CHECK=true` 来禁用自动检测
- 如需启用，可以在 docker-compose 文件中覆盖此环境变量：
  ```yaml
  environment:
    - NEXT_PUBLIC_DISABLE_CLOUD_CHECK=false
  ```

**注意事项**: 
- 禁用自动检测后，用户仍可以手动点击连接 cloud
- 此补丁仅影响自动检测，不影响手动连接功能

### `Header.tsx`

**修改内容**: 删除 Sync 按钮、Premium 链接和 API keys 链接

**修改原因**: 在本地部署时，这些功能通常不需要，删除它们可以简化用户界面。

**删除的元素**:
- Sync 按钮及其相关的同步模态框
- Premium 链接（指向 `/plan`）
- API keys 链接（指向 `https://platform.cognee.ai`）

**使用方法**: 
- 补丁在 Dockerfile 构建时自动应用
- 无需额外配置

**注意事项**: 
- 删除 Sync 按钮后，用户无法通过 UI 同步本地数据集到云端
- 删除 Premium 和 API keys 链接后，用户需要通过其他方式访问这些功能

### `Dashboard.tsx`

**修改内容**: 删除 "Select a plan" 按钮

**修改原因**: 在本地部署时，通常不需要显示选择计划的按钮，删除它可以简化用户界面。

**删除的元素**:
- 位于左侧边栏底部的 "Select a plan" 按钮

**使用方法**: 
- 补丁在 Dockerfile 构建时自动应用
- 无需额外配置

**注意事项**: 
- 删除后，用户无法从 Dashboard 页面直接跳转到计划选择页面

### `Account.tsx`

**修改内容**: 删除 "Select a plan" 按钮

**修改原因**: 在本地部署时，通常不需要显示选择计划的按钮，删除它可以简化用户界面。

**删除的元素**:
- 位于账户页面 Plan 部分的 "Select a plan" 按钮

**使用方法**: 
- 补丁在 Dockerfile 构建时自动应用
- 无需额外配置

**注意事项**: 
- 删除后，用户无法从 Account 页面直接跳转到计划选择页面

## 目录结构

```
patches/
├── next.config.mjs  # Next.js 配置补丁
├── InstanceDatasetsAccordion.tsx  # 禁用 cloud 连接自动检测补丁
├── Header.tsx  # 删除 Sync 按钮、Premium 链接和 API keys 链接补丁
├── Dashboard.tsx  # 删除 "Select a plan" 按钮补丁
└── Account.tsx  # 删除 "Select a plan" 按钮补丁
```

## 应用补丁

补丁文件在 Dockerfile 中自动应用：

```dockerfile
# Apply CozyCognee patches: 使用补丁版本的 next.config.mjs 来禁用 devIndicators
COPY deployment/docker/cognee-frontend/patches/next.config.mjs ./next.config.mjs
# Apply CozyCognee patches: 使用补丁版本的 InstanceDatasetsAccordion.tsx 来禁用自动 cloud 连接检测
COPY deployment/docker/cognee-frontend/patches/InstanceDatasetsAccordion.tsx ./src/app/dashboard/InstanceDatasetsAccordion.tsx
# Apply CozyCognee patches: 使用补丁版本的 Header.tsx 来删除 Sync 按钮、Premium 链接和 API keys 链接
COPY deployment/docker/cognee-frontend/patches/Header.tsx ./src/ui/Layout/Header.tsx
# Apply CozyCognee patches: 使用补丁版本的 Dashboard.tsx 来删除 "Select a plan" 按钮
COPY deployment/docker/cognee-frontend/patches/Dashboard.tsx ./src/app/dashboard/Dashboard.tsx
# Apply CozyCognee patches: 使用补丁版本的 Account.tsx 来删除 "Select a plan" 按钮
COPY deployment/docker/cognee-frontend/patches/Account.tsx ./src/app/account/Account.tsx
```

## 维护说明

当官方代码更新时：
1. 检查补丁文件是否需要更新
2. 如果官方代码已经包含相同功能，可以删除补丁文件
3. 更新此 README 文件

