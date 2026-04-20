# Use an official Node.js runtime as a parent image
FROM node:22-alpine

# Set the working directory to /app
WORKDIR /app

# Copy package.json and package-lock.json to the working directory
# 构建上下文是项目根目录，所以路径是 project/cognee/cognee-frontend/...
COPY project/cognee/cognee-frontend/package.json project/cognee/cognee-frontend/package-lock.json ./

# Install dependencies (npm install instead of npm ci: upstream lock file is out of sync with package.json)
RUN npm install
RUN npm rebuild lightningcss

# Copy the rest of the application code to the working directory
COPY project/cognee/cognee-frontend/src ./src
COPY project/cognee/cognee-frontend/public ./public

# Fix upstream case-sensitivity issue: upstream commit #2606 intended to rename
# PascalCase directories to lowercase for Linux compatibility, but the rename
# wasn't reflected on disk (macOS git silently ignores case-only renames).
# src/ui/app/index.ts imports from ./logo/ and ./loading/ (lowercase),
# but the actual directories are Logo/ and Loading/ (PascalCase).
RUN mv ./src/ui/app/Logo ./src/ui/app/logo && \
    mv ./src/ui/app/Loading ./src/ui/app/loading

# Apply CozyCognee patches: 使用补丁版本的 next.config.mjs 来禁用 devIndicators
# 同时通过 env 块将 NEXT_PUBLIC_* 变量传递给运行时（Next.js dev 模式支持）
COPY deployment/docker/cognee-frontend/patches/next.config.mjs ./next.config.mjs

COPY project/cognee/cognee-frontend/postcss.config.mjs .
COPY project/cognee/cognee-frontend/tsconfig.json .

# Build arguments for environment variables (NEXT_PUBLIC_*)
# 这些变量在运行时可用，Next.js dev 模式会实时读取进程环境变量
ARG NEXT_PUBLIC_BACKEND_API_URL=http://cognee:8000/api
ARG NEXT_PUBLIC_LOCAL_API_URL=http://cognee:8000
ARG NEXT_PUBLIC_CLOUD_API_URL=http://cognee-mcp:8000
ARG NEXT_PUBLIC_MCP_API_URL=http://cognee-mcp:8000
ARG NEXT_PUBLIC_COGWIT_API_KEY=
ARG NEXT_PUBLIC_IS_CLOUD_ENVIRONMENT=false
ARG NEXT_PUBLIC_DISABLE_CLOUD_CHECK=true

# Set environment variables (这些会在运行时可用)
ENV NEXT_PUBLIC_BACKEND_API_URL=${NEXT_PUBLIC_BACKEND_API_URL}
ENV NEXT_PUBLIC_LOCAL_API_URL=${NEXT_PUBLIC_LOCAL_API_URL}
ENV NEXT_PUBLIC_CLOUD_API_URL=${NEXT_PUBLIC_CLOUD_API_URL}
ENV NEXT_PUBLIC_MCP_API_URL=${NEXT_PUBLIC_MCP_API_URL}
ENV NEXT_PUBLIC_COGWIT_API_KEY=${NEXT_PUBLIC_COGWIT_API_KEY}
# IS_CLOUD_ENVIRONMENT=false → isCloudEnvironment() 返回 false，隐藏所有 cloud cognee UI
ENV NEXT_PUBLIC_IS_CLOUD_ENVIRONMENT=${NEXT_PUBLIC_IS_CLOUD_ENVIRONMENT}
ENV NEXT_PUBLIC_DISABLE_CLOUD_CHECK=${NEXT_PUBLIC_DISABLE_CLOUD_CHECK}

# Disable telemetry
ENV NEXT_TELEMETRY_DISABLED=1

# 禁用左下角开发工具指示器（通过 next.config.mjs 中的 devIndicators 配置）
ENV NEXT_DISABLE_DEV_INDICATORS=true

EXPOSE 3000

# Start the development server
CMD ["npm", "run", "dev"]
