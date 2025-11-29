# Use an official Node.js runtime as a parent image
FROM node:22-alpine

# Set the working directory to /app
WORKDIR /app

# Copy package.json and package-lock.json to the working directory
# 构建上下文是项目根目录，所以路径是 project/cognee/cognee-frontend/...
COPY project/cognee/cognee-frontend/package.json project/cognee/cognee-frontend/package-lock.json ./

# Install dependencies
RUN npm ci
RUN npm rebuild lightningcss

# Copy the rest of the application code to the working directory
COPY project/cognee/cognee-frontend/src ./src
COPY project/cognee/cognee-frontend/public ./public
# Apply CozyCognee patches: 使用补丁版本的 next.config.mjs 来禁用 devIndicators
COPY deployment/docker/cognee-frontend/patches/next.config.mjs ./next.config.mjs
COPY project/cognee/cognee-frontend/postcss.config.mjs .
COPY project/cognee/cognee-frontend/tsconfig.json .

# Build arguments for environment variables (NEXT_PUBLIC_*)
# 这些变量在运行时可用，Next.js 会在客户端使用它们
ARG NEXT_PUBLIC_BACKEND_API_URL=http://cognee:8000/api
ARG NEXT_PUBLIC_CLOUD_API_URL=http://cognee-mcp:8000
ARG NEXT_PUBLIC_MCP_API_URL=http://cognee-mcp:8000
ARG NEXT_PUBLIC_COGWIT_API_KEY=
ARG NEXT_PUBLIC_IS_CLOUD_ENVIRONMENT=false

# Set environment variables (这些会在运行时可用)
ENV NEXT_PUBLIC_BACKEND_API_URL=${NEXT_PUBLIC_BACKEND_API_URL}
ENV NEXT_PUBLIC_CLOUD_API_URL=${NEXT_PUBLIC_CLOUD_API_URL}
ENV NEXT_PUBLIC_MCP_API_URL=${NEXT_PUBLIC_MCP_API_URL}
ENV NEXT_PUBLIC_COGWIT_API_KEY=${NEXT_PUBLIC_COGWIT_API_KEY}
ENV NEXT_PUBLIC_IS_CLOUD_ENVIRONMENT=${NEXT_PUBLIC_IS_CLOUD_ENVIRONMENT}

# Disable telemetry
ENV NEXT_TELEMETRY_DISABLED=1

# CozyCognee: 禁用开发指示器（devIndicators）
# 设置此环境变量为 true 来隐藏左下角的开发工具指示器
# 默认禁用，如需启用可设置为 false 或不设置
ENV NEXT_DISABLE_DEV_INDICATORS=true

EXPOSE 3000

# Start the development server
CMD ["npm", "run", "dev"]

